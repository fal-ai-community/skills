---
name: game-asset-production
description: "Produce an engine-ready 2D game asset pack with fal. Deliver transparent sprites, sliced animation frames, backgrounds and an atlas with measured frame geometry."
---

# Game asset production

Deliver usable game assets rather than an unsliced illustration of a sprite sheet.

## Asset contract and production

Collect the engine, logical pixel size, palette, facing direction, animation states,
frame counts, FPS, pivot and atlas format. Reuse supplied choices. Read `fal-gamedev`
for generation recipes and `character-design` for a stable identity anchor.

1. Define a manifest per animation: frame size, count, order, FPS, pivot and loop.
   Choose a small first pack from the brief; do not multiply states without need.
2. Generate one approved character silhouette. Use a live text/image endpoint;
   `fal-ai/flux-2/klein/9b` is a candidate for drafts, not a guarantee of pixel accuracy.
3. Build each state from the approved reference through an edit model such as
   `openai/gpt-image-2/edit`. Specify orthographic view, a fixed baseline, repeated
   cell size, no labels and the exact frame count.
4. Remove backgrounds when needed with a verified endpoint such as
   `fal-ai/bria/background/remove` (`image_url`). Use this endpoint synchronously.
   Inspect alpha edges; background removal can destroy small details.
5. Slice using measured cell boundaries. Check width = columns × cell width and
   height = rows × cell height. Do not silently pad an incorrectly generated grid.
   Correct alignment locally or regenerate only the failed state within budget.
6. Keep nearest-neighbor resampling for pixel art. Export transparent PNG frames,
   atlas texture and JSON frame rectangles; include pivot, FPS and loop metadata.
7. Produce backgrounds as separate parallax layers only if requested. Keep the
   light direction, horizon and palette consistent with the character.

## Acceptance and delivery

Inspect animation playback and an alpha checkerboard at native size and magnified.
Measure frame dimensions, frame count, alpha coverage, atlas bounds and consistent
foot contact. Reject duplicate frozen frames in a requested moving state. Check
atlas loading in the target engine or a small preview. State engine checks not run.
Deliver source sheets, sliced frames, atlas, preview and manifest with filenames
ready for import. A plausible sheet alone does not pass.

## Execute and recover

Read the `genmedia` skill for terminal execution, or `fal-media` for connected MCP
execution. Read only the named production references needed by this brief.
Use current published routing or discover a candidate. Verify exact endpoints,
input schemas, output shape and price units before constructing inputs. Preserve
an explicitly named model. Candidate IDs below were schema-checked on 2026-11-05;
availability and price can change.

For terminal agents, copy [the example plan](assets/plan.json) into the project.
Replace every `REPLACE_` value with the actual prompt, URL or locale. Inspect each
stage's live schema and price, then run the shared helper from the installed
`genmedia` skill (locate its installation path; do not assume the current directory):

```sh
python3 /path/to/genmedia/scripts/run_plan.py plan.json --stage hero
python3 /path/to/genmedia/scripts/run_plan.py plan.json --stage hero --execute --state ./production-state
python3 /path/to/genmedia/scripts/run_plan.py plan.json --stage hero --poll --state ./production-state
```

The first command prints a dry run. Use the actual stage ID from the plan.
`--execute` spends on that stage only. The helper records schema, pricing and the
submission response. It refuses a second submission for the same stage. `--poll`
checks the saved request and downloads its output. A failed or uncertain submit
needs manual reconciliation, not a blind retry. Copy verified output URLs into
later stage inputs after visual review. Never use a local path where a URL is required.

For MCP hosts, perform the same stages with current tool contracts: use
`recommend_model` unless the user names an endpoint; use its returned input contract
and `next_call` when provided. Otherwise inspect the schema. Use `run_model` for
bounded operations, or `submit_job`, `check_job` and `get_job_result` for queued work.
Record the request ID immediately. Do not install genmedia merely to follow a CLI example.

Keep a project manifest with source assets, endpoint, inputs, request ID, output URL,
local file, dimensions/duration, cost estimate, and QA findings for every stage.
Produce only the requested variants within the existing budget. Return observed
failures and missing capabilities; do not substitute a plan for a requested artifact.
