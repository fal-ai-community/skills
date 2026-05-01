# Node rules

## Planner node

- Produces the workflow graph, shot table, or variant matrix.
- Output must be structured enough to execute without interpretation drift.
- Include node IDs, dependencies, intended endpoint role, inputs, and expected
  outputs.
- Keep creative planning separate from executable parameters.

## Extractor node

- Converts planner output into one narrow prompt, caption, subtitle, filename,
  or parameter set.
- Use deterministic wording and low creativity.
- Prefer split or merge text utilities when the task is simple string
  manipulation.

## Image generation node

- Choose the endpoint from `model-routing` first.
- Verify it with `genmedia models --endpoint_id <endpoint_id> --json`.
- Use free-text `genmedia models "<query>" --json` only when the routed
  endpoint is missing or the role is not covered.
- Inspect schema before setting aspect ratio, image size, count, seed, or
  negative prompt.
- For grids, describe layout and panel count exactly.
- For product or character continuity, prefer reference or edit workflows.

## Image editing node

- Upload every source image first.
- Change one thing per pass.
- State preservation rules first, edit instruction second.
- If multiple references are used, assign roles: identity, style, background,
  product, pose, texture.

## Image-to-video node

- Prefer image-to-video when a reference frame exists.
- Use short motion prompts, usually 15 to 35 words.
- Specify subject motion, camera motion, and ambient motion.
- Avoid describing static composition again unless the schema or model needs it.
- Run async and download via `genmedia status`.

## Utility node

- Utility work should be deterministic: resize, crop, grid, composite, overlay,
  subtitle, join audio and video, speed change, split, merge, compress.
- Always inspect schema because utility endpoints often have exact field names.
- Use generated result URLs for downstream inputs when available.
- Use `genmedia upload` for local intermediate files before passing them into
  another endpoint.

## QA node

Use a manual or vision-based check after high-risk nodes:

- Identity preserved.
- Product logo and packaging preserved.
- Crop and aspect ratio correct.
- Text is absent, intentional, or added by a text utility.
- Audio and subtitle timing match.
- Clip order and duration match the plan.

## Manifest node

Return a compact manifest at the end:

```json
{
  "node_id": "shot_03_i2v",
  "role": "image_to_video",
  "endpoint_id": "selected endpoint",
  "request_id": "fal request id",
  "inputs": ["source url or local path"],
  "outputs": ["result media url"],
  "downloaded_files": ["local file path"],
  "status": "accepted | retried | rejected",
  "notes": "short defect or continuity note"
}
```

Keep manifests factual. Do not include promotional copy.
