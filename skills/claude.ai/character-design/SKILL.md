---
name: character-design
description: >
  Build consistent character designs and character media with genmedia. Use
  this for original characters, reference sheets, expression sheets, outfit
  variations, identity-preserving edits, and character-to-video workflows.
---

# Character design with genmedia

Use this skill when the user wants to create, refine, or preserve a character.
Load the reference files when needed:

- `references/anchor-system.md`
- `references/prompt-patterns.md`
- `references/examples.md`

Load `model-routing` alongside this skill for default endpoint choices.

The main objective is consistency. Keep the character anchor stable and change
only the requested scene, expression, outfit, camera, or action.

## Inputs to collect

Only ask for missing inputs that affect identity or model routing.

- Character type: realistic human, stylized, anime, mascot, fantasy, sci-fi.
- Identity anchor: age range, face shape, hair, eyes, build, posture, marks.
- Style: photographic, 3D, illustration, manga, comic, game concept art.
- Needed outputs: portrait, full body, turnaround, expression sheet, outfit
  set, action still, video shot, edit of an existing character.
- References: source image, approved design, costume, pose, style board.
- Consistency level: exploratory, pitch-ready, production continuity.
- Model preference: use `model-routing` defaults unless the user names a model
  or the job needs a quality/cost tradeoff decision.

## Genmedia workflow

1. Start from routed endpoint IDs.

   ```bash
   genmedia models --endpoint_id openai/gpt-image-2 --json
   genmedia models --endpoint_id fal-ai/nano-banana-pro/edit --json
   genmedia models --endpoint_id bytedance/seedance-2.0/image-to-video --json
   genmedia models --endpoint_id veed/fabric-1.0 --json
   ```

   Use text search only as fallback discovery for an unsupported role:

   ```bash
   genmedia docs "consistent character generation" --json
   genmedia models "image editing character consistency" --json
   ```

2. Inspect schema before each endpoint run.

   ```bash
   genmedia schema <endpoint_id> --json
   genmedia pricing <endpoint_id> --json
   ```

3. Upload references.

   ```bash
   genmedia upload ./character-reference.png --json
   genmedia upload ./costume-reference.png --json
   ```

4. Run stills or sheets with download.

   ```bash
   genmedia run <endpoint_id> \
     --prompt "<anchor + variable prompt>" \
     --image_url "<reference url if supported>" \
     --download "./outputs/characters/{request_id}_{index}.{ext}" \
     --json
   ```

5. Run video async.

   ```bash
   genmedia run <endpoint_id> \
     --prompt "<anchor + shot action>" \
     --image_url "<approved character frame if supported>" \
     --async \
     --json

   genmedia status <endpoint_id> <request_id> \
     --download "./outputs/characters/{request_id}_{index}.{ext}" \
     --json
   ```

Use only schema-supported fields. If the model supports seed, reference image,
image strength, multiple image inputs, or negative prompt, use them deliberately
and record what was used.

## Character anchor

Create a short immutable anchor before generating.

```text
CHARACTER ANCHOR:
[name or codename], [age range], [face shape], [eye shape and color],
[nose and lips], [skin tone and distinguishing marks], [hair color, texture,
style], [body build and posture], [signature clothing or silhouette],
[style target]
```

Then add a variable block for the current shot.

```text
SHOT VARIABLE:
[expression], [pose/action], [outfit changes if allowed], [environment],
[camera/framing], [lighting], [mood]
```

Never rewrite the anchor casually. If a result changes identity, strengthen the
anchor or switch to a reference/edit workflow instead of adding more style
words.

## Model routing

- New character concept with maximum consistency: use `openai/gpt-image-2`.
- Premium but cheaper image option: use `fal-ai/nano-banana-pro` or
  `fal-ai/nano-banana-2`.
- Fast exploratory drafts: use `fal-ai/flux-2/klein/9b`.
- Consistent sheet from an approved character: use `openai/gpt-image-2` first;
  if editing an existing image, inspect `openai/gpt-image-2/edit`.
- Outfit variations and character edits: use `fal-ai/nano-banana-pro/edit`,
  then `openai/gpt-image-2/edit`, then
  `fal-ai/bytedance/seedream/v5/lite/edit`.
- Expression sheet: one approved face reference, multiple controlled
  expression prompts.
- Character video: approved still frame first, then
  `bytedance/seedance-2.0/image-to-video` for final quality.
- Fast video drafts: use `xai/grok-imagine-video/image-to-video`.
- Talking avatar or lip-sync: use `veed/fabric-1.0`,
  `veed/fabric-1.0/text`, or `fal-ai/creatify/aurora`.

## Quality bar

Reject or retry when:

- Face shape, eye spacing, hairstyle, marks, or body build drift.
- Outfit changes when the prompt says only expression or pose should change.
- The sheet mixes styles across panels.
- Hands or props distract from the requested design task.
- Video motion changes age, face, costume, or silhouette.

Return downloaded paths and include the anchor used so future prompts can reuse
the same identity.
