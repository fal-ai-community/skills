---
name: game-asset-production
description: "Produce an engine-ready 2D game asset pack with fal. Deliver transparent sprites, sliced animation frames, backgrounds and an atlas with measured frame geometry."
---

# Game asset production

Deliver usable game assets rather than an unsliced illustration of a sprite sheet.

## Asset contract and production

Collect the engine, logical pixel size, palette, facing direction, animation states,
frame counts, FPS, pivot and atlas format. Reuse supplied choices. Write a stable
character identity anchor and carry it through every state.

1. Define a manifest per animation: frame size, count, order, FPS, pivot and loop.
   Choose a small first pack from the brief; do not multiply states without need.
2. Generate one approved character silhouette with a currently accessible image
   model. Inspect native pixel dimensions and style before treating it as a master.
3. Build each state from the approved reference through a current reference-edit
   model. Specify orthographic view, a fixed baseline, repeated
   cell size, no labels and the exact frame count.
4. Remove backgrounds when needed with a currently supported matting operation.
   Use the execution mode and inputs its tool contract supports. Inspect alpha
   edges; background removal can destroy small details.
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

## Execution and specialist guidance

Use the installed `fal-media` skill for current model discovery, input contracts,
prices, native MCP execution and request recovery. Preserve the user's selected
provider, model, inputs, output count and spending limits.

The production checks above work without another domain skill. If a specialist
stage needs more guidance, follow `fal-media` to retrieve the relevant published
guide and only its needed version-pinned references. Reuse guidance already read.
If retrieval is unavailable, retain these local checks and current tool contracts;
report any stage that cannot be completed or verified. Do not invent a model,
privileged host tool or unavailable renderer to fill the gap.

Keep a manifest of sources, endpoint, actual inputs, request ID, result URL, local
file and QA findings. Inspect delivered artifacts and report unverified checks.

## Terminal execution

For a terminal-only workflow, read the [genmedia production-plan guide](../genmedia/references/production-plans.md)
and copy this skill's [example stage plan](assets/plan.json). The guide describes
explicit submission, state files and recovery. These examples are optional CLI
resources; connected MCP hosts use native fal tools.
