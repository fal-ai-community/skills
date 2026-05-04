# Character Design Recipe

Use this recipe when the user wants to create, refine, or preserve a character. The main objective is **consistency**: keep the character anchor stable and change only the requested scene, expression, outfit, camera, or action.

## Inputs to collect

Only ask for missing inputs that affect identity or model routing.

- Character type: realistic human, stylized, anime, mascot, fantasy, sci-fi.
- Identity anchor: age range, face shape, hair, eyes, build, posture, marks.
- Style: photographic, 3D, illustration, manga, comic, game concept art.
- Needed outputs: portrait, full body, turnaround, expression sheet, outfit set, action still, video shot, edit of an existing character.
- References: source image, approved design, costume, pose, style board.
- Consistency level: exploratory, pitch-ready, production continuity.

## Genmedia workflow

1. Routed endpoints (see [fal-models-catalog/text-to-image](../../fal-models-catalog/references/text-to-image.md) and [image-to-image](../../fal-models-catalog/references/image-to-image.md)):

 ```bash
 genmedia models --endpoint_id openai/gpt-image-2 --json
 genmedia models --endpoint_id fal-ai/nano-banana-pro/edit --json
 genmedia models --endpoint_id bytedance/seedance-2.0/image-to-video --json
 genmedia models --endpoint_id veed/fabric-1.0 --json
 ```

 Fallback discovery:

 ```bash
 genmedia docs "consistent character generation" --json
 genmedia models "image editing character consistency" --json
 ```

2. Inspect schema before each run.

 ```bash
 genmedia schema <endpoint_id> --json
 genmedia pricing <endpoint_id> --json
 ```

3. Upload references.

 ```bash
 genmedia upload ./character-reference.png --json
 genmedia upload ./costume-reference.png --json
 ```

4. Run stills or sheets:

 ```bash
 genmedia run <endpoint_id> \
 --prompt "<anchor + variable prompt>" \
 --image_url "<reference url if supported>" \
 --download "./outputs/characters/{request_id}_{index}.{ext}" \
 --json
 ```

5. Run video async:

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

Use only schema-supported fields. If the model exposes seed, reference image, image strength, multiple image inputs, or negative prompt, use them deliberately and record what was used.

## Anchor system

The anchor is the **identity contract**. Keep it compact and repeat it in every prompt that should preserve the same character.

### Anchor fields

- **Codename**: neutral name if the user has not named the character.
- **Age range**: avoid exact age unless supplied.
- **Face**: shape, cheekbones, jawline, chin.
- **Eyes**: shape, spacing, eyelids, color, brows.
- **Nose and mouth**: bridge, tip, lip shape, smile line.
- **Skin**: tone, freckles, scars, moles, texture.
- **Hair**: color, length, texture, part, silhouette.
- **Build**: height impression, shoulders, posture, proportions.
- **Signature**: clothing silhouette, accessory, color accent, symbolic prop.
- **Style**: photoreal, anime, painterly, 3D, comic, game concept art.

### Immutable anchor template

```text
CHARACTER ANCHOR:
[codename], [age range], [gender presentation if relevant], [face shape],
[eye shape and color], [brow shape], [nose], [mouth], [skin details],
[hair color, length, texture, and style], [build and posture],
[signature wardrobe or accessory], [visual style]
```

### Variable template

```text
SHOT VARIABLE:
[expression], [pose/action], [outfit allowed to change or not], [setting],
[camera distance and angle], [lighting], [mood], [output format]
```

### What can change

- Expression
- Pose
- Camera angle
- Lighting
- Setting
- Outfit (only if requested)
- Time period (only if requested)
- Medium (only if requested)

### What should not drift

- Eye spacing and shape
- Face silhouette
- Nose and lip structure
- Hair silhouette
- Skin marks
- Body proportions
- Signature accessory
- Overall style target

### Consistency escalation

1. Text-only anchor for exploration.
2. Approved image reference for continuity.
3. Edit or reference-image workflow for outfit and expression variations.
4. Image-to-video from an approved still for motion.
5. User-selected identity-preserving endpoint for production series.

