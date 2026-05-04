---
name: cinematography
description: >
  Design cinematic image and video prompts for genmedia. Use this for shot
  language, camera movement, lighting, lens choices, color grade, film texture,
  scene blocking, and production-ready visual direction.
---

# Cinematography with genmedia

Use this skill when the user needs cinematic direction, not generic "make it
cinematic" prompting. Load references as needed:

- `references/shot-language.md`
- `references/lighting-lens-color.md`
- `references/examples.md`

Load `model-routing` alongside this skill for default endpoint choices.

Write concrete visual direction. Avoid empty prestige words and em dashes.

## Inputs to collect

Ask only for what affects the shot:

- Subject and action.
- Medium: still image, video, image-to-video, edit, storyboard frame.
- Genre and mood.
- Framing: close-up, medium, wide, overhead, POV, profile, locked-off.
- Camera motion for video: push-in, dolly, tracking, handheld, crane, drone.
- Lens feel: wide, normal, telephoto, macro, shallow or deep focus.
- Lighting: natural, practical, studio, noir, high key, low key, backlit.
- Output: aspect ratio, duration, first frame, last frame, download path.
- Preferred model, if the user wants a specific cinematography model or
  quality/cost profile.

## Genmedia workflow

1. Start from routed endpoint IDs.

   ```bash
   genmedia models --endpoint_id openai/gpt-image-2 --json
   genmedia models --endpoint_id fal-ai/nano-banana-pro --json
   genmedia models --endpoint_id bytedance/seedance-2.0/text-to-video --json
   genmedia models --endpoint_id bytedance/seedance-2.0/image-to-video --json
   genmedia models --endpoint_id xai/grok-imagine-video/text-to-video --json
   ```

   Use text search only as fallback discovery for a missing camera-control
   role:

   ```bash
   genmedia models "cinematic video generation camera movement" --json
   genmedia docs "video generation camera movement prompt" --json
   ```

2. Inspect schema and use only supported controls.

   ```bash
   genmedia schema <endpoint_id> --json
   genmedia pricing <endpoint_id> --json
   ```

3. Upload references when using image-to-video, first frame, last frame, style
   reference, or character/product continuity.

   ```bash
   genmedia upload ./frame.png --json
   ```

4. Run stills with direct download.

   ```bash
   genmedia run <endpoint_id> \
     --prompt "<cinematography prompt>" \
     --download "./outputs/cinema/{request_id}_{index}.{ext}" \
     --json
   ```

5. Run video async.

   ```bash
   genmedia run <endpoint_id> \
     --prompt "<shot prompt>" \
     --image_url "<uploaded frame if supported>" \
     --async \
     --json

   genmedia status <endpoint_id> <request_id> \
     --download "./outputs/cinema/{request_id}_{index}.{ext}" \
     --json
   ```

## Prompt build order

Use the SCLCAM structure:

1. Subject: who or what is in frame.
2. Context: location, time, weather, story moment.
3. Lens/framing: distance, angle, focal length feel, depth of field.
4. Camera motion: only for video or if motion blur is desired.
5. Atmosphere: haze, rain, practicals, reflections, texture.
6. Mood/color: palette, contrast, grade, exposure style.
7. Output controls: aspect ratio, duration, first-frame continuity.

Example structure:

```text
[subject] in [context], framed as [shot size and angle], [lens feel],
[lighting setup], [camera movement if video], [color grade], [texture],
[duration or aspect ratio], [continuity constraints]
```

## Model routing

- Premium realistic still: use `openai/gpt-image-2`.
- Premium stylized still: use `openai/gpt-image-2`, then
  `fal-ai/nano-banana-pro`, then `fal-ai/nano-banana-2`.
- Fast draft still: use `fal-ai/flux-2/klein/9b`.
- Highest quality video: use `bytedance/seedance-2.0/text-to-video` or
  `bytedance/seedance-2.0/image-to-video`.
- Motion from a strong frame: use `bytedance/seedance-2.0/image-to-video`.
- Fast or lower-cost video: use `xai/grok-imagine-video/text-to-video` or
  `xai/grok-imagine-video/image-to-video`.
- Complex camera language: inspect Seedance 2.0 first, then Kling v3 when
  multi-prompt or element controls matter.
- Story sequence: use the storytelling skill with this skill as shot-language
  support.
- Character or product continuity: use the relevant domain skill first, then
  apply cinematography as the variable block.

## Quality bar

Before returning, check:

- Camera movement is physically plausible for the scene.
- Lens, shot size, and camera angle do not contradict each other.
- Lighting direction is clear and consistent.
- Color grade supports the mood without flattening subject detail.
- Video prompt describes one shot unless the selected model supports multiple
  prompts or shot lists.
- Downloaded files come from `downloaded_files[]`.

If a result looks generic, improve specificity in camera, blocking, light, and
environment before adding more adjectives.
