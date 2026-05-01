---
name: fal-workflow
description: Author and execute multi-step media pipelines on fal.ai. Two modes: (A) declarative workflow JSON files for the fal.ai workflow runtime ("create workflow", "chain models", "image to video pipeline"); (B) imperative genmedia CLI orchestration when scripting locally ("design pipeline", "fan-out generation", "frame bridging", "narrated video", "dataset generation").
metadata:
 author: fal-ai
 version: "4.0.0"
---

# fal.ai Workflows: Two Modes

> **Runtime:** Two modes. Mode A authors `.json` files for the fal.ai workflow runtime (executed in the cloud, no local CLI needed). Mode B drives the [genmedia CLI](https://github.com/fal-ai-community/genmedia-cli) for local orchestration. See the `genmedia` skill for Mode B command syntax; run `genmedia init` once if not yet installed.

This skill covers two complementary ways to build multi-step media pipelines on fal.ai. They share endpoints and concepts but differ in deliverable.

| Mode | Deliverable | When to use |
|------|-------------|-------------|
| **A. Workflow JSON** | A portable `.json` file the fal.ai workflow runtime executes | The user wants a reusable, shareable workflow asset; the pipeline graph is fixed at design time |
| **B. genmedia CLI orchestration** | A sequence of `genmedia run / status / upload` calls (often scripted) | Local scripting, exploratory pipelines, dataset jobs, branching logic, or pipelines that need conditional steps |

If unsure: prefer Mode A when the result is a deliverable for someone else to run; Mode B when you are running it yourself or steps need runtime decisions.

---

## Mode A: Workflow JSON authoring

Generate **100% working, production-ready fal.ai workflow JSON files**. Workflows chain multiple AI models together via a declarative graph.

**JSON-mode references:**
- [MODELS.md](references/MODELS.md), model configurations for JSON nodes
- [PATTERNS.md](references/PATTERNS.md), reusable JSON workflow patterns
- [EXAMPLES.md](references/EXAMPLES.md), code snippets and partial examples
- [WORKFLOWS.md](references/WORKFLOWS.md), full JSON workflows (debugging reference; use only when user reports errors)

## Mode B: genmedia CLI orchestration

Plan and execute a sequence of `genmedia` calls with clear inputs, outputs, dependencies, and quality checks. Use this when a single model call is not enough and the orchestration happens in your shell, not on fal.ai.

**CLI-mode references:**
- [pipeline-patterns.md](references/pipeline-patterns.md), fan-out, sequential composition, frame bridging, multi-modal assembly, variation matrices
- [node-rules.md](references/node-rules.md), per-role rules (planner / generator / editor / utility / QA / manifest)
- [utility-endpoints.md](references/utility-endpoints.md), utility endpoint catalog (resize, composite, mask, audio, subtitle, etc.)
- [recipes.md](references/recipes.md), end-to-end recipes (cinematic video, product campaign, character continuity, narrated documentary, dataset, social batch)

For default endpoint choices in Mode B, consult `fal-models-catalog`. Always run `genmedia schema <endpoint_id> --json` before executing and `genmedia pricing <endpoint_id> --json` when cost matters.

---

# Mode A: Workflow JSON authoring (continued)

## Core Architecture

### Valid Node Types

⚠️ **ONLY TWO VALID NODE TYPES EXIST:**

| Type | Purpose |
|------|---------|
| `"run"` | Execute a model/app |
| `"display"` | Output results to user |

**❌ INVALID:** `type: "input"` - This does NOT exist! Input is defined ONLY in `schema.input`.

### Minimal Working Example

```json
{
 "name": "my-workflow",
 "title": "My Workflow",
 "contents": {
 "name": "workflow",
 "nodes": {
 "output": {
 "type": "display",
 "id": "output",
 "depends": ["node-image"],
 "input": {},
 "fields": { "image": "$node-image.images.0.url" }
 },
 "node-image": {
 "type": "run",
 "id": "node-image",
 "depends": ["input"],
 "app": "fal-ai/flux/dev",
 "input": { "prompt": "$input.prompt" }
 }
 },
 "output": { "image": "$node-image.images.0.url" },
 "schema": {
 "input": {
 "prompt": {
 "name": "prompt",
 "label": "Prompt",
 "type": "string",
 "required": true,
 "modelId": "node-image"
 }
 },
 "output": {
 "image": { "name": "image", "label": "Generated Image", "type": "string" }
 }
 },
 "version": "1",
 "metadata": {
 "input": { "position": { "x": 0, "y": 0 } },
 "description": "Simple text to image workflow"
 }
 },
 "is_public": true,
 "user_id": "",
 "user_nickname": "",
 "created_at": ""
}
```

### Reference Syntax

| Reference | Use Case | Example |
|-----------|----------|---------|
| `$input.field` | Input value | `$input.prompt` |
| `$node.output` | LLM text output | `$node-llm.output` |
| `$node.images.0.url` | First image URL | `$node-img.images.0.url` |
| `$node.image.url` | Single image URL | `$node-upscale.image.url` |
| `$node.video.url` | Video URL | `$node-vid.video.url` |
| `$node.audio_file.url` | Audio URL | `$node-music.audio_file.url` |
| `$node.frame.url` | Extracted frame | `$node-extract.frame.url` |

### CRITICAL: No String Interpolation

**⚠️ NEVER mix text with variables! Variable MUST be the ENTIRE value.**

```json
// ❌ WRONG - WILL BREAK
"prompt": "Create image of $input.subject in $input.style"

// ✅ CORRECT - Variable is the ENTIRE value
"prompt": "$input.prompt"
"prompt": "$node-llm.output"
```

**To combine values:** Use `fal-ai/text-concat` or `fal-ai/workflow-utilities/merge-text`. See [Model Reference](references/MODELS.md#text-utilities-critical-for-combining-values).

---

## Critical Rules

### C1: Dependencies Must Match References

```json
// ❌ WRONG
"node-b": {
 "depends": [],
 "input": { "data": "$node-a.output" }
}

// ✅ CORRECT
"node-b": {
 "depends": ["node-a"],
 "input": { "data": "$node-a.output" }
}
```

### C2: ID Must Match Object Key

```json
// ❌ WRONG
"my-node": { "id": "different-id" }

// ✅ CORRECT
"my-node": { "id": "my-node" }
```

### C3: Use Correct LLM Type

- `openrouter/router` → Text only, no image_urls
- `openrouter/router/vision` → ONLY when analyzing images

### C4: Schema modelId Required

```json
"schema": {
 "input": {
 "field": { "modelId": "first-consuming-node" }
 }
}
```

### C5: Output Depends on All Referenced Nodes

```json
"output": {
 "depends": ["node-a", "node-b", "node-c"],
 "fields": {
 "a": "$node-a.video",
 "b": "$node-b.images.0.url"
 }
}
```

---

---

## Quick Reference Card

### Output References

| Model Type | Output Reference |
|------------|------------------|
| LLM | `$node.output` |
| Text Concat | `$node.results` |
| Merge Text | `$node.text` |
| Image Gen (array) | `$node.images.0.url` |
| Image Process (single) | `$node.image.url` |
| Video | `$node.video.url` |
| Music | `$node.audio_file.url` |
| Frame Extract | `$node.frame.url` |

Use `genmedia models "<query>" --json` or `genmedia models --category <cat> --json` to discover current models. See `references/MODELS.md` for workflow code templates.

---

## Input Schema

```json
"schema": {
 "input": {
 "text_field": {
 "name": "text_field",
 "label": "Display Label",
 "type": "string",
 "description": "Help text",
 "required": true,
 "modelId": "consuming-node"
 },
 "image_urls": {
 "name": "image_urls",
 "type": { "kind": "list", "elementType": "string" },
 "required": true,
 "modelId": "node-id"
 }
 }
}
```

---

## Pre-Output Checklist

Before outputting any workflow, verify:

- [ ] **⚠️ All nodes have `type: "run"` or `type: "display"` ONLY (NO `type: "input"`!)**
- [ ] **⚠️ No string interpolation - variable MUST be ENTIRE value**
- [ ] Every `$node.xxx` has matching `depends` entry
- [ ] Every node `id` matches object key
- [ ] Input schema has `modelId` for each field
- [ ] Output depends on ALL referenced nodes
- [ ] Correct LLM type (router vs router/vision)

---

## Authoring a workflow JSON

Author the JSON file by hand following the structure shown above. There is no script wrapper; the agent writes the file directly. Validate before delivery:

1. Every node id matches its object key.
2. Every `$node.xxx` reference appears in `depends`.
3. No string interpolation; variables are entire values.
4. Schema input has `modelId` for each field.
5. Output node `depends` includes every node it references.

For each model used, inspect the schema first:

```bash
genmedia schema <endpoint_id> --json
```

Then write the corresponding `input` block in the workflow JSON.

---

## Troubleshooting

### Invalid Node Type Error (MOST COMMON)
```
Error: unexpected value; permitted: 'run', 'display', field required
```
**Cause:** You created a node with `type: "input"` which does NOT exist.
**Solution:** Remove ANY node with `type: "input"`. Define input fields ONLY in `schema.input`.

### Dependency Error
```
Error: Node references $node-x but doesn't depend on it
```
**Solution:** Add the referenced node to the `depends` array.

### ID Mismatch Error
```
Error: Node key "my-node" doesn't match id "different-id"
```
**Solution:** Ensure the object key matches the `id` field exactly.

### LLM Vision Error
```
Error: image_urls provided but using text-only router
```
**Solution:** Switch to `openrouter/router/vision` when analyzing images.

---

## Finding Model Schemas

Every model's input/output schema:
```
https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=[endpoint_id]
```

Example:
```
https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=fal-ai/nano-banana-pro
```

---

# Mode B: genmedia CLI orchestration

When the deliverable is local execution rather than a portable JSON file, plan a pipeline of `genmedia` calls.

## Inputs to collect

Ask only for missing information that changes the pipeline:

- Final deliverable: image set, video, clips, audio, subtitles, dataset, social batch, product campaign, storyboard, style exploration.
- Source assets: product images, character references, first frames, video, audio, logo, transcript, brand guide.
- Runtime limits: quality target, cost sensitivity, number of variants, duration, aspect ratios, deadline.
- Continuity requirements: product identity, character face, scene layout, voice, color grade.
- Model preference: ask only when quality/speed/cost tradeoffs are not clear from the brief.

## Core CLI workflow

1. Write a short pipeline graph before running anything.

 ```text
 input assets -> planner -> generation nodes -> utility nodes -> QA -> final outputs
 ```

2. Resolve endpoints for each role. Check known endpoint IDs first via `fal-models-catalog`.

 ```bash
 genmedia models --endpoint_id <endpoint_id> --json
 ```

 Use text search only as fallback discovery for roles not covered:

 ```bash
 genmedia models "image generation product photography" --json
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
 ```

5. Run each node with JSON output. Use `--async` for slow generation; poll with `genmedia status`.

 ```bash
 genmedia run <endpoint_id> --<field> "<value>" --json
 genmedia run <endpoint_id> --<field> "<value>" --async --json
 genmedia status <endpoint_id> <request_id> --download "./outputs/workflow/{request_id}_{index}.{ext}" --json
 ```

6. For downstream nodes, pass the media URL from the previous result. Only upload local intermediate files when no URL is available.

7. Download final assets with templates that cannot collide:

 ```bash
 --download "./outputs/workflow/{request_id}_{index}.{ext}"
 ```

8. Return a compact manifest (see [node-rules.md](references/node-rules.md) for the manifest schema).

## CLI pipeline rules

- One node, one transformation.
- Fan out independent generation / crop / upscale / subtitle / variation lanes.
- Sequential chains only when node B genuinely needs node A output.
- Prefer reference / edit / image-to-video over independent text-only generations when continuity matters.
- Use utility endpoints for deterministic work (crop, resize, grid, composite, audio merge, subtitle, speed change, compression).
- Record endpoint, schema-relevant parameters, request ID, and output path for every node.
- On 422 errors: read `validation_errors`, re-inspect schema, fix the exact field.

## CLI quality gate

Before returning, verify:

- The pipeline graph matches the requested deliverable.
- No generation model was chosen from memory alone.
- All local source files were uploaded before use.
- Final files were saved through `--download`.
- Utility endpoints used exact schema fields.
- Continuity anchors were repeated where identity or product fidelity matters.
- Each node output is either accepted, retried, or marked with a defect.

If the workflow becomes too complex, stop expanding and ask the user to choose between faster iteration, higher fidelity, or broader variation.
