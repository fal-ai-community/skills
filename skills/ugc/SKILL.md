---
name: ugc
description: >
  Plan and run UGC-style creator ads and social proof videos with genmedia.
  Use this for direct-to-camera creator scripts, talking-head ads, product
  demos, testimonials, founder clips, unboxing, reaction, before-after,
  faceless voiceover, and short vertical social videos.
---

# UGC production with genmedia

Use this skill when the user wants creator-style content rather than polished
studio advertising. Load references as needed:

- `references/formats.md`
- `references/workflows.md`
- `references/examples.md`

Load `model-routing` alongside this skill for default endpoint choices.

Keep outputs believable, platform-native, and claim-safe. Do not write fake
testimonials, fake metrics, invented reviews, medical claims, financial
claims, or readable legal copy unless the user provides the exact wording.

## Inputs to collect

Only ask when the answer changes execution.

- Product or offer: what is being shown, sold, taught, or explained.
- Format: direct-to-camera, demo, reaction, unboxing, founder, faceless b-roll.
- Speaker: supplied portrait/video, generated avatar, no face, or voiceover.
- Script source: exact script, bullet points, offer copy, or ask to draft.
- Platform: TikTok, Reels, Shorts, paid social, landing page, prototype.
- Runtime and crop: usually 9:16, 6-15 seconds for hooks, 15-45 seconds for ads.
- Source media: portrait, product image, product video, logo, b-roll, audio.
- Claims: proof the user supplied, required disclaimers, banned phrases.
- Tone: casual, expert, founder-led, skeptical, excited, calm, documentary.

## Genmedia workflow

1. Start from routed endpoint IDs.

   ```bash
   genmedia models --endpoint_id veed/fabric-1.0 --json
   genmedia models --endpoint_id veed/fabric-1.0/text --json
   genmedia models --endpoint_id fal-ai/creatify/aurora --json
   genmedia models --endpoint_id fal-ai/sync-lipsync/v2 --json
   genmedia models --endpoint_id bytedance/seedance-2.0/image-to-video --json
   genmedia models --endpoint_id openai/gpt-image-2 --json
   ```

   Use text search only as fallback discovery for missing roles:

   ```bash
   genmedia models "ugc talking head avatar" --json
   genmedia models "short social video product demo" --json
   genmedia docs "lip sync video" --json
   ```

2. Inspect the selected endpoint before running.

   ```bash
   genmedia schema <endpoint_id> --json
   genmedia pricing <endpoint_id> --json
   ```

3. Upload all local source media.

   ```bash
   genmedia upload ./creator.jpg --json
   genmedia upload ./product.png --json
   genmedia upload ./voiceover.wav --json
   genmedia upload ./existing-clip.mp4 --json
   ```

4. Choose the production route.

   - Portrait plus audio: `veed/fabric-1.0`.
   - Portrait plus text: `veed/fabric-1.0/text` when schema supports it.
   - Avatar with stronger visual direction: `fal-ai/creatify/aurora`.
   - Existing video with new speech: `fal-ai/sync-lipsync/v2`.
   - Product b-roll: `bytedance/seedance-2.0/image-to-video` from an approved
     still or product reference.
   - Hook frames and thumbnails: `openai/gpt-image-2`, especially when text or
     product fidelity matters.

5. Run long video jobs async and download from status.

   ```bash
   genmedia run <endpoint_id> \
     --prompt "<ugc visual direction or shot prompt>" \
     --async \
     --json

   genmedia status <endpoint_id> <request_id> \
     --download "./outputs/ugc/{request_id}_{index}.{ext}" \
     --json
   ```

6. Use schema fields exactly. Mirror the model's field names such as
   `image_url`, `audio_url`, `video_url`, `text`, `prompt`,
   `visual_direction`, `aspect_ratio`, `duration`, or `seed`.

## Script build order

Build scripts as short spoken beats, not polished ad copy:

1. Hook: one concrete tension, problem, result, or curiosity gap.
2. Context: why this speaker cares or what situation they are in.
3. Product moment: product appears, is used, or is shown solving a problem.
4. Proof: sensory detail, visible demo, supplied metric, or user-provided fact.
5. Turn: before-after, objection answered, or unexpected benefit.
6. Close: soft CTA, next action, or clean final product frame.

Keep claims grounded. Replace unsupported claims with observable statements:
"the texture looks lighter" beats "this cures acne".

## Prompt build order

For each UGC clip or shot, write:

1. Speaker and frame: creator type, age range if supplied, setting, crop.
2. Performance: eye contact, casual delivery, gestures, expression, pace.
3. Product action: held up, opened, applied, compared, demonstrated, shown.
4. Camera: handheld phone, desk tripod, mirror shot, close-up, b-roll insert.
5. Lighting and audio feel: natural window, bathroom light, car interior.
6. Platform constraints: 9:16, safe top/bottom zones, no generated captions.
7. Guardrails: no fake claims, no new logos, no changed product packaging.

## Model routing

- Talking head from portrait and audio: `veed/fabric-1.0`.
- Talking head from portrait and text: `veed/fabric-1.0/text`.
- Avatar with visual direction: `fal-ai/creatify/aurora`.
- Lip-sync existing footage: `fal-ai/sync-lipsync/v2`.
- Product b-roll or demo motion: `bytedance/seedance-2.0/image-to-video`.
- Fast draft b-roll: `xai/grok-imagine-video/image-to-video`.
- Creator keyframes, thumbnails, and product-faithful stills:
  `openai/gpt-image-2` or `fal-ai/nano-banana-pro`.
- TTS: use `fal-models-catalog/references/text-to-audio.md` and inspect
  schema. Prefer short test sentences before full scripts.

## Quality bar

Before returning:

- The clip feels like plausible creator content, not a studio commercial.
- Spoken script length fits the requested runtime.
- Mouth motion is synced when a speaking face is used.
- Product shape, packaging, and logo are stable.
- Claims are supplied by the user or phrased as visible observations.
- The first 1-2 seconds have a clear hook.
- Captions or text overlays are not hallucinated inside the video.
- Output paths come from `downloaded_files[]`, not manually fetched URLs.

If the face drifts, shorten the script, use cleaner portrait/audio inputs, or
switch from generated avatar to lip-syncing approved source footage.
