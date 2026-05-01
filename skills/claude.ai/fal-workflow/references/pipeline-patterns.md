# Pipeline patterns

## Fan-out parallel pipeline

Use for multi-scene video, batches, datasets, and variant exploration.

```text
planner -> structured plan
planner -> extract shot 1 -> generate 1 -> utility 1
planner -> extract shot 2 -> generate 2 -> utility 2
planner -> extract shot N -> generate N -> utility N
all outputs -> assembly
```

Rules:

- Planner output must be structured JSON or clearly delimited text.
- Independent lanes can run in parallel.
- Assembly waits until every required lane is complete.
- Record each lane's request ID and downloaded file.

## Sequential compositing chain

Use when each step must preserve the previous result.

```text
base scene -> add product -> add person -> add effect -> final image -> video
```

Rules:

- One edit pass changes one thing.
- Every edit prompt states what must be preserved.
- Use the previous result URL as the next input when possible.
- Check identity, product shape, and lighting before advancing.

## Contact sheet then slice

Use for character poses, product angles, style variants, and dataset panels.

```text
generate grid -> crop panel 1..N -> upscale panel 1..N -> optional video
```

Rules:

- Generate panels in one image when consistency matters.
- Prompt for exact grid layout and no visible borders or gaps.
- Crop by percentage coordinates if the crop utility expects percentages.
- Upscale after crop when final quality matters.

## Frame bridging

Use for long continuous videos.

```text
start image -> clip 1 -> extract last frame -> clip 2 -> extract last frame -> clip N -> merge
```

Rules:

- The last frame of one clip becomes the start image of the next clip.
- Motion prompt stays short and physically specific.
- Keep visual anchors stable across clips.
- Merge only after all clips pass continuity checks.

## Start/end frame interpolation

Use for precise product reveals, character motion, and controlled transitions.

```text
start frame -> edit into end frame -> video from start and end
```

Rules:

- Create the end frame by editing the start frame, not independent generation.
- Motion prompt describes only the transition.
- Use degrees, directions, distances, and speed rather than vague movement.

## Multi-modal assembly

Use for narration, music, subtitles, and visual clips.

```text
scene plan -> narration text -> TTS
scene plan -> image prompt -> image -> video
TTS + video -> join audio video
joined clips -> subtitles -> final assembly
```

Rules:

- Visual and audio lanes can run in parallel.
- Merge audio with each scene before final concatenation.
- Keep voice settings consistent.
- Disable generated video audio if external TTS is used and schema supports it.

## Multi-expert planning

Use for complex briefs with strategy, art direction, motion, and format
variation.

```text
brief -> brand analysis
brand analysis -> strategist
brand analysis -> art director
brand analysis -> motion director
experts -> master prompt plan -> generation nodes
```

Rules:

- Each expert output must be structured.
- Master plan removes repetition across angles, backgrounds, and lighting.
- This is a planning pattern. Generation still uses discovered genmedia models.

## Systematic variation matrix

Use for product sets, style exploration, character sheets, and A/B testing.

```text
base prompt + angle A + light A -> output 1
base prompt + angle B + light A -> output 2
base prompt + angle A + light B -> output 3
```

Rules:

- Vary one controlled axis per node when analyzing results.
- Keep all identity and product constraints identical.
- Avoid random changes when the user needs comparable outputs.
