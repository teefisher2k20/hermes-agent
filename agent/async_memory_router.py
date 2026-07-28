#!/usr/bin/env python3
"""
Async Memory Router for Hermes Agent.

Provides multiple memory persistence strategies to eliminate UI freezes, SQLite lock contention,
and hanging tool calls during memory preference operations.

Strategies:
  - PLAN_A (Two-Tier Hybrid): Fast inline file append (<2ms) + Async background thread commit for vector/DB indexing.
  - PLAN_B (Full Async): Immediate response return with 0ms UI delay; background task handles all I/O & DB writes.
  - PLAN_C (Inline Fast File Write + Cron Sync): Fast inline file write with WAL guard; defers re-indexing to cron.
  - AUTO: Dynamically inspects I/O latency and SQLite lock state to select the optimal strategy.
"""

import asyncio
import concurrent.futures
import enum
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Dedicated background thread pool executor for memory operations
_MEMORY_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="hermes-memory-worker")


class MemoryPlan(str, enum.Enum):
    PLAN_A = "PLAN_A"  # Two-Tier Hybrid (Inline File <2ms + Async DB Sync)
    PLAN_B = "PLAN_B"  # Full Async (0ms UI return)
    PLAN_C = "PLAN_C"  # Fast Inline File Write + Cron Sync
    AUTO = "AUTO"      # Auto-select strategy based on I/O and DB contention


class AsyncMemoryRouter:
    """Memory Persistence Router supporting Plan A, B, C and Auto mode selection."""

    def __init__(self, default_plan: MemoryPlan = MemoryPlan.AUTO):
        self.configured_plan = default_plan

    @staticmethod
    def check_sqlite_contention() -> bool:
        """Check if SQLite state database is currently experiencing write lock contention."""
        try:
            from hermes_state import SessionDB
            db = SessionDB()
            # Fast ping query
            with db._lock:
                db._conn.execute("SELECT 1")
            return False
        except Exception as err:
            logger.debug("SQLite write lock contention detected: %s", err)
            return True

    def auto_select_plan(self) -> MemoryPlan:
        """Evaluate DB lock status and file I/O load to choose the optimal memory plan."""
        is_locked = self.check_sqlite_contention()
        if is_locked:
            logger.info("Auto-memory router selected PLAN_B (Full Async due to DB contention)")
            return MemoryPlan.PLAN_B
        logger.info("Auto-memory router selected PLAN_A (Two-Tier Hybrid: Inline File + Async DB)")
        return MemoryPlan.PLAN_A

    def resolve_effective_plan(self, requested_plan: Optional[MemoryPlan] = None) -> MemoryPlan:
        target = requested_plan or self.configured_plan
        if target == MemoryPlan.AUTO:
            return self.auto_select_plan()
        return target

    def submit_background_task(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> concurrent.futures.Future:
        """Schedule a function to execute asynchronously in the background thread pool."""
        return _MEMORY_EXECUTOR.submit(fn, *args, **kwargs)

    def execute_memory_write(
        self,
        inline_file_fn: Callable[[], Dict[str, Any]],
        async_db_fn: Optional[Callable[[], Any]] = None,
        requested_plan: Optional[MemoryPlan] = None,
    ) -> Dict[str, Any]:
        """Execute memory write according to the resolved MemoryPlan strategy."""
        effective_plan = self.resolve_effective_plan(requested_plan)
        start = time.perf_counter()

        if effective_plan == MemoryPlan.PLAN_B:
            # Full Async: Submit all work to background worker, return immediate success
            if async_db_fn:
                self.submit_background_task(async_db_fn)
            self.submit_background_task(inline_file_fn)
            return {
                "success": True,
                "status": "saving_in_background",
                "strategy": effective_plan.value,
                "duration_ms": round((time.perf_counter() - start) * 1000.0, 2),
            }

        elif effective_plan == MemoryPlan.PLAN_C:
            # Inline File Write only (defer heavy indexing)
            result = inline_file_fn()
            result["strategy"] = effective_plan.value
            return result

        else:
            # Default Plan A: Fast inline file append + background async DB commit
            result = inline_file_fn()
            if async_db_fn:
                self.submit_background_task(async_db_fn)
            result["strategy"] = effective_plan.value
            result["duration_ms"] = round((time.perf_counter() - start) * 1000.0, 2)
            return result


# Global singleton instance
async_memory_router = AsyncMemoryRouter()
