"""
Free-Tier Smart Image Model Router for Design View & Image Generation.

Dynamically selects the optimal free provider model based on the target task
(base generation, inpainting/mark tool, text/typography editing, or fast mobile batching).
Excludes Nano Banana/Gemini Nano per system design requirements.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

_log = logging.getLogger(__name__)

# Task categories supported by Design View
TASK_BASE_GEN = "base_gen"
TASK_INPAINT = "inpaint"
TASK_TEXT_EDIT = "text_edit"
TASK_FAST_BATCH = "fast_batch"

# Excluded models per explicit system rules
EXCLUDED_MODELS = {"nano_banana", "gemini_nano", "nano-banana-pro"}


@dataclass
class FreeModelEndpoint:
    name: str
    provider: str
    task_specialty: str
    base_url: str
    free_tier: bool = True
    requires_key: bool = False


# Catalog of supported free-tier image models across companies
FREE_MODEL_CATALOG: Dict[str, List[FreeModelEndpoint]] = {
    TASK_BASE_GEN: [
        FreeModelEndpoint(
            name="flux-1-schnell",
            provider="pollinations",
            task_specialty="Photorealistic base generation & prompt fidelity",
            base_url="https://image.pollinations.ai/prompt/{prompt}",
            requires_key=False,
        ),
        FreeModelEndpoint(
            name="stabilityai/stable-diffusion-xl-base-1.0",
            provider="huggingface",
            task_specialty="High-resolution composition & lighting",
            base_url="https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            requires_key=True,
        ),
    ],
    TASK_INPAINT: [
        FreeModelEndpoint(
            name="stabilityai/stable-diffusion-xl-refiner-1.0",
            provider="huggingface",
            task_specialty="Mark Tool localized region inpainting",
            base_url="https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-refiner-1.0",
            requires_key=True,
        ),
        FreeModelEndpoint(
            name="sdxl-inpaint-pollinations",
            provider="pollinations",
            task_specialty="Free keyless localized region editing",
            base_url="https://image.pollinations.ai/prompt/{prompt}?model=flux-realism",
            requires_key=False,
        ),
    ],
    TASK_TEXT_EDIT: [
        FreeModelEndpoint(
            name="black-forest-labs/FLUX.1-dev",
            provider="huggingface",
            task_specialty="Typography & poster text rendering",
            base_url="https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev",
            requires_key=True,
        ),
        FreeModelEndpoint(
            name="ideogram-free-proxy",
            provider="pollinations",
            task_specialty="Poster & infographic text element editing",
            base_url="https://image.pollinations.ai/prompt/{prompt}?model=flux-pro",
            requires_key=False,
        ),
    ],
    TASK_FAST_BATCH: [
        FreeModelEndpoint(
            name="flux-schnell-fast",
            provider="pollinations",
            task_specialty="Mobile batch processing & rapid iteration",
            base_url="https://image.pollinations.ai/prompt/{prompt}?model=turbo",
            requires_key=False,
        ),
    ],
}


def select_best_free_model(task_type: str = TASK_BASE_GEN, *, prefer_keyless: bool = False) -> Dict[str, Any]:
    """Select the optimal free-tier image model for the given Design View task.

    Args:
        task_type: One of 'base_gen', 'inpaint', 'text_edit', 'fast_batch'.
        prefer_keyless: If True, prioritizes zero-key endpoints (e.g. Pollinations).

    Returns:
        Dict describing the selected model, provider, base URL, and capabilities.
    """
    category = FREE_MODEL_CATALOG.get(task_type, FREE_MODEL_CATALOG[TASK_BASE_GEN])
    
    # Filter out any explicitly excluded models
    valid_candidates = [m for m in category if m.name.lower() not in EXCLUDED_MODELS]
    
    if not valid_candidates:
        valid_candidates = category

    if prefer_keyless:
        keyless = [m for m in valid_candidates if not m.requires_key]
        if keyless:
            selected = keyless[0]
        else:
            selected = valid_candidates[0]
    else:
        selected = valid_candidates[0]

    _log.info("Design View Router selected free model '%s' via '%s' for task '%s'", selected.name, selected.provider, task_type)

    return {
        "status": "selected",
        "task_type": task_type,
        "model_name": selected.name,
        "provider": selected.provider,
        "specialty": selected.task_specialty,
        "base_url": selected.base_url,
        "requires_key": selected.requires_key,
        "excluded_models_enforced": list(EXCLUDED_MODELS),
    }


def list_available_free_tier_models() -> Dict[str, List[Dict[str, Any]]]:
    """Return all cataloged free tier models grouped by task specialty."""
    catalog_summary: Dict[str, List[Dict[str, Any]]] = {}
    for category, models in FREE_MODEL_CATALOG.items():
        catalog_summary[category] = [
            {
                "name": m.name,
                "provider": m.provider,
                "specialty": m.task_specialty,
                "requires_key": m.requires_key,
            }
            for m in models
            if m.name.lower() not in EXCLUDED_MODELS
        ]
    return catalog_summary
