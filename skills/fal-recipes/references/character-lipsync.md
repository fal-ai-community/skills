# Character Lip-Sync Recipe

Use this recipe to create talking-head video, sync lips to existing footage, or animate a portrait with voiced expression. Three flows depending on starting material.

## Inputs to collect

- **Source face/portrait**: image URL or local path. Should be a clear front-facing portrait.
- **Speech source**: one of:
 - existing audio file (URL or local)
 - text to be spoken (TTS will be generated first)
 - existing video (lip-sync mode replaces only the mouth area)
- **Style preference**: talking-head endpoint vs avatar endpoint vs lip-sync of existing video.
- **Duration / aspect ratio**.
- **Voice preference** for TTS-driven flows.

## Flow A: talking head from image + audio

Single-step: face image + audio file → animated video.

```bash
URL_FACE=$(genmedia upload ./portrait.jpg --json | jq -r '.url')
URL_AUDIO=$(genmedia upload ./speech.mp3 --json | jq -r '.url')

genmedia run veed/fabric-1.0 \
 --image_url "$URL_FACE" \
 --audio_url "$URL_AUDIO" \
 --async \
 --json
```

Then poll status and download:

```bash
genmedia status veed/fabric-1.0 <request_id> \
 --download "./outputs/talking-head/{request_id}_{index}.{ext}" \
 --json
```

## Flow B: talking head from image + text (auto-TTS chain)

Two-step: TTS first, then talking-head.

```bash
URL_FACE=$(genmedia upload ./portrait.jpg --json | jq -r '.url')

# Step 1: TTS
TTS_RESULT=$(genmedia run fal-ai/minimax/speech-2.6-turbo \
 --text "Hello, welcome to our presentation." \
 --json)
URL_AUDIO=$(echo "$TTS_RESULT" | jq -r '.audio.url')

# Step 2: animate the portrait with the generated audio
genmedia run veed/fabric-1.0 \
 --image_url "$URL_FACE" \
 --audio_url "$URL_AUDIO" \
 --async \
 --json
```

Alternative: `veed/fabric-1.0/text` accepts text directly when supported.

```bash
genmedia run veed/fabric-1.0/text \
 --image_url "$URL_FACE" \
 --text "Hello, welcome to our presentation." \
 --async \
 --json
```

For an avatar with optional visual direction (gestures, framing):

```bash
genmedia run fal-ai/creatify/aurora \
 --image_url "$URL_FACE" \
 --audio_url "$URL_AUDIO" \
 --visual_direction "soft side lighting, slight head tilt, medium close-up" \
 --async \
 --json
```

## Flow C: lip-sync to existing video

Replace the mouth area in an existing video to match new audio.

```bash
URL_VIDEO=$(genmedia upload ./original-video.mp4 --json | jq -r '.url')
URL_AUDIO=$(genmedia upload ./new-speech.mp3 --json | jq -r '.url')

genmedia run fal-ai/sync-lipsync/v2 \
 --video_url "$URL_VIDEO" \
 --audio_url "$URL_AUDIO" \
 --async \
 --json
```

Use this when the rest of the performance (head movement, expression, gestures) should stay intact and only the mouth needs to match new dialogue.

## Endpoint reference

| Endpoint | Mode | When to use |
|----------|------|-------------|
| `veed/fabric-1.0` | image + audio → video | Default talking head from a still portrait |
| `veed/fabric-1.0/text` | image + text → video | Skip explicit TTS step |
| `fal-ai/creatify/aurora` | image + audio (+ direction) → video | Avatar with visual direction controls |
| `fal-ai/sync-lipsync/v2` | video + audio → synced video | Replace mouth in existing footage |

For TTS endpoint selection, see [fal-models-catalog/text-to-audio.md](../../fal-models-catalog/references/text-to-audio.md).

## Quality bar

Before returning:

- Mouth shapes match audio phonemes (no obvious mismatches).
- Head pose is stable; no face drift mid-sentence.
- Eyes blink naturally; no frozen gaze unless intentional.
- Audio is synced, no leading/trailing silence mismatch.
- For Flow C, the rest of the video is unchanged (no flickering background).

## Common parameters

Always inspect schema before running:

```bash
genmedia schema veed/fabric-1.0 --json
genmedia schema fal-ai/sync-lipsync/v2 --json
```

Frequently exposed:

- `image_url` / `audio_url` / `video_url`, depending on flow
- `text`: for `/text` variants
- `aspect_ratio`: `9:16` for vertical/social, `16:9` for landscape
- `quality`: when supported

## Tips

- Front-facing portrait works best. Three-quarter angle and profile reduce quality.
- Clean audio (no music behind speech) lip-syncs more accurately.
- For TTS-driven flows, generate a short test (one sentence) before committing to a full script, voice matching matters.
- Keep first attempts under 10 seconds; longer clips often introduce drift.
