---
name: fal-media
description: "Generate or process media with connected fal MCP tools. Use for Fal model selection, schemas, pricing, uploads and job recovery; preserve an explicitly chosen provider."
---

# fal.ai Media

Route media generation and processing through the fal.ai MCP tools exposed by
this plugin. This is the provider-level entry point; load a more specialized
Fal skill when the task needs its production guidance.

## Provider And Model Routing

- Preserve an explicitly requested provider. When the user names Fal, keep the
  operation on Fal. When the user names another provider, do not invoke Fal.
- For a named model, search Fal's live catalog and verify its exact canonical
  endpoint. Prefer an exact match over a similarly named model exposed by an
  intermediary. Do not silently substitute a different model or provider.
- When no model is specified, call `recommend_model` for a current candidate,
  then judge the result against the requested artifact and constraints.
- Inspect the selected endpoint schema before constructing its input. Check
  pricing when duration, resolution, batching, training, audio, video, or 3D
  can materially affect cost.

## Execution

- Use `run_model` for bounded image and utility operations.
- Use `submit_job` for video, audio, 3D, training, or other long-running work;
  poll the same request with `check_job`, then fetch it with `get_job_result`.
- Upload local inputs before generation when the endpoint requires a URL.
- Preserve continuity with image-to-video, reference-to-video, or frame
  extraction when an earlier result should anchor the next shot.
- Return the endpoint ID, request ID, output URL, and material limitations.

## Related Skills

- Load `model-routing` for model selection beyond a direct exact match.
- Load `fal-models-catalog` for broader family or modality comparisons.
- Load `fal-prompting` after selecting an endpoint that needs family-specific
  prompt construction.
- Load `fal-workflow` for model chains, batches, or dependent generation steps.
