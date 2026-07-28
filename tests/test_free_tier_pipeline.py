#!/usr/bin/env python3
"""Tests for FreeTierModelPipeline module."""

import pytest
from unittest.mock import MagicMock, patch
from agent.free_tier_pipeline import FreeTierModelPipeline, free_tier_pipeline


def test_free_tier_status_probes():
    pipeline = FreeTierModelPipeline()
    top_ok, top_desc = pipeline.check_top_model_status()
    assert top_ok is True
    assert "D:\\Top-Model" in top_desc


def test_free_tier_primary_success():
    pipeline = FreeTierModelPipeline()
    mock_primary = MagicMock(return_value="primary_response")
    res = pipeline.generate_response(prompt="Hello", primary_func=mock_primary)
    assert res["success"] is True
    assert res["provider"] == "primary_cloud"
    assert res["response"] == "primary_response"


def test_free_tier_intercepts_billing_error():
    pipeline = FreeTierModelPipeline()

    def failing_primary(prompt):
        raise Exception("402 Insufficient Quota / Payment Required")

    with patch.object(pipeline, "check_ollama_status", return_value=(False, "")):
        with patch.object(pipeline, "check_top_model_status", return_value=(False, "")):
            res = pipeline.generate_response(prompt="Test prompt", primary_func=failing_primary)
            assert res["success"] is True
            assert res["provider"] == "free_tier_fallback"
            assert "Hermes Free-Tier Pipeline" in res["response"]