If a result changes identity, **strengthen the anchor or switch to a reference/edit workflow** instead of adding more style words.

## Prompt patterns

### First concept portrait

```text
CHARACTER ANCHOR:
[anchor]

SHOT VARIABLE:
waist-up portrait, neutral expression, relaxed posture, simple background,
[lighting], [style], clean readable design, no extra characters
```

### Full-body design

```text
CHARACTER ANCHOR:
[anchor]

SHOT VARIABLE:
full-body character design standing pose, entire silhouette visible, costume
details clear, simple neutral background, front view, production concept art,
no cropped feet, no extra props unless requested
```

### Turnaround sheet

```text
CHARACTER ANCHOR:
[anchor]

SHOT VARIABLE:
character turnaround sheet with front view, side view, back view, consistent
proportions and outfit, neutral standing pose, clean white background,
production model sheet layout, no style drift between views
```

### Expression sheet

```text
CHARACTER ANCHOR:
[anchor]

SHOT VARIABLE:
expression sheet with nine head-and-shoulder portraits: neutral, happy,
angry, afraid, sad, surprised, suspicious, determined, amused; same face,
same hairstyle, same style, clean grid, no identity drift
```

### Outfit variation

```text
keep the uploaded character's face, hair, body proportions, and style exactly
consistent; change only the outfit to [outfit], [material and color], same
pose or simple standing pose, clean studio background, no face changes
```

### Character video shot

```text
[duration] second shot of the uploaded character, same face, hair, outfit, and
body proportions, [specific action], [camera movement], [environment],
[lighting], controlled motion, no age drift, no costume morphing
```

### Negative prompt components

Use only when supported by schema:

```text
different face, different hairstyle, different eye color, altered age,
changed outfit, extra character, distorted hands, inconsistent style, cropped
body, duplicate character, text, watermark
```

## Examples

### Realistic editorial character

```text
CHARACTER ANCHOR:
Maren, woman in her early 30s, oval face with high cheekbones, almond green
eyes, straight nose, soft defined lips, light olive skin with a small mole
under the left eye, dark auburn shoulder-length wavy hair with a center part,
slim athletic build, upright calm posture, charcoal wool coat and small silver
ear cuff, realistic cinematic photography

SHOT VARIABLE:
waist-up portrait in a quiet train station at blue hour, thoughtful expression,
three-quarter angle, soft practical lights behind her, shallow depth of field,
35mm documentary lens feel, no extra people in focus
```

### Stylized sci-fi pilot

```text
CHARACTER ANCHOR:
Kade, young adult male sci-fi pilot, square face, heavy brows, narrow dark
brown eyes, short black textured hair, warm brown skin, compact muscular
build, matte white flight jacket with orange collar stripe, small triangular
mission patch on left chest, high-end animated feature style

SHOT VARIABLE:
full-body design sheet, front view, helmet tucked under one arm, neutral gray
background, clean readable silhouette, precise costume seams, no extra logos
```

### Mascot concept

```text
CHARACTER ANCHOR:
round friendly tea-shop mascot, small fox-like creature with cream fur, amber
ears, oversized green scarf, tiny ceramic cup pendant, soft plush proportions,
warm illustrated brand mascot style

SHOT VARIABLE:
three-quarter standing pose, waving with one paw, simple mint background,
clear silhouette, cheerful but not childish, no text, no extra mascots
```

### Outfit-only edit

```text
keep the uploaded character's face, hairstyle, skin tone, body proportions,
and illustration style exactly the same; change only the outfit to a navy
raincoat over a cream sweater, wet street lighting, same identity, no face
changes, no age changes, no additional characters
```

## Quality bar

Reject or retry when:

- Face shape, eye spacing, hairstyle, marks, or body build drift.
- Outfit changes when the prompt says only expression or pose should change.
- The sheet mixes styles across panels.
- Hands or props distract from the requested design task.
- Video motion changes age, face, costume, or silhouette.

Return downloaded paths and include the anchor used so future prompts can reuse the same identity.
