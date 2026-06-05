# ControlNet Endpoints Reference

Always run `genmedia schema <endpoint_id> --json` before writing nodes — field names and available
parameters vary between endpoint versions.

---

## Preprocessors (Extract Control Signal)

Preprocessors transform a raw reference image into a spatial control signal. All preprocessors
output a single processed image at `$node.image.url`.

### Canny Edge Detection

**Endpoint:** `fal-ai/imageutils/canny`

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `image_url` | string | required | URL of source image |
| `low_threshold` | int | 50 | Lower hysteresis threshold. Lower = more edges captured |
| `high_threshold` | int | 200 | Upper threshold. Higher = only strong edges kept |

**Output:** `$node.image.url` — white-on-black edge map

**Best for:** Architecture, product outlines, text-heavy compositions, object silhouettes,
illustrations with clear line art.

**Tuning guide:**
- Detailed scene: `low_threshold: 30, high_threshold: 150`
- Clean outlines only: `low_threshold: 80, high_threshold: 250`
- Default (balanced): `low_threshold: 50, high_threshold: 200`

---

### Depth Estimation (Apple Depth Pro)

**Endpoint:** `fal-ai/depth-pro`

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `image_url` | string | required | URL of source image |

**Output:** `$node.image.url` — grayscale depth map (white = near, black = far)

**Best for:** Indoor rooms, architectural spaces, landscapes, scenes with clear foreground /
background separation. Preserves volumetric 3D structure across restyling.

---

### Human Pose Estimation (DWPose)

**Endpoint:** `fal-ai/dwpose`

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `image_url` | string | required | URL of source image containing humans |

**Output:** `$node.image.url` — OpenPose-compatible skeleton overlay on black background

**Best for:** Character re-illustration, athletic/dance poses, fashion, any workflow where body
position must stay identical while appearance changes entirely.

**Note:** Works best when the full human body is visible. Quality degrades with severe occlusion
or extreme wide shots where the skeleton becomes too small.

---

## ControlNet Generation Endpoints

### FLUX Dev ControlNet (Recommended Default)

**Endpoint:** `fal-ai/flux/dev/controlnet`

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `prompt` | string | required | Style/content description |
| `control_image_url` | string | required | Preprocessed control signal URL |
| `controlnet_conditioning_scale` | float | 0.85 | Lock strength (0.0–1.0) |
| `num_inference_steps` | int | 28 | Higher = quality, slower |
| `guidance_scale` | float | 3.5 | Prompt adherence (3.5–7.0 typical) |
| `image_size` | object | 1024×1024 | `{"width": 1024, "height": 1024}` |
| `seed` | int | — | Set for reproducible outputs |
| `negative_prompt` | string | — | What to avoid |

**Output:** `$node.images.0.url`

**Best for:** Photorealistic restyle, illustration-to-photo, photo-to-illustration, high-quality
style transfer. State-of-the-art quality with fast inference at 28 steps.

---

### Stable Diffusion XL ControlNet

**Endpoint:** `fal-ai/stable-diffusion-xl/controlnet`

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `prompt` | string | required | Style/content description |
| `negative_prompt` | string | — | What to avoid |
| `controlnet_conditioning_scale` | float | 0.7 | Lock strength (0.0–1.0) |
| `num_inference_steps` | int | 25 | |
| `guidance_scale` | float | 7.5 | Higher = stricter prompt adherence |
| `image_size` | object | — | `{"width": 1024, "height": 1024}` |

**Output:** `$node.images.0.url`

**Best for:** Stylized art, anime, detailed illustration, workflows where the SDXL model
ecosystem (LoRAs, checkpoints) is preferred.

---

## Conditioning Scale Guide

| Scale | Lock Strength | Creative Freedom | When to Use |
|-------|--------------|-----------------|-------------|
| `0.5–0.65` | Loose | High | Rough layout inspiration, reimagining with loose reference |
| `0.7–0.79` | Medium | Moderate | Scene restyle where prompt drives most choices |
| `0.80–0.89` | Tight | Low | Standard composition lock, style transfer |
| `0.90–1.0` | Maximum | Minimal | Exact structural clone, blueprint adherence, product shots |

---

## Output Reference Cheatsheet

| Node Type | Output Field |
|-----------|-------------|
| Canny preprocessor | `$node.image.url` |
| Depth preprocessor | `$node.image.url` |
| Pose preprocessor | `$node.image.url` |
| FLUX Dev ControlNet | `$node.images.0.url` |
| SDXL ControlNet | `$node.images.0.url` |
| Upscale (post-process) | `$node.image.url` |

---

## Discovery Commands

```bash
# Find all ControlNet-related endpoints
genmedia models "controlnet" --json
genmedia models "composition control" --json

# Inspect specific endpoint schemas
genmedia schema fal-ai/imageutils/canny --json
genmedia schema fal-ai/depth-pro --json
genmedia schema fal-ai/dwpose --json
genmedia schema fal-ai/flux/dev/controlnet --json
genmedia schema fal-ai/stable-diffusion-xl/controlnet --json

# Check pricing before long runs
genmedia pricing fal-ai/flux/dev/controlnet --json
```
