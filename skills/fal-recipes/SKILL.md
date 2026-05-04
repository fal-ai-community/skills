---
name: fal-recipes
description: >
 Use-case-driven multi-step pipelines on fal.ai. Trigger when the user asks
 for a specific kind of content production rather than a single endpoint
 call: "make a commercial", "ad creative", "product photography", "cinematic
 shot", "film look", "character design", "consistent character", "anchor
 system", "storyboard", "multi-shot", "narrative video", "talking head",
 "lip sync", "make this person talk", "virtual try-on", "garment transfer",
 "restore image", "deblur", "denoise", "fix face", "old photo restore",
 "add audio to video", "video sound effects", "product shot",
 "photoreal", "realistic photo", "candid photo", "editorial portrait",
 "documentary photo", "looks like a real photograph", "iPhone-style photo",
 "film photo", "archival photo". Each recipe describes inputs, the genmedia
 call sequence, and quality checks.
---

# fal.ai Recipes

> **Runtime:** All endpoint calls run via the [genmedia CLI](https://github.com/fal-ai-community/genmedia-cli). See the `genmedia` skill for command syntax; run `genmedia init` once if not yet installed.

A recipe is a use-case-driven pipeline. It tells you the inputs to collect, the genmedia calls to chain, and the quality bar to verify before returning.

Recipes use `genmedia` for execution and `fal-models-catalog` for endpoint defaults. They differ from `fal-workflow`:

- **fal-workflow** = how to *build* a pipeline (JSON authoring or CLI orchestration patterns), generic
- **fal-recipes** = how to *produce a specific kind of content*, opinionated by use case

## Available recipes

| Reference | Use for |
|-----------|---------|
| [cinematography.md](references/cinematography.md) | Cinematic stills and video, shot language, lighting, lens, color grade |
| [character-design.md](references/character-design.md) | Original characters with consistent identity across shots |
| [commercial.md](references/commercial.md) | Product photography, ads, e-commerce batches, hero shots |
| [storytelling.md](references/storytelling.md) | Multi-shot narratives, short films, ads, brand films, social stories |
| [character-lipsync.md](references/character-lipsync.md) | Talking head / lip-sync video (TTS → animated portrait) |
| [image-restoration.md](references/image-restoration.md) | Smart-dispatch restoration, deblur, denoise, dehaze, fix faces, document restore |
| [virtual-tryon.md](references/virtual-tryon.md) | Apply a garment onto a person photo (with optional cleanup chain) |
| [video-with-audio.md](references/video-with-audio.md) | Add narration / SFX / music to a silent video |
| [product-shot.md](references/product-shot.md) | Hero product photography from a packshot reference |
| [realism.md](references/realism.md) | Photoreal stills (candid, editorial, documentary, archival, food, nature, architectural) with an anti-AI-look checklist |

## How to choose a recipe

1. Match the user's intent to a use case in the table above.
2. If multiple recipes apply (e.g., "commercial featuring a consistent character"), load both and run the dominant one, usually the more specific one (`character-design` first, then commercial framing).
3. If no recipe matches but the task is multi-step, fall back to `fal-workflow` Mode B (CLI orchestration) and design the pipeline from scratch.
4. If the task is a single endpoint call, skip recipes, go directly to the right `fal-models-catalog` reference.

## Universal recipe structure

Every reference follows the same skeleton so the agent knows where to look:

1. **Inputs to collect**: only what changes the pipeline.
2. **Genmedia workflow**: endpoint discovery, schema inspection, upload, run, status, download.
3. **Prompt build order**: domain-specific structure (e.g., SCLCAM for cinema, anchor + variable for character).
4. **Patterns / examples**: concrete prompt templates and finished examples.
5. **Quality bar**: explicit checks before returning.

## Cross-references

- For endpoint defaults: [fal-models-catalog](../fal-models-catalog/SKILL.md)
- For prompt-craft per model family: [fal-prompting](../fal-prompting/SKILL.md)
- For pipeline patterns (fan-out, sequential, frame-bridging, etc.): [fal-workflow](../fal-workflow/SKILL.md) Mode B
- For utility endpoints (resize, composite, audio merge, subtitle, etc.): [fal-workflow/references/utility-endpoints.md](../fal-workflow/references/utility-endpoints.md)

Information lives in one place. If a recipe needs an endpoint listed in the catalog, it links to the catalog instead of duplicating the list.
