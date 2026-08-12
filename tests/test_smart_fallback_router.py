#!/usr/bin/env python3
"""Tests for SmartFallbackRouter module."""

import pytest
from unittest.mock import MagicMock, patch
from agent.smart_fallback_router import FallbackPlan, SmartFallbackRouter, smart_router


def test_fallback_plan_enum_values():
    assert FallbackPlan.PLAN_A == "PLAN_A"
    assert FallbackPlan.PLAN_B == "PLAN_B"
    assert FallbackPlan.PLAN_C == "PLAN_C"
    assert FallbackPlan.AUTO == "AUTO"


def test_resolve_effective_plan():
    router = SmartFallbackRouter(default_plan=FallbackPlan.PLAN_B)
    assert router.resolve_effective_plan() == FallbackPlan.PLAN_B
    assert router.resolve_effective_plan(FallbackPlan.PLAN_C) == FallbackPlan.PLAN_C


def test_auto_plan_selection_with_mocked_health():
    router = SmartFallbackRouter()
    with patch.object(SmartFallbackRouter, "check_ollama_health", return_value=(True, 12.5)):
        with patch.object(SmartFallbackRouter, "check_top_model_health", return_value=(True, "d:\\path")):
            assert router.auto_select_plan() == FallbackPlan.PLAN_A

    with patch.object(SmartFallbackRouter, "check_ollama_health", return_value=(True, 15.0)):
        with patch.object(SmartFallbackRouter, "check_top_model_health", return_value=(False, "")):
            assert router.auto_select_plan() == FallbackPlan.PLAN_B

    with patch.object(SmartFallbackRouter, "check_ollama_health", return_value=(False, -1.0)):
        with patch.object(SmartFallbackRouter, "check_top_model_health", return_value=(True, "d:\\path")):
            assert router.auto_select_plan() == FallbackPlan.PLAN_C


def test_execute_with_fallback_success():
    router = SmartFallbackRouter()
    mock_primary = MagicMock(return_value="primary_result")
    result = router.execute_with_fallback(primary_func=mock_primary, prompt="hello", requested_plan=FallbackPlan.PLAN_A)
    assert result == "primary_result"
    mock_primary.assert_called_once()


def test_execute_with_fallback_triggers_ollama():
    router = SmartFallbackRouter()
    def failing_primary():
        raise Exception("402 Payment Required")

    with patch.object(router, "_execute_ollama_fallback", return_value="ollama_fallback_result") as mock_ollama:
        result = router.execute_with_fallback(primary_func=failing_primary, prompt="hello", requested_plan=FallbackPlan.PLAN_B)
        assert result == "ollama_fallback_result"
        mock_ollama.assert_called_once_with("hello")
