---
name: fal-controlnet-lock
description: >
  Author fal.ai workflow JSON and genmedia CLI pipelines that lock image composition using ControlNet.
  Covers canny-edge, depth, pose, and tile control types; preprocessor-to-ControlNet generation
  chains; multi-controlnet weighting; and style-transfer while preserving spatial structure.
  Trigger for "controlnet", "composition lock", "lock the layout", "keep the pose", "same structure
  different style", "restyle with controlnet", "edge-guided generation", "depth-conditioned
  generation", "lock composition", "preserve structure", "structural restyle".
metadata:
 author: fal-ai
 version: "1.0.0"
---

# fal.ai ControlNet Composition Lock

**ControlNet composition lock** preserves the spatial layout, edges, depth, or pose of a reference
image while generating entirely new content from a text prompt. Use it when you want: the same
scene framing with a different art style, a character's pose reused in a new illustration, or a
room's structure rebuilt in a fantasy setting.

## Core Concept

```
[Reference Image] → [Preprocessor]  → [Control Signal]
                                              ↓
                    [Text Prompt]  → [ControlNet Model] → [Locked-Composition Output]
```

The **preprocessor** extracts a spatial signal (edge map, depth map, skeleton) from the reference.
The **ControlNet model** uses that signal as a structural constraint during diffusion — the prompt
drives style and content; the control signal drives layout and composition.

---

## Two Workflow Modes

| Mode | Deliverable | When to use |
|------|-------------|-------------|
| **A. Workflow JSON** | Portable `.json` for the fal.ai workflow runtime | Reusable asset, UI-driven, fixed graph |
| **B. genmedia CLI** | Sequence of `genmedia run` calls (local) | Local scripting, exploratory, conditional logic |

---

## Mode A: Workflow JSON

See [patterns.md](references/patterns.md) for annotated node patterns and
[workflows.md](references/workflows.md) for production-ready complete JSON files.

### Control Types at a Glance

| Type | Extracts | Best For | Preprocessor Endpoint |
|------|----------|----------|-----------------------|
| **Canny** | Hard edges / outlines | Silhouettes, architecture, product outlines | `fal-ai/imageutils/canny` |
| **Depth** | Scene depth / 3D structure | Indoor scenes, landscapes, volumetric restyle | `fal-ai/depth-pro` |
| **Pose** | Human body skeleton | Character re-illustration, dance, athletics | `fal-ai/dwpose` |
| **Tile** | Fine texture detail | Detail-preserving upscale, in-place restyle | *(raw source image, no preprocessor)* |

### Minimal Working Skeleton (Canny → FLUX ControlNet)

```json
{
  "node-canny": {
    "type": "run",
    "id": "node-canny",
    "depends": ["input"],
    "app": "fal-ai/imageutils/canny",
    "input": {
      "image_url": "$input.reference_image",
      "low_threshold": 50,
      "high_threshold": 200
    }
  },
  "node-controlnet": {
    "type": "run",
    "id": "node-controlnet",
    "depends": ["node-canny", "input"],
    "app": "fal-ai/flux/dev/controlnet",
    "input": {
      "prompt": "$input.style_prompt",
      "control_image_url": "$node-canny.image.url",
      "controlnet_conditioning_scale": 0.85,
      "num_inference_steps": 28,
      "guidance_scale": 3.5
    }
  },
  "output": {
    "type": "display",
    "id": "output",
    "depends": ["node-controlnet", "node-canny"],
    "input": {},
    "fields": {
      "result_image": "$node-controlnet.images.0.url",
      "edge_map": "$node-canny.image.url"
    }
  }
}
```

**ControlNet output:** `$node-controlnet.images.0.url`
**Preprocessor output:** `$node-preprocess.image.url` (canny, depth, pose all use `.image.url`)

### Input Schema for ControlNet Workflows

```json
"schema": {
  "input": {
    "reference_image": {
      "name": "reference_image",
      "label": "Reference Image URL",
      "type": "string",
      "description": "URL of the image whose composition you want to lock",
      "required": true,
      "modelId": "node-canny"
    },
    "style_prompt": {
      "name": "style_prompt",
      "label": "Style Prompt",
      "type": "string",
      "description": "Describe the style, mood, or content for the output image",
      "required": true,
      "modelId": "node-controlnet"
    },
    "conditioning_scale": {
      "name": "conditioning_scale",
      "label": "Lock Strength (0.0–1.0)",
      "type": "number",
      "description": "How tightly to follow the reference structure. 0.85 is a good default.",
      "required": false,
      "modelId": "node-controlnet"
    }
  }
}
```

