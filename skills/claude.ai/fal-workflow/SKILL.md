---
name: fal-workflow
description: Generate production-ready fal.ai workflow JSON files. Use when user requests "create workflow", "chain models", "multi-step generation", "image to video pipeline", or complex AI generation pipelines.
metadata:
  author: fal-ai
  version: "3.0.0"
---

# fal.ai Workflow Generator

Generate **100% working, production-ready fal.ai workflow JSON files**. Workflows chain multiple AI models together for complex generation pipelines.

**References:**
- [Model Reference](references/MODELS.md) - Detailed model configurations
- [Common Patterns](references/PATTERNS.md) - Reusable workflow patterns
- [Code Examples](references/EXAMPLES.md) - Code snippets and partial examples

**Troubleshooting Reference:**
- [Complete Workflows](references/WORKFLOWS.md) - Working JSON examples for debugging (use ONLY when user reports errors)

---

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

Use `search-models.sh` or `search_models` MCP tool to discover current models. See `references/MODELS.md` for workflow code templates.

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

## Usage

### Using Script

```bash
bash /mnt/skills/user/fal-workflow/scripts/create-workflow.sh \
  --name "my-workflow" \
  --title "My Workflow Title" \
  --nodes '[...]' \
  --outputs '{...}'
```

### Using MCP Tool

```javascript
mcp__fal-ai__create-workflow({
  smartMode: true,
  intent: "Generate a story with LLM, create an illustration, then animate it"
})
```

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
