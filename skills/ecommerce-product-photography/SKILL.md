---
name: ecommerce-product-photography
description: "Create a consistent fal e-commerce product photo set from real SKU references. Deliver verified hero, detail and lifestyle images with accurate packaging and channel exports."
---

# E-commerce product photography

Make a consistent product photo set with the real SKU as the identity source.

## Product lock and production

Collect SKU IDs, front/back/detail references, dimensions, material, true color,
logo/label assets, shot list, channel requirements and budget. Separate product
identity edits from deterministic crop, color and export corrections.

1. Map each output to a SKU and reference. Never invent a back view, ingredient
   label, certification or physical feature absent from the supplied sources.
2. Produce one hero against a suitable background with a currently accessible
   reference-edit model. Inspect its reference fields and image size contract first.
3. Compare the result with the source: silhouette, proportions, cap, seams, material,
   label spelling and logo placement. Preserve true color rather than an attractive recolor.
4. Derive detail and lifestyle scenes from the approved reference. Keep scale and
   light direction plausible. Treat hands, reflections and transparent packaging as
   separate fidelity risks. Do not scale up a false product detail for a close-up.
5. For pure white/cutout delivery, use a current matting operation where needed
   and deterministic composition. Keep contact
   shadows only when the channel permits them. Check current marketplace image rules.
6. Export requested dimensions, color space and format. Keep a clean master before
   channel crops. Apply the same crop margins and visual product scale across SKUs.

## Acceptance and delivery

Deliver per-SKU folders, hero/detail/lifestyle files, a contact sheet and manifest.
Measure dimensions, background/alpha, crop margins and file sizes. Inspect every
label and product feature against the real reference. Reject drift before batch
expansion. Identify any SKU or view that lacks a sufficient reference.

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
