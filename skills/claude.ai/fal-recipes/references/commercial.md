# Commercial Recipe

Use this recipe when the user wants advertising, product, brand, or e-commerce media. Keep the output production-focused. Do not add inflated marketing language, unsupported claims, fake text in the image, or em dashes.

## Inputs to collect

Only ask when the answer cannot be inferred from the task or the source files.

- Product: exact product name, category, material, color, scale, logo rules.
- Goal: hero shot, PDP image, ad creative, motion reveal, demo, UGC, lifestyle.
- Platform: square, vertical, landscape, banner, transparent background, print.
- Brand: premium, playful, clinical, athletic, minimal, natural, technical.
- Source media: product packshot, logo, reference scene, prior generated asset.
- Constraints: preserve packaging, avoid new labels, no fake readable copy.

## Genmedia workflow

1. Routed endpoints (see [fal-models-catalog](../../fal-models-catalog/SKILL.md)):

 ```bash
 genmedia models --endpoint_id openai/gpt-image-2 --json
 genmedia models --endpoint_id fal-ai/nano-banana-pro/edit --json
 genmedia models --endpoint_id fal-ai/nano-banana-2 --json
 genmedia models --endpoint_id bytedance/seedance-2.0/image-to-video --json
 ```

 Fallback discovery:

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

4. Still-image jobs synchronously when quick:

 ```bash
 genmedia run <endpoint_id> \
 --prompt "<commercial prompt>" \
 --image_url "<uploaded product url if supported>" \
 --download "./outputs/commercial/{request_id}_{index}.{ext}" \
 --json
 ```

5. Video jobs async, download from `status`:

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

6. Use schema fields exactly. Mirror the model's field names. `image_urls`, `reference_image_url`, `aspect_ratio`, `duration`, `seed`, etc.

## Prompt build order

1. **Product invariant**: exact object, material, color, packaging, scale.
2. **Commercial role**: hero image, PDP image, launch teaser, demo shot, social ad.
3. **Setting**: surface, background, props, environment, distance from product.
4. **Lighting**: softbox, strip light, rim light, backlight, caustics, practicals.
5. **Camera**: angle, focal length feel, macro, depth of field, motion if video.
6. **Composition**: centered, negative space, safe zone, text-free area, platform.
7. **Brand tone**: premium, clean, clinical, bold, energetic, warm, editorial.
8. **Guardrails**: preserve logo and packaging, no extra text, no distorted labels.

Do not promise claims like "best", "clinically proven", "50 percent faster", or celebrity endorsements unless the user provides that copy.

## Prompt patterns

### Product hero image

```text
[exact product] as the only hero object, [material and color], placed on
[surface], [background], [lighting setup], [camera angle and lens feel],
[composition and crop], premium commercial product photography, clean edges,
accurate packaging, no extra text, no fake labels, no hands unless requested
```

### Product with lifestyle context

```text
[exact product] used in [specific real setting], natural interaction with
[person or environment], product remains sharp and readable, [time of day],
[brand tone], [lens feel], [platform crop], no invented claims, no extra logos
```

### E-commerce PDP image

```text
[exact product] centered on seamless [background color], front-facing,
accurate silhouette, even softbox lighting, realistic shadow, high detail,
no props, no decorative text, clean product catalog photography
```

### Social ad with safe-zone composition

```text
[product] in [scene], subject placed in [left/right/lower third], large clean
negative space on [side] for copy, [platform aspect ratio], strong first-frame
readability, no text generated inside the image
```

### Product reveal video

```text
[duration] second product reveal of [product], starts with [opening frame],
camera [movement], product rotates or reveals [feature], [lighting change],
[background motion], premium commercial pacing, product remains centered and
undistorted, no text, no logo morphing
```

### Background replacement

```text
keep the uploaded product exactly unchanged, replace only the background with
[environment], match reflections and contact shadows, [lighting direction],
commercial product photography, no product deformation, no added labels
```

### Material cues

- **Glass**: backlight, rim light, caustics, transparent edges, controlled reflections.
- **Metal**: strip highlights, hard rim, dark flags, precise specular lines.
- **Plastic**: softbox, clean shadow, realistic molded edges, no over-gloss.
- **Fabric**: side light, visible weave, natural folds, accurate color.
- **Food**: soft directional light, steam or condensation only when plausible.
- **Jewelry**: macro lens feel, dark cards, crisp sparkle, controlled highlights.

