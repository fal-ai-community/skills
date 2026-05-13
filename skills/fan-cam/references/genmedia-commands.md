# Genmedia command patterns

Use these command patterns to run the fan-cam pipeline. Inspect schemas in the
current session before using them.

## Verify endpoints

```bash
genmedia models --endpoint_id openai/gpt-image-2/edit --json
genmedia models --endpoint_id openai/gpt-image-2 --json
genmedia models --endpoint_id fal-ai/kling-video/v3/standard/image-to-video --json
genmedia models --endpoint_id fal-ai/kling-video/v3/pro/image-to-video --json
genmedia models --endpoint_id fal-ai/kling-video/v3/4k/image-to-video --json
genmedia schema openai/gpt-image-2/edit --json
genmedia schema openai/gpt-image-2 --json
genmedia schema fal-ai/kling-video/v3/pro/image-to-video --format openapi --json
```

Swap the Kling endpoint in schema and pricing checks only when explicitly
choosing Standard for economy or 4K for native 4K video.

## Upload source image

If the user gives a local file:

```bash
PHOTO_URL=$(genmedia upload ./person.jpg --json | jq -r '.url')
```

If the user gives a remote URL, use it directly:

```bash
PHOTO_URL="https://example.com/person.jpg"
```

This URL is the identity reference, not the Kling `start_image_url`. For a
personalized fan-cam, always create the broadcast frame with
`openai/gpt-image-2/edit` before running Kling, unless the user explicitly
provides an already approved 16:9 fan-cam frame.

Build the GPT Image 2 image URL array:

```bash
IMAGE_URLS=$(jq -nc --arg url "$PHOTO_URL" '[$url]')
```

For optional extra references:

```bash
IMAGE_URLS=$(jq -nc \
  --arg person "$PHOTO_URL" \
  --arg venue "$VENUE_REF_URL" \
  '[$person, $venue]')
```

## Generate broadcast frame

Agent writes `IMAGE_PROMPT` first. This step creates the Kling-ready broadcast
frame from the identity photo and event brief.

```bash
GPT_IMAGE_QUALITY="${GPT_IMAGE_QUALITY:-high}"

FRAME=$(genmedia run openai/gpt-image-2/edit \
  --image_urls "$IMAGE_URLS" \
  --prompt "$IMAGE_PROMPT" \
  --image_size '{"width":3840,"height":2160}' \
  --quality "$GPT_IMAGE_QUALITY" \
  --output_format jpeg \
  --num_images 1 \
  --download "./outputs/fan-cam/frame_{request_id}_{index}.{ext}" \
  --json)

FRAME_URL=$(echo "$FRAME" | jq -r '.result.images[0].url')
FRAME_FILE=$(echo "$FRAME" | jq -r '.downloaded_files[0] // empty')
```

Use `FRAME_URL`, not `PHOTO_URL`, as Kling `start_image_url`.

Use `GPT_IMAGE_QUALITY=high` by default. Override with
`GPT_IMAGE_QUALITY=low` only for explicitly requested economy or preview runs.

## Two-pass plate workflow

Use this workflow when direct photo-to-scene editing fails quality gates or
when the brief needs reliable broadcast composition, scoreboard text, and a
real broadcaster bug.

First generate an identity-free broadcast plate:

```bash
PLATE=$(genmedia run openai/gpt-image-2 \
  --prompt "$PLATE_PROMPT" \
  --image_size '{"width":3840,"height":2160}' \
  --quality high \
  --output_format jpeg \
  --num_images 1 \
  --download "./outputs/fan-cam/plate_{request_id}_{index}.{ext}" \
  --json)

PLATE_URL=$(echo "$PLATE" | jq -r '.result.images[0].url')
PLATE_FILE=$(echo "$PLATE" | jq -r '.downloaded_files[0] // empty')
```

Then edit only the placeholder spectator with the user photo. Keep image URL
order stable: plate first, person photo second.

```bash
FRAME=$(genmedia run openai/gpt-image-2/edit \
  --image_urls "$(jq -nc --arg plate "$PLATE_URL" --arg photo "$PHOTO_URL" '[$plate, $photo]')" \
  --prompt "$IDENTITY_EDIT_PROMPT" \
  --image_size '{"width":3840,"height":2160}' \
  --quality high \
  --output_format jpeg \
  --num_images 1 \
  --download "./outputs/fan-cam/frame_{request_id}_{index}.{ext}" \
  --json)

FRAME_URL=$(echo "$FRAME" | jq -r '.result.images[0].url')
FRAME_FILE=$(echo "$FRAME" | jq -r '.downloaded_files[0] // empty')
```

