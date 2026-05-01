# Prompting Happy Horse 1.0

Alibaba's text-to-video model on fal.ai. Translates short, declarative text directions into video, particularly strong with camera moves and atmospheric lighting.

Endpoints:

- `alibaba/happy-horse/text-to-video`
- `alibaba/happy-horse/image-to-video`

## Core principle

**Brevity wins.** The default template is roughly 20 words:

```text
[Subject] [does action] in [setting], [time of day], [one atmosphere or camera cue].
```

If you keep adding adjectives, quality drops. The model wants direction, not enthusiasm.

## Strengths

- Camera moves: tracking shots, dolly-ins, steadicam glides, aerials
- Atmospheric lighting recipes: neon noir, blue hour, single-key setups
- Vehicles and metallic reflections
- Cloth / fabric motion in wind
- Fire and embers
- Wide establishing shots
- Mirror reflections with geometric consistency
- Short legible text (2-3 words max)

## Prompt structure

### Single-beat (~20 words)

```text
A young woman in a red coat walks down a wet city street at night, neon
reflections.
```

That is a complete prompt. Don't expand.

### With camera language (40-60 words)

Add lens type, camera move, and lighting cue at the end:

```text
A young woman in a red coat walks down a wet city street at night, neon
reflections, 35mm telephoto compression, slow tracking shot from behind,
sodium vapor practicals.
```

### Multi-beat action, use shot lists with timecodes

```text
Shot 1 (wide establishing, 0-1s): empty wet street under neon signs.
Shot 2 (mid tracking, 1-4s): woman in red coat walks toward camera.
Shot 3 (close push-in, 4-6s): rain hitting her shoulder, breath visible in cold air.
```

### Long single-take prompts

For extended single-take videos, use markdown sections (Subject, Action, Setting, Camera, Lighting, Mood). Keep each section short.

## Don't

- **Hedging adjectives.** "Beautiful", "stunning", "epic", "hyperrealistic", drop them all.
- **Stacked synonyms for colors.** "Red, crimson, scarlet", pick one.
- **Negative cues** unless addressing concrete risks.
- **Bare director name references.** "In the style of Wes Anderson" rarely works; describe the visual qualities you want instead.
- **Booru tags, JSON, weighted parentheses.** Plain prose only.
- **Multi-step prose sequences in a single prompt.** Use timecoded shot lists.
- **Extreme slow-motion cues** (1000fps).
- **Heavy wardrobe details during fast action.**

## Use instead

- Specific cinematography terms: "overcast daylight", "35mm telephoto", "sodium vapor lamps"
- One strong technical cue per shot
- Plain English prose
- Concrete framing labels: "wide establishing", "slow push-in close"

## Pattern matrix

**Works well:**

- Camera moves with lens specifications
- Atmospheric moods with color/lighting detail
- Single-character movement
- Environmental establishing shots

**Struggles:**

- Multi-step sequences in prose (use timecoded shot lists instead)
- Extreme time-dilation effects
- Intricate wardrobe during motion
- Long readable text inside the frame (limit to 2-3 words)

## Pre-generation checklist

Before submitting a prompt, verify:

- Subject and action in opening sentence?
- Under 30 words, or justified length?
- One cinematography cue maximum (per shot)?
- All non-specific adjectives cut?
- Multi-beat shots formatted as shot lists?
- Plain English, no structured syntax markup?

## Image-to-video

When chaining from a still:

```text
slow camera push-in toward the subject, subtle wind, ambient haze
```

That is the entire prompt. The reference frame already carries identity, wardrobe, lighting direction. Don't re-describe the still, describe motion only.

## Common parameters

Run `genmedia schema alibaba/happy-horse/text-to-video --json` for authoritative list. Typical:

- `prompt`: short declarative direction
- `aspect_ratio`: `16:9`, `9:16`, `1:1`
- `duration`: typically 4s or 6s
- `seed`: for reproducible iterations
- `image_url` (image-to-video), reference frame
