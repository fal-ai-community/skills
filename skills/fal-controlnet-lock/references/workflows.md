# Complete ControlNet Composition Lock Workflows

Production-ready workflow JSON files for direct import into fal.ai.

---

## Workflow 1: Canny Edge Style Transfer

Takes a reference image and a style prompt. Extracts canny edges, then generates a new image that
preserves all outlines and composition while applying the requested style.

**Input:** Reference image URL + style prompt + optional conditioning scale
**Output:** Restyled image (composition-locked) + the edge map used

**Flow:**
```
[Reference Image] → [Canny Edge] → [FLUX ControlNet] → [Styled Output]
                                 ↗ (parallel, no dep)
[Style Prompt] ─────────────────────────────────────────────────────────
```

```json
{
  "name": "canny-style-transfer",
  "title": "Canny Style Transfer",
  "contents": {
    "name": "workflow",
    "nodes": {
      "output": {
        "type": "display",
        "id": "output",
        "depends": ["node-controlnet", "node-canny"],
        "input": {},
        "fields": {
          "result_image": "$node-controlnet.images.0.url",
          "edge_map": "$node-canny.image.url"
        },
        "metadata": { "position": { "x": 2200, "y": 0 } }
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
        },
        "metadata": { "position": { "x": 600, "y": 0 } }
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
          "guidance_scale": 3.5,
          "image_size": { "width": 1024, "height": 1024 }
        },
        "metadata": { "position": { "x": 1400, "y": 0 } }
      }
    },
    "output": {
      "result_image": "$node-controlnet.images.0.url",
      "edge_map": "$node-canny.image.url"
    },
    "schema": {
      "input": {
        "reference_image": {
          "name": "reference_image",
          "label": "Reference Image URL",
          "type": "string",
          "description": "URL of the image whose composition (edges, outlines) you want to preserve",
          "required": true,
          "modelId": "node-canny"
        },
        "style_prompt": {
          "name": "style_prompt",
          "label": "Style Prompt",
          "type": "string",
          "description": "Describe the output style, art direction, mood, and content",
          "required": true,
          "modelId": "node-controlnet"
        }
      },
      "output": {
        "result_image": {
          "name": "result_image",
          "label": "Composition-Locked Styled Image",
          "type": "string"
        },
        "edge_map": {
          "name": "edge_map",
          "label": "Canny Edge Map (Control Signal)",
          "type": "string"
        }
      }
    },
    "version": "1",
    "metadata": {
      "input": { "position": { "x": 0, "y": 0 } },
      "description": "Lock image composition via canny edges and restyle with FLUX ControlNet"
    }
  },
  "is_public": true,
  "user_id": "",
  "user_nickname": "",
  "created_at": ""
}
```

---

## Workflow 2: LLM-Enhanced Pose Lock

Takes a photo of a person and a character brief. An LLM expands the brief into a detailed
generation prompt; DWPose extracts the skeleton; FLUX ControlNet re-illustrates the character in
the exact same pose. Both LLM and pose extraction run in parallel.

**Input:** Reference photo URL + character brief
**Output:** Re-illustrated character (same pose, new style) + skeleton reference

**Flow:**
```
[Character Brief] → [LLM Prompt Writer] ──────────────→
                                                        ↓
[Reference Photo] → [DWPose Skeleton] → [FLUX ControlNet] → [Output]
```

