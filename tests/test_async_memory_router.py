#!/usr/bin/env python3
"""Tests for AsyncMemoryRouter module."""

import pytest
from unittest.mock import MagicMock, patch
from agent.async_memory_router import AsyncMemoryRouter, MemoryPlan, async_memory_router


def test_memory_plan_enum_values():
    assert MemoryPlan.PLAN_A == "PLAN_A"
    assert MemoryPlan.PLAN_B == "PLAN_B"
    assert MemoryPlan.PLAN_C == "PLAN_C"
    assert MemoryPlan.AUTO == "AUTO"


def test_resolve_effective_plan():
    router = AsyncMemoryRouter(default_plan=MemoryPlan.PLAN_A)
    assert router.resolve_effective_plan() == MemoryPlan.PLAN_A
    assert router.resolve_effective_plan(MemoryPlan.PLAN_C) == MemoryPlan.PLAN_C


def test_plan_a_two_tier_execution():
    router = AsyncMemoryRouter()
    mock_file = MagicMock(return_value={"success": True})
    mock_db = MagicMock()

    res = router.execute_memory_write(inline_file_fn=mock_file, async_db_fn=mock_db, requested_plan=MemoryPlan.PLAN_A)
    assert res["success"] is True
    assert res["strategy"] == "PLAN_A"
    mock_file.assert_called_once()


def test_plan_b_full_async_execution():
    router = AsyncMemoryRouter()
    mock_file = MagicMock(return_value={"success": True})
    mock_db = MagicMock()

    res = router.execute_memory_write(inline_file_fn=mock_file, async_db_fn=mock_db, requested_plan=MemoryPlan.PLAN_B)
    assert res["success"] is True
    assert res["status"] == "saving_in_background"
    assert res["strategy"] == "PLAN_B"


def test_auto_plan_selection():
    router = AsyncMemoryRouter()
    with patch.object(AsyncMemoryRouter, "check_sqlite_contention", return_value=False):
        assert router.auto_select_plan() == MemoryPlan.PLAN_A

    with patch.object(AsyncMemoryRouter, "check_sqlite_contention", return_value=True):
        assert router.auto_select_plan() == MemoryPlan.PLAN_B
