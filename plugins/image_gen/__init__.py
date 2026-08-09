"""
Image Generation plugin module.

Exposes provider registries, Design View specifications, and the Free-Tier
Smart Image Model Router for dynamic task-based model selection.
"""

from __future__ import annotations

from plugins.image_gen.free_tier_router import (
    select_best_free_model,
    list_available_free_tier_models,
    TASK_BASE_GEN,
    TASK_INPAINT,
    TASK_TEXT_EDIT,
    TASK_FAST_BATCH,
)

__all__ = [
    "select_best_free_model",
    "list_available_free_tier_models",
    "TASK_BASE_GEN",
    "TASK_INPAINT",
    "TASK_TEXT_EDIT",
    "TASK_FAST_BATCH",
]
