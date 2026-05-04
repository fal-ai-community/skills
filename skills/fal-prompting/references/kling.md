# Prompting Kling

Kling is Kuaishou's video model family. Two generations are routinely useful on fal.ai:

- **Kling O3**: most powerful tier, separate Standard and Pro endpoints
- **Kling v3**: multi-prompt and element controls

## Endpoints (Kling O3)

### Image generation
| Endpoint | Tier |
|----------|------|
| `fal-ai/kling-image/o3/text-to-image` | Pro (only) |

### Video generation
| Endpoint | Tier | Mode |
|----------|------|------|
| `fal-ai/kling-video/o3/standard/text-to-video` | Standard | Text → Video |
| `fal-ai/kling-video/o3/pro/text-to-video` | Pro | Text → Video |
| `fal-ai/kling-video/o3/standard/image-to-video` | Standard | Image → Video |
| `fal-ai/kling-video/o3/pro/image-to-video` | Pro | Image → Video |

### Video editing
| Endpoint | Tier | Mode |
|----------|------|------|
| `fal-ai/kling-video/o3/standard/video-to-video/edit` | Standard | Content edit |
| `fal-ai/kling-video/o3/pro/video-to-video/edit` | Pro | Content edit |
| `fal-ai/kling-video/o3/standard/video-to-video/reference` | Standard | Style remix |
| `fal-ai/kling-video/o3/pro/video-to-video/reference` | Pro | Style remix |

### Endpoints (Kling v3): multi-shot storytelling
| Endpoint | Mode |
|----------|------|
| `fal-ai/kling-video/v3/pro/text-to-video` | Text → Video, supports multi-prompt |
| `fal-ai/kling-video/v3/pro/image-to-video` | Image → Video |

## Standard vs Pro

| Tier | Use for |
|------|---------|
| **Pro** | Final output, commercial work, hero shots, best quality |
| **Standard** | Drafts, iteration, A/B exploration. ~2x faster, ~half the cost |

Default to Pro for delivery. Use Standard only when iteration count matters more than per-frame quality.

## Prompt structure

Kling responds well to **direct, declarative prompts**. Don't pad with prestige adjectives.

Single-shot template (text-to-video, image-to-video):

```text
[subject doing action] in [setting], [time of day], [camera framing/movement],
[lighting/mood]
```

Example:

```text
A samurai walking through a misty bamboo forest at dawn, low handheld tracking
shot from behind, soft golden backlight filtering through leaves
```

## Multi-prompt sequences (Kling v3)

When the schema exposes a prompt array or shot list, write each shot as one declarative line. Keep cross-shot anchors (character, location, palette) in a global section if supported.

```text
SHOT 1: wide establishing of the bamboo forest at dawn
SHOT 2: medium tracking shot of the samurai walking forward
SHOT 3: close-up of his hand on the sword hilt
```

Inspect schema first, multi-prompt fields differ between endpoints.

```bash
genmedia schema fal-ai/kling-video/v3/pro/text-to-video --json
```

## Camera and motion vocabulary that works

- **Movement:** "slow push-in", "dolly left", "tracking shot", "crane up", "handheld", "locked-off", "orbit"
- **Framing:** "wide", "medium", "close-up", "macro", "POV", "over-the-shoulder", "Dutch angle"
- **Lens feel:** "35mm cinematic", "85mm portrait", "100mm macro", "wide 24mm"
- **Lighting:** "rim light", "backlight", "soft key", "noir hard key", "practical lights", "blue hour"

For full cinema vocabulary across families, see [fal-recipes/references/cinematography.md](../../fal-recipes/references/cinematography.md).

## Image-to-video specifics

When chaining from a still:

- The reference frame defines identity, wardrobe, lighting direction.
- The prompt should describe **motion only**, not re-describe the static scene.
- Keep motion physically plausible. Kling is conservative with implausible physics.

Good motion prompt:

```text
slow camera push-in toward the subject, subtle wind in hair, ambient haze drift
```

Bad (over-describes the still):

```text
A samurai with long dark hair wearing armor in a misty bamboo forest, cinematic
mood, walking forward... [Kling interprets as a fresh shot, may drift]
```

## Edit mode (video-to-video)

- **`/edit`** changes content while preserving motion (e.g., "change the sky to a starry night").
- **`/reference`** restyles the entire video to match a style cue (e.g., "transform into watercolor").

For `/edit`, state preservation explicitly:

```text
Change: the sky becomes a starry night with a visible moon.
Preserve: the subject, all motion, the foreground composition, the camera move.
```

## Don't

- Stack synonyms: "beautiful, gorgeous, stunning, magnificent", drop them all.
- Over-describe the static frame in image-to-video, describe motion.
- Use weighted parentheses or booru tags. Kling ignores them.
- Request extreme slow-motion (1000fps+), falls apart.
- Cram more than 30-40 words into a single-shot prompt unless schema explicitly supports more.

## Common parameters

Run `genmedia schema <endpoint_id> --json` for the authoritative list. Frequently exposed:

- `prompt`: the shot description
- `negative_prompt`: when supported, list specific things to avoid (not vague)
- `aspect_ratio`: `16:9`, `9:16`, `1:1` are usually the safe set
- `duration`: typically 5s or 10s; longer durations cost more and risk drift
- `seed`: for reproducible iterations
- `image_url` (image-to-video), uploaded reference frame
