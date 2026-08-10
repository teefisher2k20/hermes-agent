# Design View Architecture Specification & Source Reference

## Overview
Design View is an integrated multi-step visual editing feature within the Hermes Agent platform. It transforms single-prompt image generation into an iterative, precise design workflow using inpainting, text extraction/editing, reference image guidance, and mobile batch instructions.

---

## Key Components & Workflow

### 1. Initial Concept Generation
- Prompt intake: Translates descriptive text into base visual scenes (e.g. Japandi living room, modern UI poster).
- Provider routing: Dispatches to photorealistic base generation models.

### 2. Mark Tool (Localized Inpainting & Editing)
- Target selection: Enables region masking on existing images.
- Precise instruction payload: E.g., "Change sofa to muted sage green", "Replace plant with wildflower arrangement".
- Reference image guidance: Merges uploaded element assets (e.g., custom lamp photo) into the target region.

### 3. Text Element Extraction & Editing
- OCR & Inpainting pipeline: Detects text overlays on generated posters/infographics.
- Preserves composition, background lighting, and typography style while updating strings.

### 4. Mobile & Batch Editing
- Touch-and-hold region selection.
- Multi-mark batch payload processing in a single inference call.

---

## Free-Tier Model Routing Strategy

The free tier router dynamically selects the optimal model per task without relying on Nano Banana:

| Task Type | Primary Free Provider | Alternate Free Fallback | Key Selection Criteria |
| :--- | :--- | :--- | :--- |
| **Photorealism / Base Gen** | `FLUX.1-schnell` (Pollinations / HF) | `SDXL Turbo` (HuggingFace API) | High prompt adherence & lighting realism |
| **Inpainting / Mark Tool** | `SDXL Inpaint` (Stability Free) | `FLUX Inpaint` (HF Inference) | Edge-aware masked inpainting |
| **Typography / Text Editing** | `Ideogram V2` / `FLUX.1-dev` | `SD3 Medium` (HF Free) | High typographic accuracy |
| **Mobile Fast Batch** | `Pollinations Fast` | `HuggingFace Inference` | Low latency & high throughput |

---

## Status & Maintenance Tracking
> [!NOTE]
> This specification is maintained as part of the `plugins/image_gen` system and flagged for continuous updates as new free-tier provider endpoints become available.
