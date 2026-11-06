---
name: ecommerce-product-photography
description: "Create a consistent fal e-commerce product photo set from real SKU references. Deliver verified hero, detail and lifestyle images with accurate packaging and channel exports."
---

# E-commerce product photography

Make a consistent product photo set with the real SKU as the identity source.

## Product lock and production

Collect SKU IDs, front/back/detail references, dimensions, material, true color,
logo/label assets, shot list, channel requirements and budget. Read `commercial`
for fidelity and `photo-editing` for deterministic corrections.

1. Map each output to a SKU and reference. Never invent a back view, ingredient
   label, certification or physical feature absent from the supplied sources.
2. Produce one hero against a suitable background with a reference edit model.
   Candidates include `openai/gpt-image-2/edit` and `google/nano-banana-2.1/edit`.
   Inspect the actual reference fields and image size contract first.
3. Compare the result with the source: silhouette, proportions, cap, seams, material,
   label spelling and logo placement. Preserve true color rather than an attractive recolor.
4. Derive detail and lifestyle scenes from the approved reference. Keep scale and
   light direction plausible. Treat hands, reflections and transparent packaging as
   separate fidelity risks. Do not scale up a false product detail for a close-up.
5. For pure white/cutout delivery, use verified background removal where needed
   (`fal-ai/bria/background/remove`) and deterministic composition. Keep contact
   shadows only when the channel permits them. Check current marketplace image rules.
6. Export requested dimensions, color space and format. Keep a clean master before
   channel crops. Apply the same crop margins and visual product scale across SKUs.

## Acceptance and delivery

Deliver per-SKU folders, hero/detail/lifestyle files, a contact sheet and manifest.
Measure dimensions, background/alpha, crop margins and file sizes. Inspect every
label and product feature against the real reference. Reject drift before batch
expansion. Identify any SKU or view that lacks a sufficient reference.

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
