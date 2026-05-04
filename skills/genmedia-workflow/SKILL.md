---
name: genmedia-workflow
description: >
  Design and execute multi-step media workflows with genmedia. Use this for
  pipelines that combine planning, generation, editing, image or video
  utilities, audio, subtitles, batching, and final delivery manifests.
---

# Genmedia workflow production

> **Runtime:** All endpoint calls run via the [genmedia CLI](https://github.com/fal-ai-community/genmedia-cli). See the `genmedia` skill for command syntax; run `genmedia init` once if not yet installed.

Use this skill when a single model call is not enough. A workflow is a planned
sequence of genmedia calls with clear inputs, outputs, dependencies, and
quality checks.

Load references as needed:

- `references/pipeline-patterns.md`
- `references/node-rules.md`
- `references/utility-endpoints.md`
- `references/recipes.md`
- `model-routing` for creative model defaults

Use `model-routing` for default creative model choices. Still inspect schemas,
check pricing when cost matters, and use exact endpoint fields.

## Inputs to collect

Ask only for missing information that changes the pipeline:

- Final deliverable: image set, video, clips, audio, subtitles, dataset, social
  batch, product campaign, storyboard, style exploration.
- Source assets: product images, character references, first frames, video,
  audio, logo, transcript, brand guide.
- Runtime limits: quality target, cost sensitivity, number of variants,
  duration, aspect ratios, deadline.
- Continuity requirements: product identity, character face, scene layout,
  voice, color grade.
- Model preference: ask the user only when quality, speed, cost, or audio
  tradeoffs are not clear from the brief.

## Core workflow

1. Write a short pipeline graph before running anything.

   ```text
   input assets -> planner -> generation nodes -> utility nodes -> QA -> final outputs
   ```

2. Resolve endpoints for each role. Check known endpoint IDs first.

   ```bash
   genmedia models --endpoint_id openai/gpt-image-2 --json
   genmedia models --endpoint_id fal-ai/nano-banana-pro/edit --json
   genmedia models --endpoint_id bytedance/seedance-2.0/image-to-video --json
   genmedia models --endpoint_id xai/grok-imagine-video/image-to-video --json
   genmedia models --endpoint_id veed/fabric-1.0 --json
   ```

   Use text search only as fallback discovery for roles not covered by
   `model-routing` or the utility reference:

   ```bash
   genmedia models "image generation product photography" --json
   genmedia models "image editing reference preservation" --json
   genmedia models "image to video" --json
   genmedia models "subtitle video utility" --json
   genmedia docs "fal.ai workflow utility endpoints" --json
   ```

3. Inspect every endpoint before use.

   ```bash
   genmedia schema <endpoint_id> --json
   genmedia pricing <endpoint_id> --json
   ```

4. Upload local files once and reuse returned URLs.

   ```bash
   genmedia upload ./input.png --json
   genmedia upload ./voiceover.wav --json
   ```

5. Run each node with JSON output. Use async for slow generation.

   ```bash
   genmedia run <endpoint_id> --<field> "<value>" --json
   genmedia run <endpoint_id> --<field> "<value>" --async --json
   genmedia status <endpoint_id> <request_id> --download "./outputs/workflow/{request_id}_{index}.{ext}" --json
   ```

6. For downstream nodes, pass the media URL from the previous `result` when it
   is available. If you only have a local file path, upload it first.

7. Download final assets with templates that cannot collide.

   ```bash
   --download "./outputs/workflow/{request_id}_{index}.{ext}"
   ```

8. Return a compact manifest.

   ```json
   {
     "goal": "short deliverable description",
     "nodes": [
       {
         "id": "shot_01",
         "role": "image_to_video",
         "endpoint_id": "...",
         "request_id": "...",
         "input_urls": ["..."],
         "output_urls": ["..."],
         "downloaded_files": ["..."],
         "notes": "continuity or defect notes"
       }
     ],
     "final_files": ["..."]
   }
   ```

## Pipeline rules

- Keep one node responsible for one clear transformation.
- Fan out independent generation, crop, upscale, subtitle, or variation nodes.
- Keep sequential chains only when node B needs node A output.
- For consistency, prefer reference/edit or image-to-video over independent
  text-only generations.
- For default creative model choices, follow `model-routing` unless the user
  names a model.
- Use utility endpoints for deterministic work: crop, resize, grid, composite,
  audio merge, subtitle, speed change, compression.
- Record endpoint, schema-relevant parameters, request ID, and output path for
  every node.
- If a 422 error occurs, read `validation_errors`, inspect schema again, then
  fix the exact field.

## Quality gate

Before returning, verify:

- The pipeline graph matches the requested deliverable.
- No generation model was chosen from memory alone.
- All local source files were uploaded before use.
- Final files were saved through `--download`.
- Utility endpoints used exact schema fields.
- Continuity anchors were repeated where identity or product fidelity matters.
- Each node output is either accepted, retried, or marked with a defect.

If the workflow becomes too complex, stop expanding and ask the user to choose
between faster iteration, higher fidelity, or broader variation.
