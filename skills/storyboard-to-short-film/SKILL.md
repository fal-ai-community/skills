---
name: storyboard-to-short-film
description: "Turn a storyboard or shot list into a finished fal short film. Preserve character and scene continuity, render each shot, assemble picture and sound, and verify the final cut."
---

# Storyboard to short film

Convert supplied boards or a shot list into a rendered short film and editable shot package.

## Lock and produce

Record the runtime, aspect ratio, boards, shot order, character/product references,
dialogue, audio treatment and budget. Define continuity anchors, shot timing and
physical action before choosing models.

1. Create a timed shot table: shot ID, source board, duration, action, camera,
   continuity anchor, sound and exact overlay copy. Sum durations against runtime.
2. Establish approved character and location anchors. Prefer image/reference inputs
   over unrelated text rerolls. A storyboard contact sheet is not a clean motion input;
   extract each shot into its own image and inspect it.
3. Resolve a live image-to-video or reference-to-video model for each shot. Use its
   actual input contract, including required prompt controls. Check supported
   duration and resolution before submitting.
4. Queue one shot at a time for the initial look test. Record IDs and review actual
   motion, continuity and scene content before continuing the authorized shot list.
   Keep failed shots isolated. Do not add shots to fill a timing mistake.
5. Trim and assemble the approved clips with a consistent timeline. Use a verified
   local editor/renderer, or an available compositing tool. If neither exists, report
   that final assembly is blocked and deliver the reviewed shot package.
6. Add dialogue, music and effects only as requested. Keep voices pinned. Measure speech length; do not fit speech by cutting words.
   Keep picture, voice, music and effects stems for a later remix.
7. Compose exact titles and logos deterministically. Use measured speech timestamps
   for captions. Render the final cut, then inspect the actual exported file.

## Acceptance and delivery

Watch every transition and listen to the mix. Measure total runtime, resolution,
frame rate, audio peaks and speech placement. Verify shot count and order, legible
copy, continuity and correct final-frame hold. Deliver the film, clean cut, stems,
shot table, sources and manifest. Flag any review that the host cannot perform.

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
