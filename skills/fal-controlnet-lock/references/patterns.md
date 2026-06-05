# ControlNet Workflow Patterns

Reusable JSON node patterns for composition-locked generation.

---

## Pattern 1: Canny Edge Style Transfer

The most common ControlNet pattern. Extracts outlines from the reference and regenerates in any style.

```
[Reference Image] → [Canny] → [FLUX ControlNet] → [Output]
```

```json
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
}
```

**Outputs:**
- `$node-controlnet.images.0.url` — restyled image

---

## Pattern 2: Depth-Guided Scene Restyle

Preserves volumetric 3D structure. Best for rooms, landscapes, outdoor environments.

```
[Reference Image] → [Depth Pro] → [FLUX ControlNet] → [Output]
```

```json
"node-depth": {
  "type": "run",
  "id": "node-depth",
  "depends": ["input"],
  "app": "fal-ai/depth-pro",
  "input": {
    "image_url": "$input.reference_image"
  }
},
"node-controlnet": {
  "type": "run",
  "id": "node-controlnet",
  "depends": ["node-depth", "input"],
  "app": "fal-ai/flux/dev/controlnet",
  "input": {
    "prompt": "$input.style_prompt",
    "control_image_url": "$node-depth.image.url",
    "controlnet_conditioning_scale": 0.75,
    "num_inference_steps": 28,
    "guidance_scale": 4.0
  }
}
```

**Use lower conditioning_scale (0.7–0.8)** for depth — depth maps are coarser than edge maps and
benefit from more generative freedom.

---

## Pattern 3: Pose-Lock Character Re-illustration

Skeleton from a reference human photo is applied to a fully new character in any style.

```
[Photo w/ Human] → [DWPose] → [FLUX ControlNet] → [New Character, Same Pose]
```

```json
"node-pose": {
  "type": "run",
  "id": "node-pose",
  "depends": ["input"],
  "app": "fal-ai/dwpose",
  "input": {
    "image_url": "$input.reference_image"
  }
},
"node-controlnet": {
  "type": "run",
  "id": "node-controlnet",
  "depends": ["node-pose", "input"],
  "app": "fal-ai/flux/dev/controlnet",
  "input": {
    "prompt": "$input.character_prompt",
    "control_image_url": "$node-pose.image.url",
    "controlnet_conditioning_scale": 0.9,
    "num_inference_steps": 30,
    "guidance_scale": 4.5
  }
}
```

**Use higher conditioning_scale (0.85–1.0)** for pose — skeleton positions are meaningful only
when followed closely.

---

## Pattern 4: LLM-Enhanced Style Prompt → ControlNet

An LLM crafts a detailed style prompt before generation, improving output quality.

```
[User Brief] → [LLM] → [Style Prompt]
                              ↓
[Reference Image] → [Canny] → [FLUX ControlNet] → [Output]
```

```json
"node-prompt-writer": {
  "type": "run",
  "id": "node-prompt-writer",
  "depends": ["input"],
  "app": "openrouter/router",
  "input": {
    "prompt": "$input.style_brief",
    "system_prompt": "You are an expert image prompt writer for diffusion models. The user gives you a brief style description. Expand it into a detailed, evocative image generation prompt. Include: art style, lighting, color palette, mood, rendering quality. Output ONLY the prompt text, max 120 words.",
    "model": "google/gemini-2.5-flash",
    "temperature": 0.7
  }
},
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
  "depends": ["node-canny", "node-prompt-writer"],
  "app": "fal-ai/flux/dev/controlnet",
  "input": {
    "prompt": "$node-prompt-writer.output",
    "control_image_url": "$node-canny.image.url",
    "controlnet_conditioning_scale": 0.85,
    "num_inference_steps": 28,
    "guidance_scale": 3.5
  }
}
```

**Note:** `node-canny` and `node-prompt-writer` are independent — they run in parallel.

---

## Pattern 5: ControlNet + Upscale

Generate at 1024px with ControlNet, then upscale to 4K for delivery.

```
[Reference] → [Canny] → [ControlNet @ 1024px] → [SeedVR Upscale] → [4K Output]
```

```json
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
    "image_size": {"width": 1024, "height": 1024}
  }
},
"node-upscale": {
  "type": "run",
  "id": "node-upscale",
  "depends": ["node-controlnet"],
  "app": "fal-ai/seedvr/upscale/image",
  "input": {
    "image_url": "$node-controlnet.images.0.url"
  }
}
```

**Output:** `$node-upscale.image.url` (4K)

---

## Pattern 6: Parallel Control Type Comparison

Generate the same prompt from three control types simultaneously to compare lock quality.

```
[Reference] → [Canny]  → [ControlNet-Canny]  →
           → [Depth]  → [ControlNet-Depth]  → [Output: compare all three]
           → [Pose]   → [ControlNet-Pose]   →
```

```json
"node-canny": {
  "type": "run", "id": "node-canny", "depends": ["input"],
  "app": "fal-ai/imageutils/canny",
  "input": { "image_url": "$input.reference_image", "low_threshold": 50, "high_threshold": 200 }
},
"node-depth": {
  "type": "run", "id": "node-depth", "depends": ["input"],
  "app": "fal-ai/depth-pro",
  "input": { "image_url": "$input.reference_image" }
},
"node-pose": {
  "type": "run", "id": "node-pose", "depends": ["input"],
  "app": "fal-ai/dwpose",
  "input": { "image_url": "$input.reference_image" }
},
"node-result-canny": {
  "type": "run", "id": "node-result-canny",
  "depends": ["node-canny", "input"],
  "app": "fal-ai/flux/dev/controlnet",
  "input": {
    "prompt": "$input.style_prompt",
    "control_image_url": "$node-canny.image.url",
    "controlnet_conditioning_scale": 0.85,
    "num_inference_steps": 28
  }
},
"node-result-depth": {
  "type": "run", "id": "node-result-depth",
  "depends": ["node-depth", "input"],
  "app": "fal-ai/flux/dev/controlnet",
  "input": {
    "prompt": "$input.style_prompt",
    "control_image_url": "$node-depth.image.url",
    "controlnet_conditioning_scale": 0.75,
    "num_inference_steps": 28
  }
},
"node-result-pose": {
  "type": "run", "id": "node-result-pose",
  "depends": ["node-pose", "input"],
  "app": "fal-ai/flux/dev/controlnet",
  "input": {
    "prompt": "$input.style_prompt",
    "control_image_url": "$node-pose.image.url",
    "controlnet_conditioning_scale": 0.90,
    "num_inference_steps": 28
  }
},
"output": {
  "type": "display", "id": "output",
  "depends": ["node-result-canny", "node-result-depth", "node-result-pose",
              "node-canny", "node-depth", "node-pose"],
  "input": {},
  "fields": {
    "canny_result": "$node-result-canny.images.0.url",
    "depth_result": "$node-result-depth.images.0.url",
    "pose_result": "$node-result-pose.images.0.url",
    "edge_map": "$node-canny.image.url",
    "depth_map": "$node-depth.image.url",
    "skeleton_map": "$node-pose.image.url"
  }
}
```

---

## Conditioning Scale Quick Reference

| Control Type | Recommended Scale | Rationale |
|---|---|---|
| Canny | `0.80–0.90` | Edge maps are precise; follow closely for structure |
| Depth | `0.70–0.80` | Depth maps are coarser; allow more generative freedom |
| Pose | `0.85–0.95` | Skeleton positions are semantically critical |
| Tile | `0.60–0.75` | Tile is soft guidance; lower scale avoids over-constraining |
