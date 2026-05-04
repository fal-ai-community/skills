# Commercial workflows

## Hero image from product reference

1. Upload the product image with `genmedia upload`.
2. Search for image editing, reference image, or product photography models.
3. Inspect schema and choose the fields that preserve product identity.
4. Prompt for surface, lighting, crop, and background. Keep the product
   invariant short and exact.
5. Run with `--download "./outputs/commercial/{request_id}_{index}.{ext}"`.
6. Reject outputs with altered logos, warped packaging, or invented text.

## Text-to-image product concept

Use when no reference exists or the user wants early creative exploration.

1. Ask or infer product category, materials, and brand tone.
2. Generate 2 to 4 controlled variants if the model supports count.
3. Keep each variant different by one dimension only: background, lighting,
   camera angle, or prop set.
4. Pick the strongest frame before moving to video or batch production.

## Product reveal video

1. Create a still hero frame or upload the user's approved product frame.
2. Search image-to-video models and inspect `duration`, `aspect_ratio`, image
   input, seed, and motion controls.
3. Keep motion simple: push-in, turntable, parallax, reveal, pour, unwrap.
4. Run async, then download from `genmedia status`.
5. If the product changes shape, reduce motion and strengthen identity
   constraints.

## E-commerce batch

1. Build a base prompt with exact product invariants.
2. Create a small matrix: white background, brand-color background, lifestyle,
   scale/detail, packaging close-up.
3. Use consistent output naming with `{request_id}_{index}`.
4. Return a table of output path, concept, endpoint, and notable defects.

## Ad creative set

Produce separate assets for:

- Hook frame: product and benefit visible in under one second.
- Proof frame: product detail, ingredient, feature, texture, or before-after.
- Lifestyle frame: human or environmental context.
- Conversion frame: clean safe-zone layout for external text and CTA.

Do not generate legal claims, pricing, discounts, or health claims unless the
user supplies the exact copy.
