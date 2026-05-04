---
name: commercial
description: >
  Plan and run commercial image or video production with genmedia. Use this
  for product photography, ads, e-commerce batches, product reveals, lifestyle
  commercials, background replacement, social formats, and brand-safe prompt
  work.
---

# Commercial production with genmedia

Use this skill when the user wants advertising, product, brand, or e-commerce
media. Load the reference files when you need prompt patterns or category
examples:

- `references/prompt-patterns.md`
- `references/workflows.md`
- `references/examples.md`

Load `model-routing` alongside this skill for default endpoint choices.

Keep the output production-focused. Do not add inflated marketing language,
unsupported claims, fake text in the image, or em dashes.

## Inputs to collect

Only ask when the answer cannot be inferred from the task or the source files.

- Product: exact product name, category, material, color, scale, logo rules.
- Goal: hero shot, PDP image, ad creative, motion reveal, demo, UGC, lifestyle.
- Platform: square, vertical, landscape, banner, transparent background, print.
- Brand: premium, playful, clinical, athletic, minimal, natural, technical.
- Source media: product packshot, logo, reference scene, prior generated asset.
- Constraints: preserve packaging, avoid new labels, no fake readable copy.
- Model preference: use `model-routing` defaults unless the user names a model
  or the job is unusually expensive.

## Genmedia workflow

1. Start from routed endpoint IDs.

   ```bash
   genmedia models --endpoint_id openai/gpt-image-2 --json
   genmedia models --endpoint_id fal-ai/nano-banana-pro/edit --json
   genmedia models --endpoint_id fal-ai/nano-banana-2 --json
   genmedia models --endpoint_id bytedance/seedance-2.0/image-to-video --json
   ```

   Use text search only as fallback discovery for a missing utility or
   unsupported role:

   ```bash
   genmedia models "background removal product image" --json
   genmedia docs "commercial product image generation" --json
   ```

2. Inspect the selected endpoint before running.

   ```bash
   genmedia schema <endpoint_id> --json
   genmedia pricing <endpoint_id> --json
   ```

3. Upload every local or remote reference file.

   ```bash
   genmedia upload ./product.png --json
   genmedia upload ./logo.png --json
   ```

4. Run still-image jobs synchronously when they are quick.

   ```bash
   genmedia run <endpoint_id> \
     --prompt "<commercial prompt>" \
     --image_url "<uploaded product url if supported>" \
     --download "./outputs/commercial/{request_id}_{index}.{ext}" \
     --json
   ```

5. Run video jobs async and download from `status`.

   ```bash
   genmedia run <endpoint_id> \
     --prompt "<motion prompt>" \
     --image_url "<uploaded hero frame if supported>" \
     --async \
     --json

   genmedia status <endpoint_id> <request_id> \
     --download "./outputs/commercial/{request_id}_{index}.{ext}" \
     --json
   ```

6. Use schema fields exactly. Do not pass guessed flags. If the model uses
   `image_urls`, `reference_image_url`, `aspect_ratio`, `duration`, `seed`, or
   another name, mirror that schema.

## Prompt build order

Write prompts in this order so commercial intent stays clear:

1. Product invariant: exact object, material, color, packaging, scale.
2. Commercial role: hero image, PDP image, launch teaser, demo shot, social ad.
3. Setting: surface, background, props, environment, distance from product.
4. Lighting: softbox, strip light, rim light, backlight, caustics, practicals.
5. Camera: angle, focal length feel, macro, depth of field, motion if video.
6. Composition: centered, negative space, safe zone, text-free area, platform.
7. Brand tone: premium, clean, clinical, bold, energetic, warm, editorial.
8. Guardrails: preserve logo and packaging, no extra text, no distorted labels.

Do not promise claims like "best", "clinically proven", "50 percent faster",
or celebrity endorsements unless the user provides that copy.

## Model routing

- Text-heavy ads, labels, posters, UI mockups, packaging copy, and
  infographics: use `openai/gpt-image-2` at `quality=high`. Prefer 2K or 4K
  when the final must carry small readable details. Treat this as expensive.
- Premium realistic stills: use `openai/gpt-image-2`.
- Premium stylized stills: use `openai/gpt-image-2`, then
  `fal-ai/nano-banana-pro`, then `fal-ai/nano-banana-2`.
- Fast draft stills: use `fal-ai/flux-2/klein/9b`.
- Image edits: use `fal-ai/nano-banana-pro/edit`, then
  `openai/gpt-image-2/edit`, then `fal-ai/bytedance/seedream/v5/lite/edit`.
- Product fidelity: use `fal-ai/nano-banana-pro`, `fal-ai/nano-banana-2`, or
  `fal-ai/bytedance/seedream/v5/lite/text-to-image`; use the matching edit
  endpoint when a product reference image exists.
- Product reveal video: create or upload a strong hero frame, then use
  `bytedance/seedance-2.0/image-to-video` for final quality.
- Fast or lower-cost video draft: use `xai/grok-imagine-video/image-to-video`
  or `xai/grok-imagine-video/text-to-video`.
- E-commerce batch: keep the same prompt skeleton and vary only background,
  crop, lighting, or platform format.
- Text overlays: generate with empty safe space. Add final text in a design or
  editing tool unless the selected model is explicitly good at typography.
- Background removal or cleanup: search for background removal, segmentation,
  inpainting, or product editing models and inspect their schemas.
- Final delivery: use `--download` with `{request_id}` and `{index}`.

## Quality bar

Before returning, check:

- Product shape, logo, material, and color are not invented or distorted.
- The composition leaves enough room for platform crop and optional copy.
- Background props support the product and do not compete with it.
- Any generated text is absent or intentionally controlled.
- Lighting makes sense for the product material.
- Output paths are from `downloaded_files[]`, not manually curled URLs.

If the result misses product fidelity, switch from text-only generation to a
reference or edit workflow before retrying.
