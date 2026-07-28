#!/usr/bin/env python3
"""
Smart Fallback Model Router for Hermes Agent.

Provides multi-tier model fallback routing strategies and automatic health-probing
to prevent hangs, timeouts, and quota errors during LLM inference.

Strategies:
  - PLAN_A (Multi-Tier Hybrid): Primary Cloud -> Ollama (127.0.0.1:11434) -> D:\\Top-Model\\model_fallback.py
  - PLAN_B (Ollama-First): Primary Cloud -> Ollama
  - PLAN_C (In-Process D:\\Top-Model): Primary Cloud -> D:\\Top-Model\\model_fallback.py
  - AUTO: Automatically probes health and latency of Ollama and D:\\Top-Model to pick the best operational strategy.
"""

import enum
import logging
import os
import sys
import time
import urllib.request
import urllib.error
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

OLLAMA_DEFAULT_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434/v1")
OLLAMA_TAGS_URL = os.getenv("OLLAMA_TAGS_URL", "http://127.0.0.1:11434/api/tags")
TOP_MODEL_DIR = os.getenv("TOP_MODEL_DIR", r"D:\Top-Model")


class FallbackPlan(str, enum.Enum):
    PLAN_A = "PLAN_A"  # Cloud -> Ollama -> D:\Top-Model
    PLAN_B = "PLAN_B"  # Cloud -> Ollama
    PLAN_C = "PLAN_C"  # Cloud -> D:\Top-Model
    AUTO = "AUTO"      # Auto-select best strategy based on health probes


class SmartFallbackRouter:
    """Intelligent Model Router with health checks and tier-based failover."""

    def __init__(self, default_plan: FallbackPlan = FallbackPlan.AUTO):
        self.configured_plan = default_plan

    @staticmethod
    def check_ollama_health(timeout: float = 1.5) -> Tuple[bool, float]:
        """Probe Ollama endpoint for availability and latency.

        Returns (is_available, latency_ms).
        """
        start = time.perf_counter()
        try:
            req = urllib.request.Request(OLLAMA_TAGS_URL, headers={"User-Agent": "Hermes-SmartRouter"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    latency = (time.perf_counter() - start) * 1000.0
                    return True, round(latency, 2)
        except Exception as err:
            logger.debug("Ollama health check failed: %s", err)
        return False, -1.0

    @staticmethod
    def check_top_model_health() -> Tuple[bool, str]:
        """Check if local D:\\Top-Model fallback pipeline is accessible."""
        fallback_script = os.path.join(TOP_MODEL_DIR, "model_fallback.py")
        if os.path.exists(fallback_script):
            return True, fallback_script
        return False, ""

    def auto_select_plan(self) -> FallbackPlan:
        """Dynamically evaluate environment health and pick the best plan."""
        ollama_ok, latency = self.check_ollama_health()
        top_model_ok, _ = self.check_top_model_health()

        if ollama_ok and top_model_ok:
            logger.info("Auto-router selected PLAN_A (Hybrid: Cloud -> Ollama [latency=%.1fms] -> Top-Model)", latency)
            return FallbackPlan.PLAN_A
        elif ollama_ok:
            logger.info("Auto-router selected PLAN_B (Ollama available [latency=%.1fms])", latency)
            return FallbackPlan.PLAN_B
        elif top_model_ok:
            logger.info("Auto-router selected PLAN_C (Direct Top-Model fallback)")
            return FallbackPlan.PLAN_C
        else:
            logger.info("Auto-router default fallback to PLAN_A")
            return FallbackPlan.PLAN_A

    def resolve_effective_plan(self, requested_plan: Optional[FallbackPlan] = None) -> FallbackPlan:
        """Resolve requested plan or AUTO to an operational plan."""
        target = requested_plan or self.configured_plan
        if target == FallbackPlan.AUTO:
            return self.auto_select_plan()
        return target

    def _execute_ollama_fallback(self, prompt: str, model: str = "qwen2.5-coder:7b") -> Optional[str]:
        """Execute request against local Ollama OpenAI-compatible endpoint."""
        try:
            import json
            url = f"{OLLAMA_DEFAULT_URL.rstrip('/')}/chat/completions"
            payload = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            }).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "Hermes-SmartRouter"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                logger.info("Successfully received response from Ollama fallback (%s)", model)
                return content
        except Exception as exc:
            logger.warning("Ollama fallback execution failed: %s", exc)
            return None

    def _execute_top_model_fallback(self, prompt: str, fallback_key: str = "qwen0.8b") -> Optional[str]:
        """Execute request using local D:\\Top-Model Hugging Face pipeline."""
        top_model_ok, script_path = self.check_top_model_health()
        if not top_model_ok:
            return None
        try:
            if TOP_MODEL_DIR not in sys.path:
                sys.path.insert(0, TOP_MODEL_DIR)
            import model_fallback
            result = model_fallback.smart_generate(prompt, primary_func=None, fallback_model_key=fallback_key)
            logger.info("Successfully received response from D:\\Top-Model fallback")
            return str(result)
        except Exception as exc:
            logger.warning("D:\\Top-Model fallback execution failed: %s", exc)
            return None

    def execute_with_fallback(
        self,
        primary_func: Callable[[], Any],
        prompt: str = "",
        requested_plan: Optional[FallbackPlan] = None,
        fallback_key: str = "qwen0.8b",
    ) -> Any:
        """Execute primary API function with automatic multi-tier fallback routing on failure."""
        effective_plan = self.resolve_effective_plan(requested_plan)
        try:
            return primary_func()
        except Exception as err:
            err_msg = str(err).lower()
            logger.warning("Primary API call failed (%s). Triggering fallback plan: %s", err, effective_plan.value)

            if effective_plan in (FallbackPlan.PLAN_A, FallbackPlan.PLAN_B):
                ollama_res = self._execute_ollama_fallback(prompt)
                if ollama_res:
                    return ollama_res

            if effective_plan in (FallbackPlan.PLAN_A, FallbackPlan.PLAN_C):
                top_model_res = self._execute_top_model_fallback(prompt, fallback_key=fallback_key)
                if top_model_res:
                    return top_model_res

            # Re-raise primary error if all fallbacks fail
            raise err


# Global singleton instance
smart_router = SmartFallbackRouter()
