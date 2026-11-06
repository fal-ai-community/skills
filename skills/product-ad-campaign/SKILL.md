---
name: product-ad-campaign
description: "Produce a complete fal product ad campaign from a brief and product references. Deliver reviewed hero art, channel variants, short motion ads and a reusable asset manifest."
---

# Product ad campaign

Turn one product brief into a consistent campaign asset package.

## Brief and production

Capture the product reference, original logo, approved copy, audience, offer,
channels, sizes, variant count and spending limit. Infer supplied values; ask only
for a missing input that blocks production. Never invent claims, discounts or testimonials.

1. Build a small matrix of hook × product benefit × channel. Name each deliverable
   and its dimensions. Use `marketing` for creative patterns and `commercial` for product fidelity.
2. Lock one hero composition against the real product reference. A current candidate
   is `openai/gpt-image-2/edit`; inspect `prompt` and `image_urls` before use.
3. Review packaging, silhouette, colors, hands and product scale before variants.
   Use edit/reference inputs from the approved hero. Keep the product consistent;
   change only the planned hook, framing or backdrop.
4. Place original logos and exact copy with deterministic composition when model
   text or logos drift. Read `branded-graphics`; inspect the final exported image.
5. If motion is requested, animate approved product art with a verified image-to-video
   endpoint such as `minimax/h3-max/image-to-video`. Explicitly resolve its required
   `prompt_expansion_mode` from the schema. Generate one short test before a batch.
6. Export each channel size without cutting the product, logo or CTA. Check current
   platform safe areas. Keep the editable composition, clean image and motion stems.

## Acceptance and delivery

Deliver a contact sheet, named final files, copy matrix and manifest. Check each
requested size, exact copy, actual product fidelity and motion continuity. Record
unverified platform specs. Do not publish ads, upload campaigns or make spending
commitments beyond the user's brief.

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
