---
name: storyboard-to-short-film
description: "Turn a storyboard or shot list into a finished fal short film. Preserve character and scene continuity, render each shot, assemble picture and sound, and verify the final cut."
---

# Storyboard to short film

Convert supplied boards or a shot list into a rendered short film and editable shot package.

## Lock and produce

Record the runtime, aspect ratio, boards, shot order, character/product references,
dialogue, audio treatment and budget. Read `storytelling` for continuity,
`fal-script-writer` for timing and `fal-shot-craft` for one-shot action.

1. Create a timed shot table: shot ID, source board, duration, action, camera,
   continuity anchor, sound and exact overlay copy. Sum durations against runtime.
2. Establish approved character and location anchors. Prefer image/reference inputs
   over unrelated text rerolls. A storyboard contact sheet is not a clean motion input;
   extract each shot into its own image and inspect it.
3. Resolve a live image-to-video or reference-to-video model for each shot. A candidate
   is `minimax/h3-max/image-to-video`, with `prompt_expansion_mode` explicitly set
   from its live schema. Check supported duration and resolution before submitting.
4. Queue one shot at a time for the initial look test. Record IDs and review actual
   motion, continuity and scene content before continuing the authorized shot list.
   Keep failed shots isolated. Do not add shots to fill a timing mistake.
5. Trim and assemble the approved clips with a consistent timeline. Use a verified
   local editor/renderer, or an available compositing tool. If neither exists, report
   that final assembly is blocked and deliver the reviewed shot package.
6. Add dialogue, music and effects only as requested. Read `fal-audio-generation`.
   Keep voices pinned. Measure speech length; do not fit speech by cutting words.
   Keep picture, voice, music and effects stems for a later remix.
7. Compose exact titles and logos deterministically. Use measured speech timestamps
   for captions. Render the final cut, then inspect the actual exported file.

## Acceptance and delivery

Watch every transition and listen to the mix. Measure total runtime, resolution,
frame rate, audio peaks and speech placement. Verify shot count and order, legible
copy, continuity and correct final-frame hold. Deliver the film, clean cut, stems,
shot table, sources and manifest. Flag any review that the host cannot perform.

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
