# Workflow recipes

## Multi-scene cinematic video

Input: concept, style, duration, aspect ratio.

```text
1. Planner creates N scenes with start frame prompt, end frame edit prompt, and motion prompt.
2. Generate start frames in parallel.
3. Edit start frames into end frames in parallel.
4. Run image-to-video for each scene with start and end frames if schema supports it.
5. Download clips.
6. Merge clips if a suitable utility endpoint is selected and verified.
7. Return clip manifest in playback order.
```

Use `storytelling` and `cinematography` references for shot language.

## Product campaign

Input: product reference, brand tone, deliverables.

```text
1. Upload product reference.
2. Generate or edit hero image while preserving product identity.
3. Create platform variants: square, vertical, wide, PDP.
4. Create one product reveal clip from the approved hero frame.
5. Add controlled text only through a utility endpoint or external design step.
6. Download all assets and return a campaign manifest.
```

Use `commercial` for product prompt rules.

## Character continuity sequence

Input: approved character reference, scene list.

```text
1. Use character anchor and uploaded reference.
2. Generate approved still for each scene or expression.
3. Run image-to-video per shot from approved stills.
4. Reject clips with face, hair, wardrobe, or age drift.
5. Return shot order and local clip paths.
```

Use `character-design` for anchor and prompt patterns.

## Narrated documentary

Input: topic, runtime, voice direction, visual style.

```text
1. Planner creates scene table with narration, visual prompt, and duration.
2. Generate TTS or upload voiceover.
3. Generate images or clips per scene.
4. Join each scene's audio and video.
5. Add subtitles.
6. Download final scene files or merged output.
```

Keep narration, subtitles, and visuals aligned by duration.

## Dataset generator

Input: task definition and target count.

```text
1. Planner creates N diverse prompt pairs.
2. Generate original images in parallel.
3. Apply edit or transformation in parallel.
4. Generate captions or metadata from actual outputs.
5. Return triplets: original, transformed, caption.
```

Keep variation controlled and track every seed or schema parameter if used.

## Style exploration

Input: reference asset and target style family.

```text
1. Build a variation matrix with one changed axis per row.
2. Run image edit or generation nodes in parallel.
3. Download all variants.
4. Return a selection table with style axis, endpoint, output path, and notes.
```

Use systematic variation before random shotgun variation unless the user asks
for broad ideation.

## Social media batch

Input: master creative, target platforms.

```text
1. Generate or choose master asset.
2. Resize or crop for each platform.
3. Add platform-safe text externally or through text utility.
4. Compress for web delivery.
5. Return outputs grouped by platform and aspect ratio.
```

Do not rely on generated in-image text for final ad copy.