### Critical Rules

1. **Always preprocess before ControlNet.** Pass the preprocessed control signal
   (`$node-canny.image.url`, `$node-depth.image.url`) to `control_image_url` — never the raw
   reference image directly (unless using Tile mode).
2. **`conditioning_scale` is the lock knob.** `0.6`–`0.75` = loose (creative freedom);
   `0.8`–`1.0` = tight (near-exact structure). Default `0.85` suits most restyle tasks.
3. **ControlNet output is an image array.** Use `$node.images.0.url` (same as standard image gen).
4. **Preprocessor output is a single image.** Use `$node.image.url`.
5. **Verify field names.** Run `genmedia schema <endpoint_id> --json` before writing any node —
   `control_image_url`, `controlnet_image_url`, and `image_url` vary across implementations.

---

## Mode B: genmedia CLI

### Canny Restyle (step-by-step)

```bash
# Step 1: Upload your reference image
genmedia upload ./reference.png --json
# Save returned URL → REFERENCE_URL

# Step 2: Inspect preprocessor schema
genmedia schema fal-ai/imageutils/canny --json

# Step 3: Extract canny edges
genmedia run fal-ai/imageutils/canny \
  --image_url "$REFERENCE_URL" \
  --low_threshold 50 \
  --high_threshold 200 \
  --json
# Save .image.url → CANNY_URL

# Step 4: Inspect ControlNet schema
genmedia schema fal-ai/flux/dev/controlnet --json

# Step 5: Generate with composition lock
genmedia run fal-ai/flux/dev/controlnet \
  --prompt "watercolor painting of a mountain village, warm tones, impressionist" \
  --control_image_url "$CANNY_URL" \
  --controlnet_conditioning_scale 0.85 \
  --num_inference_steps 28 \
  --json \
  --download "./outputs/controlnet/{request_id}_{index}.{ext}"
```

### Depth Restyle

```bash
genmedia schema fal-ai/depth-pro --json

genmedia run fal-ai/depth-pro \
  --image_url "$REFERENCE_URL" \
  --json
# Save .image.url → DEPTH_URL

genmedia run fal-ai/flux/dev/controlnet \
  --prompt "fantasy forest at twilight, bioluminescent plants, cinematic" \
  --control_image_url "$DEPTH_URL" \
  --controlnet_conditioning_scale 0.75 \
  --num_inference_steps 28 \
  --json
```

### Pose Lock (Character Re-illustration)

```bash
genmedia schema fal-ai/dwpose --json

genmedia run fal-ai/dwpose \
  --image_url "$REFERENCE_URL" \
  --json
# Save .image.url → POSE_URL

genmedia run fal-ai/flux/dev/controlnet \
  --prompt "anime illustration of a warrior, vibrant colors, detailed armor" \
  --control_image_url "$POSE_URL" \
  --controlnet_conditioning_scale 0.9 \
  --num_inference_steps 30 \
  --json
```

---

## Reference Files

- [endpoints.md](references/endpoints.md) — ControlNet and preprocessor endpoint catalog
- [patterns.md](references/patterns.md) — Reusable workflow JSON patterns (canny, depth, pose, multi-controlnet, LLM-enhanced)
- [workflows.md](references/workflows.md) — Complete production-ready workflow JSON examples

---

## Pre-Output Checklist

Before delivering any ControlNet workflow:

- [ ] Preprocessor node exists and is in `depends` of the ControlNet generation node
- [ ] `control_image_url` references `$node-preprocess.image.url` (not raw input)
- [ ] `conditioning_scale` is set explicitly (not left to default)
- [ ] Field names verified with `genmedia schema <endpoint_id> --json`
- [ ] Output node `depends` includes the ControlNet generation node
- [ ] Every `$node.xxx` reference has a matching `depends` entry
- [ ] Node `id` matches object key in every node