```json
{
  "name": "pose-lock-character",
  "title": "Pose Lock: Character Re-illustration",
  "contents": {
    "name": "workflow",
    "nodes": {
      "output": {
        "type": "display",
        "id": "output",
        "depends": ["node-controlnet", "node-pose"],
        "input": {},
        "fields": {
          "character_image": "$node-controlnet.images.0.url",
          "skeleton_reference": "$node-pose.image.url"
        },
        "metadata": { "position": { "x": 2800, "y": 0 } }
      },
      "node-prompt-writer": {
        "type": "run",
        "id": "node-prompt-writer",
        "depends": ["input"],
        "app": "openrouter/router",
        "input": {
          "prompt": "$input.character_brief",
          "system_prompt": "You are an expert image prompt engineer for diffusion models. The user describes a character. Write a detailed, vivid text-to-image prompt for that character. Include: physical appearance, clothing style, art style, lighting, color palette, mood. The composition and pose will be set by a reference image — do NOT describe pose or framing. Output ONLY the prompt, max 100 words.",
          "model": "google/gemini-2.5-flash",
          "temperature": 0.7
        },
        "metadata": { "position": { "x": 600, "y": -300 } }
      },
      "node-pose": {
        "type": "run",
        "id": "node-pose",
        "depends": ["input"],
        "app": "fal-ai/dwpose",
        "input": {
          "image_url": "$input.reference_photo"
        },
        "metadata": { "position": { "x": 600, "y": 300 } }
      },
      "node-controlnet": {
        "type": "run",
        "id": "node-controlnet",
        "depends": ["node-pose", "node-prompt-writer"],
        "app": "fal-ai/flux/dev/controlnet",
        "input": {
          "prompt": "$node-prompt-writer.output",
          "control_image_url": "$node-pose.image.url",
          "controlnet_conditioning_scale": 0.9,
          "num_inference_steps": 30,
          "guidance_scale": 4.5,
          "image_size": { "width": 1024, "height": 1024 }
        },
        "metadata": { "position": { "x": 1800, "y": 0 } }
      }
    },
    "output": {
      "character_image": "$node-controlnet.images.0.url",
      "skeleton_reference": "$node-pose.image.url"
    },
    "schema": {
      "input": {
        "reference_photo": {
          "name": "reference_photo",
          "label": "Reference Photo URL",
          "type": "string",
          "description": "URL of the source photo containing the person whose pose you want to lock",
          "required": true,
          "modelId": "node-pose"
        },
        "character_brief": {
          "name": "character_brief",
          "label": "Character Brief",
          "type": "string",
          "description": "Describe the new character: who they are, their style, art direction (e.g. 'anime warrior with golden armor, cel-shaded, vibrant')",
          "required": true,
          "modelId": "node-prompt-writer"
        }
      },
      "output": {
        "character_image": {
          "name": "character_image",
          "label": "Re-illustrated Character",
          "type": "string"
        },
        "skeleton_reference": {
          "name": "skeleton_reference",
          "label": "Pose Skeleton (Reference)",
          "type": "string"
        }
      }
    },
    "version": "1",
    "metadata": {
      "input": { "position": { "x": 0, "y": 0 } },
      "description": "Re-illustrate a character in any style while locking their body pose from a reference photo"
    }
  },
  "is_public": true,
  "user_id": "",
  "user_nickname": "",
  "created_at": ""
}
```

---

## Workflow 3: Depth Restyle + Upscale

Takes a reference image and style prompt. Extracts depth map to lock scene structure, generates
at 1024px with FLUX ControlNet, then upscales to 4K for final delivery.

**Input:** Reference image URL + style prompt
**Output:** 4K upscaled styled image + depth map reference

**Flow:**
```
[Reference Image] → [Depth Pro] → [FLUX ControlNet @ 1024px] → [SeedVR Upscale 4K] → [Output]
```

```json
{
  "name": "depth-restyle-4k",
  "title": "Depth Restyle to 4K",
  "contents": {
    "name": "workflow",
    "nodes": {
      "output": {
        "type": "display",
        "id": "output",
        "depends": ["node-upscale", "node-depth"],
        "input": {},
        "fields": {
          "final_image_4k": "$node-upscale.image.url",
          "depth_map": "$node-depth.image.url",
          "draft_1024": "$node-controlnet.images.0.url"
        },
        "metadata": { "position": { "x": 2800, "y": 0 } }
      },
      "node-depth": {
        "type": "run",
        "id": "node-depth",
        "depends": ["input"],
        "app": "fal-ai/depth-pro",
        "input": {
          "image_url": "$input.reference_image"
        },
        "metadata": { "position": { "x": 600, "y": 0 } }
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
          "guidance_scale": 4.0,
          "image_size": { "width": 1024, "height": 1024 }
        },
        "metadata": { "position": { "x": 1400, "y": 0 } }
      },
      "node-upscale": {
        "type": "run",
        "id": "node-upscale",
        "depends": ["node-controlnet"],
        "app": "fal-ai/seedvr/upscale/image",
        "input": {
          "image_url": "$node-controlnet.images.0.url"
        },
        "metadata": { "position": { "x": 2100, "y": 0 } }
      }
    },
    "output": {
      "final_image_4k": "$node-upscale.image.url",
      "depth_map": "$node-depth.image.url",
      "draft_1024": "$node-controlnet.images.0.url"
    },
    "schema": {
      "input": {
        "reference_image": {
          "name": "reference_image",
          "label": "Reference Image URL",
          "type": "string",
          "description": "URL of the image whose depth structure (3D layout) you want to preserve",
          "required": true,
          "modelId": "node-depth"
        },
        "style_prompt": {
          "name": "style_prompt",
          "label": "Style Prompt",
          "type": "string",
          "description": "Describe the target style, setting, and mood for the output",
          "required": true,
          "modelId": "node-controlnet"
        }
      },
      "output": {
        "final_image_4k": {
          "name": "final_image_4k",
          "label": "Final Image (4K)",
          "type": "string"
        },
        "depth_map": {
          "name": "depth_map",
          "label": "Depth Map (Control Signal)",
          "type": "string"
        },
        "draft_1024": {
          "name": "draft_1024",
          "label": "Draft at 1024px",
          "type": "string"
        }
      }
    },
    "version": "1",
    "metadata": {
      "input": { "position": { "x": 0, "y": 0 } },
      "description": "Restyle a scene using depth-guided ControlNet, then upscale to 4K"
    }
  },
  "is_public": true,
  "user_id": "",
  "user_nickname": "",
  "created_at": ""
}
```
