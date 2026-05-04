# Utility endpoint reference

These are workflow utility candidates from the falgen workflow notes. Verify
availability with `genmedia models --endpoint_id <id> --json` or search, then
inspect schema before use.

## Image resize and transform

- `workflowutils/resize-image`: resize to explicit dimensions.
- `workflowutils/resize-to-max-pixels`: resize while preserving aspect ratio.
- `workflowutils/crop-image`: crop with percentage-based coordinates.
- `workflowutils/image-size`: return width and height.
- `workflow-utilities/compress-image`: compress and optionally resize.

## Image compositing and layout

- `workflowutils/composite-image`: layer images together.
- `workflow-utilities/overlay-image`: overlay with position, scale, opacity,
  and stroke.
- `workflow-utilities/concat-image`: concatenate images horizontally or
  vertically.
- `workflow-utilities/image-grid`: create a grid from multiple images.
- `workflow-utilities/add-text-to-image`: add controlled text after generation.

## Image conversion and masks

- `workflowutils/rgba-to-rgb`: convert transparent image to RGB.
- `workflow-utilities/split`: split multiple images into individual outputs.
- `workflow-utilities/merge`: merge multiple images into one output array.
- `workflowutils/sam-hq`: segmentation masks.
- `workflowutils/invert_mask`: invert a mask.
- `workflowutils/blur_mask`: soften mask edges.
- `workflowutils/grow_mask`: expand mask region.
- `workflowutils/shrink_mask`: contract mask region.
- `workflowutils/transparent-image-to_mask`: create a mask from alpha.

## Detection and safety

- `workflowutils/teed`: edge detector.
- `workflowutils/canny`: Canny edge detector.
- `workflowutils/image-preprocessors-canny`: alternate Canny endpoint.
- `workflowutils/face`: face detection or face processing.
- `workflowutils/brand-checker`: brand detection check.
- `workflowutils/llm-nsfw-checker`: text safety check.

## Video utilities

- `workflow-utilities/overlay-video`: overlay one video on another.
- `workflow-utilities/setpts-video`: change playback speed. Keep within
  schema bounds.
- `workflow-utilities/add-subtitles-to-video`: add provided subtitles.
- `workflow-utilities/auto-subtitle`: transcribe and add karaoke-style
  subtitles.
- `workflowutils/join-audio-video`: combine audio and video.
- `workflow-utilities/video-to-gif`: convert video segment to GIF.
- `workflow-utilities/gif-to-video`: convert GIF to video.

## Audio utilities

- `workflow-utilities/extract-audio`: extract audio from video.
- `workflow-utilities/split-audio`: split by timestamps.
- `workflow-utilities/merge-audio`: merge files with optional gaps.
- `workflow-utilities/amix-audio`: mix streams with weights and normalization.

## Text utilities

- `workflow-utilities/merge-text`: merge strings with a separator.
- `workflow-utilities/split-text`: split text by delimiter.
- `workflowutils/text-concat`: concatenate text, prompts, or trigger strings.

## Common utility chains

Background replacement:

```text
source image -> sam-hq mask -> invert or refine mask -> new background -> composite-image
```

Social resize:

```text
master asset -> resize 1:1 -> resize 9:16 -> compress-image
```

Subtitled video:

```text
video -> auto-subtitle -> optional setpts-video -> final download
```

Product catalog:

```text
product image -> segment -> composite clean background -> image-grid -> compress
```