For GPT Image 2 prompt stability, prefer short positive prompts. Avoid long
negative lists, exhaustive face-anatomy wording, and repeated "no X" clauses in
image prompts. Keep detailed negatives in the Kling `negative_prompt`.

## Optional frame compression

Kling image input has file size and dimension limits. If the generated frame is
too large, compress it:

```bash
COMPRESSED=$(genmedia run fal-ai/workflow-utilities/compress-image \
  --image_url "$FRAME_URL" \
  --max_width 1920 \
  --quality 92 \
  --output_format jpg \
  --optimize true \
  --json)

FRAME_URL=$(echo "$COMPRESSED" | jq -r '.result.image.url')
```

Use compression only when needed. Do not compress by default if the frame
already fits Kling limits and quality matters.

## Build multi prompt

Agent chooses 2 to 5 beats. Each beat duration must be at least 3 seconds and
the total must be at most 15 seconds.

Example for 12 seconds:

```bash
MULTI_PROMPT=$(jq -nc \
  --arg p1 "$P1" \
  --arg p2 "$P2" \
  --arg p3 "$P3" \
  --arg p4 "$P4" \
  '[
    {prompt:$p1,duration:"3"},
    {prompt:$p2,duration:"3"},
    {prompt:$p3,duration:"3"},
    {prompt:$p4,duration:"3"}
  ]')

TOTAL_DURATION="12"
```

Example for mixed durations:

```bash
MULTI_PROMPT=$(jq -nc \
  --arg p1 "$P1" \
  --arg p2 "$P2" \
  --arg p3 "$P3" \
  '[
    {prompt:$p1,duration:"3"},
    {prompt:$p2,duration:"5"},
    {prompt:$p3,duration:"4"}
  ]')

TOTAL_DURATION="12"
```

If you pass a real approved `elements` entry, every prompt must mention
`@Element1`. If not, do not invent an element; describe the featured spectator
from the `start_image_url`.

## Optional Kling element

```bash
ELEMENTS=$(jq -nc --arg url "$FRAME_URL" \
  '[{reference_image_urls:[$url],frontal_image_url:$url}]')
```

Use `--elements "$ELEMENTS"` only when that reference role is intentional and
approved by the user or source workflow.

## Generate video

Default to Kling v3 Pro:

```bash
KLING_ENDPOINT="${KLING_ENDPOINT:-fal-ai/kling-video/v3/pro/image-to-video}"
```

Override with `fal-ai/kling-video/v3/standard/image-to-video` only for
explicit economy or preview runs. Override with
`fal-ai/kling-video/v3/4k/image-to-video` only for explicit native 4K video
delivery.

Submit async:

```bash
SUBMIT=$(genmedia run "$KLING_ENDPOINT" \
  --start_image_url "$FRAME_URL" \
  --duration "$TOTAL_DURATION" \
  --multi_prompt "$MULTI_PROMPT" \
  --shot_type customize \
  --cfg_scale 0.3 \
  --generate_audio true \
  --negative_prompt "$NEGATIVE_PROMPT" \
  --async \
  --json)

REQ=$(echo "$SUBMIT" | jq -r '.request_id')
```

Add `--elements "$ELEMENTS"` only for real approved elements. Do not pass
`--end_image_url` together with `--multi_prompt`.

Poll and download:

```bash
VIDEO=$(genmedia status "$KLING_ENDPOINT" "$REQ" \
  --download "./outputs/fan-cam/video_{request_id}_{index}.{ext}" \
  --json)

VIDEO_URL=$(echo "$VIDEO" | jq -r '.result.video.url // .result.video // empty')
VIDEO_FILE=$(echo "$VIDEO" | jq -r '.downloaded_files[0] // empty')
```

## Manifest

Return a compact manifest:

```json
{
  "goal": "personalized sports broadcast fan cam",
  "image_endpoint": "openai/gpt-image-2/edit",
  "image_quality": "high",
  "image_size": { "width": 3840, "height": 2160 },
  "kling_endpoint": "fal-ai/kling-video/v3/pro/image-to-video",
  "total_duration": "12",
  "request_ids": {
    "image": "...",
    "video": "..."
  },
  "outputs": {
    "frame_url": "...",
    "video_url": "...",
    "downloaded_frame": "...",
    "downloaded_video": "..."
  },
  "notes": "defects or confirmation"
}
```
