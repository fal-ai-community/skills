# Character anchor system

The anchor is the identity contract. Keep it compact and repeat it in every
prompt that should preserve the same character.

## Anchor fields

- Codename: use a neutral name if the user has not named the character.
- Age range: avoid exact age unless supplied.
- Face: shape, cheekbones, jawline, chin.
- Eyes: shape, spacing, eyelids, color, brows.
- Nose and mouth: bridge, tip, lip shape, smile line.
- Skin: tone, freckles, scars, moles, texture.
- Hair: color, length, texture, part, silhouette.
- Build: height impression, shoulders, posture, proportions.
- Signature: clothing silhouette, accessory, color accent, symbolic prop.
- Style: photoreal, anime, painterly, 3D, comic, game concept art.

## Immutable anchor template

```text
CHARACTER ANCHOR:
[codename], [age range], [gender presentation if relevant], [face shape],
[eye shape and color], [brow shape], [nose], [mouth], [skin details],
[hair color, length, texture, and style], [build and posture],
[signature wardrobe or accessory], [visual style]
```

## Variable template

```text
SHOT VARIABLE:
[expression], [pose/action], [outfit allowed to change or not], [setting],
[camera distance and angle], [lighting], [mood], [output format]
```

## What can change

- Expression
- Pose
- Camera angle
- Lighting
- Setting
- Outfit, only if requested
- Time period, only if requested
- Medium, only if requested

## What should not drift

- Eye spacing and shape
- Face silhouette
- Nose and lip structure
- Hair silhouette
- Skin marks
- Body proportions
- Signature accessory
- Overall style target

## Consistency escalation

1. Text-only anchor for exploration.
2. Approved image reference for continuity.
3. Edit or reference-image workflow for outfit and expression variations.
4. Image-to-video from an approved still for motion.
5. User-selected identity-preserving endpoint for production series.