### Negative prompt components

Use only when the selected model supports a negative prompt:

```text
extra text, fake logo, misspelled label, deformed packaging, duplicated
product, cropped product, warped geometry, bad reflections, messy background,
unreadable brand mark, synthetic hands, low resolution
```

## Workflows

### Hero image from product reference

1. Upload the product image with `genmedia upload`.
2. Search for image editing, reference image, or product photography models.
3. Inspect schema and choose fields that preserve product identity.
4. Prompt for surface, lighting, crop, and background. Keep the product invariant short and exact.
5. Run with `--download "./outputs/commercial/{request_id}_{index}.{ext}"`.
6. Reject outputs with altered logos, warped packaging, or invented text.

### Text-to-image product concept

Use when no reference exists or the user wants early creative exploration.

1. Ask or infer product category, materials, and brand tone.
2. Generate 2-4 controlled variants if the model supports count.
3. Keep each variant different by one dimension only: background, lighting, camera angle, or prop set.
4. Pick the strongest frame before moving to video or batch production.

### Product reveal video

1. Create a still hero frame or upload the user's approved product frame.
2. Search image-to-video models and inspect `duration`, `aspect_ratio`, image input, seed, and motion controls.
3. Keep motion simple: push-in, turntable, parallax, reveal, pour, unwrap.
4. Run async, then download from `genmedia status`.
5. If the product changes shape, reduce motion and strengthen identity constraints.

### E-commerce batch

1. Build a base prompt with exact product invariants.
2. Create a small matrix: white background, brand-color background, lifestyle, scale/detail, packaging close-up.
3. Use consistent output naming with `{request_id}_{index}`.
4. Return a table of output path, concept, endpoint, and notable defects.

### Ad creative set

Produce separate assets for:

- **Hook frame**: product and benefit visible in under one second.
- **Proof frame**: product detail, ingredient, feature, texture, or before-after.
- **Lifestyle frame**: human or environmental context.
- **Conversion frame**: clean safe-zone layout for external text and CTA.

Do not generate legal claims, pricing, discounts, or health claims unless the user supplies the exact copy.

## Examples

### Skincare serum hero

```text
amber glass skincare serum bottle with matte black dropper, exact label and
packaging preserved from the reference image, standing on pale stone, soft
diffused key light from upper left, thin rim light on glass edges, subtle
water condensation, warm beige background, centered square crop, premium beauty
product photography, no added text, no extra bottles, no warped label
```

### Sneaker launch still

```text
single white running sneaker with blue outsole accents, three-quarter side
view, suspended just above a clean concrete surface, sharp shadow under sole,
crisp studio flash, slight motion dust behind heel, athletic launch campaign
style, product fully visible, no brand changes, no text
```

### Beverage pour video

```text
8 second commercial video of a cold craft soda can on wet black stone,
opening on a close-up of condensation, slow push-in as liquid pours into a
glass beside it, controlled splash, amber backlight through the liquid, premium
beverage ad pacing, can shape and label remain stable, no added text
```

### SaaS device mockup

```text
thin laptop on a clean walnut desk showing an abstract dashboard interface,
morning side light, shallow depth of field, organized workspace with notebook
and pen, calm productivity mood, wide landscape crop with negative space on
right for headline, no readable fake UI text
```

### Background replacement

```text
preserve the uploaded ceramic coffee mug exactly, replace background with a
bright Scandinavian kitchen counter, soft morning window light from left,
realistic contact shadow and reflection, warm lifestyle product photography,
no new logo, no deformation, no text
```

## Quality bar

Before returning, check:

- Product shape, logo, material, and color are not invented or distorted.
- The composition leaves enough room for platform crop and optional copy.
- Background props support the product and do not compete with it.
- Any generated text is absent or intentionally controlled.
- Lighting makes sense for the product material.
- Output paths come from `downloaded_files[]`, not manually curled URLs.

If the result misses product fidelity, switch from text-only generation to a reference or edit workflow before retrying.
