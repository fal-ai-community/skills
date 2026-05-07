---
name: marketing
description: >
  Plan and run campaign-level marketing asset production with genmedia. Use
  this for launch kits, campaign matrices, paid social variants, landing-page
  visuals, email and banner imagery, hook/proof/conversion assets, creator ad
  packages, and channel-specific marketing deliverables.
---

# Marketing production with genmedia

Use this skill when the user wants a campaign system, not one isolated asset.
Load references as needed:

- `references/campaign-patterns.md`
- `references/workflows.md`
- `references/examples.md`

Load `model-routing` alongside this skill for default endpoint choices.

Marketing output should be executable: a brief, asset matrix, genmedia command
plan, downloaded files, and clear defects. Do not add fake claims, fake social
proof, fake partner logos, fake award badges, or invented legal copy.

## Inputs to collect

Only ask when missing details would change the asset plan.

- Objective: launch, acquisition, retargeting, activation, education, event.
- Audience: persona, market, use case, awareness level, objections.
- Offer: product, feature, bundle, trial, waitlist, event, promotion.
- Channels: paid social, organic social, landing page, email, display, app.
- Required assets: stills, video, thumbnails, hero image, carousel, banner.
- Brand rules: colors, logo use, typography, tone, taboo visuals, competitors.
- Source media: product images, screenshots, app UI, people, logo, prior ads.
- Claims: exact approved copy, proof points, disclaimers, compliance limits.
- Budget preference: final-quality, draft exploration, or mixed pipeline.

## Genmedia workflow

1. Start from routed endpoint IDs.

   ```bash
   genmedia models --endpoint_id openai/gpt-image-2 --json
   genmedia models --endpoint_id fal-ai/nano-banana-pro/edit --json
   genmedia models --endpoint_id fal-ai/nano-banana-2 --json
   genmedia models --endpoint_id bytedance/seedance-2.0/image-to-video --json
   genmedia models --endpoint_id bytedance/seedance-2.0/text-to-video --json
   genmedia models --endpoint_id veed/fabric-1.0 --json
   ```

   Use text search only as fallback discovery for a missing channel role:

   ```bash
   genmedia models "marketing banner image typography" --json
   genmedia models "social ad video product campaign" --json
   genmedia docs "image generation text rendering" --json
   ```

2. Inspect the selected endpoint before planning exact payloads.

   ```bash
   genmedia schema <endpoint_id> --json
   genmedia pricing <endpoint_id> --json
   ```

3. Upload all source media.

   ```bash
   genmedia upload ./product.png --json
   genmedia upload ./logo.svg --json
   genmedia upload ./screenshot.png --json
   genmedia upload ./creator.jpg --json
   ```

4. Build the campaign matrix before generating.

   Minimum matrix:

   - Hook asset: earns attention in the first frame.
   - Proof asset: shows product, result, process, feature, or evidence.
   - Context asset: places product in audience use case.
   - Conversion asset: clean end frame with safe space for external copy.

5. Run still assets synchronously when quick.

   ```bash
   genmedia run <endpoint_id> \
     --prompt "<marketing asset prompt>" \
     --download "./outputs/marketing/{request_id}_{index}.{ext}" \
     --json
   ```

6. Run video assets async and download from status.

   ```bash
   genmedia run <endpoint_id> \
     --prompt "<campaign video prompt>" \
     --async \
     --json

   genmedia status <endpoint_id> <request_id> \
     --download "./outputs/marketing/{request_id}_{index}.{ext}" \
     --json
   ```

7. Use schema fields exactly. Do not pass guessed flags. Mirror names such as
   `image_urls`, `image_url`, `reference_image_url`, `aspect_ratio`,
   `duration`, `quality`, `seed`, `prompt`, or `negative_prompt`.

## Brief build order

Build the campaign brief before prompts:

1. Product truth: what the product is and what must stay accurate.
2. Audience tension: problem, desire, objection, or trigger moment.
3. Campaign promise: user-approved benefit or visible outcome.
4. Asset roles: hook, proof, context, conversion, retention, reminder.
5. Channel specs: crop, runtime, safe zones, text needs, file count.
6. Variation axis: audience, setting, proof point, visual metaphor, offer.
7. Guardrails: claims, logo, legal, copy, product fidelity, banned imagery.

## Prompt build order

Write every asset prompt in this order:

1. Asset role and channel: launch hero, Meta ad, TikTok hook, email header.
2. Product or subject invariant: exact product, UI, feature, person, logo rule.
3. Audience context: where, who, problem state, usage moment.
4. Visual system: camera, lighting, color, composition, texture, motion.
5. Copy handling: no generated text, safe space, or exact provided wording.
6. Variant axis: what differs from the other assets.
7. Guardrails: no fake claims, no extra logos, no distorted product or UI.

## Model routing

- Text-heavy campaign key art, posters, landing heroes, app/UI visuals, and
  ads with exact copy: `openai/gpt-image-2` at `quality=high`.
- Premium product or brand stills: `openai/gpt-image-2`, then
  `fal-ai/nano-banana-pro`, then `fal-ai/nano-banana-2`.
- Edits from source assets: `fal-ai/nano-banana-pro/edit`, then
  `openai/gpt-image-2/edit`, then
  `fal-ai/bytedance/seedream/v5/lite/edit`.
- Fast visual exploration: `fal-ai/flux-2/klein/9b`.
- Product reveal or social video: `bytedance/seedance-2.0/image-to-video`.
- Text-to-video concept or brand film: `bytedance/seedance-2.0/text-to-video`.
- Creator or spokesperson ad: load `ugc` and use `veed/fabric-1.0`,
  `veed/fabric-1.0/text`, or `fal-ai/creatify/aurora`.
- Multi-shot narrative: load `storytelling`.
- Single polished product asset: load `commercial`.

## Quality bar

Before returning:

- Every asset maps to a campaign role and channel.
- Product, UI, logo, and packaging are stable.
- Claims are user-supplied, observable, or removed.
- Text is either exact and schema-supported or reserved for external editing.
- Variants differ by one clear axis, not random style drift.
- Safe zones support overlays, cropping, and platform UI.
- Output paths come from `downloaded_files[]`.
- The final answer includes a campaign manifest: asset role, endpoint, request
  id, local path, prompt summary, and defects.

If the campaign feels generic, reduce the asset count and make each role more
specific before generating more variants.
