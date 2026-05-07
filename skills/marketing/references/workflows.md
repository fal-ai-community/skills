# Marketing workflows

## Campaign asset set

1. Write a one-paragraph brief.
2. Build an asset matrix with role, channel, crop, endpoint, source media, and
   variation axis.
3. Generate the minimum complete set: hook, proof, context, conversion.
4. Inspect outputs before expanding variants.
5. Return a manifest with local paths and defects.

## Launch kit

Use when the user needs broad go-to-market visuals.

1. Create one hero still.
2. Create one product or feature detail.
3. Create one social hook video or motion reveal.
4. Create one clean conversion/end frame.
5. Optional: create one UGC creator variant through the `ugc` skill.

## Paid social variant test

1. Keep product, offer, and crop constant.
2. Generate 3-5 variants that differ by hook angle only.
3. Use exact output naming with `{request_id}_{index}`.
4. Score each output for thumb-stop, product clarity, claim safety, and crop.
5. Do not mix model changes and concept changes in the same test unless the
   user specifically wants a model shootout.

## Landing-page visual system

1. Define hero, proof, feature, and conversion sections.
2. Generate visuals with consistent palette, lighting, and product treatment.
3. Leave text and UI copy for the frontend unless the model is explicitly
   selected for text rendering.
4. Return assets in page order.

## Creator ad package

1. Use `ugc` for the talking-head or faceless creator asset.
2. Use this skill for campaign framing, channel matrix, hook variants, and
   conversion/end frames.
3. Keep the same proof and offer across creator variants.
4. Return creator clips and supporting marketing assets together.
