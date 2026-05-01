# Image-to-3D Endpoints

Curated picks across 3 use cases, premium quality, fast/cheap, and multi-view input. **Meshy 6** and **Hunyuan 3D Pro** lead premium; **Tripo P1/H3.1** are strong alternatives. Verify with `genmedia models --endpoint_id <id> --json` before running.

## Premium

High-quality mesh generation.

- `fal-ai/hunyuan-3d/v3.1/pro/image-to-3d`: Tencent · Hunyuan 3D v3.1 Pro
- `fal-ai/meshy/v6/image-to-3d`: Meshy 6
- `fal-ai/meshy/v6-preview/image-to-3d`: Meshy 6 Preview
- `tripo3d/h3.1/image-to-3d`: Tripo · H3.1
- `fal-ai/hyper3d/rodin/v2`: Hyper3D · Rodin v2

## Fast / cheap

Fast / draft 3D.

- `fal-ai/hunyuan-3d/v3.1/rapid/image-to-3d`: Tencent · Hunyuan 3D Rapid
- `fal-ai/triposr`: TripoSR

## Multi-view to 3D

Multiple view angles → 3D (front / side / three-quarter).

- `fal-ai/meshy/v5/multi-image-to-3d`: Meshy 5 Multi
- `fal-ai/meshy/v6/multi-image-to-3d`: Meshy 6 Multi
- `fal-ai/hunyuan3d/v2/multi-view`: Tencent · Hunyuan3D v2 Multi-view
- `fal-ai/hunyuan3d/v2/multi-view/turbo`: Tencent · Hunyuan3D v2 Multi-view Turbo
- `tripo3d/h3.1/multiview-to-3d`: Tripo · H3.1 Multiview
- `tripo3d/tripo/v2.5/multiview-to-3d`: Tripo3D v2.5 Multiview
- `fal-ai/trellis/multi`: Trellis Multi

## Tips for best results

- **Single object on plain background.** Photogrammetry-style 3D extraction works dramatically better when the subject is isolated.
- **Remove the background first** if the source has clutter (use `fal-ai/bria/background/remove`).
- **Multiple angles help** when the model supports multi-image input, front, side, three-quarter views give the best mesh.
- **Generation is slow** (1-5 minutes), always run async with `genmedia status` polling.

## Pre-processing chain (single-image, busy background)

```bash
URL_RAW=$(genmedia upload ./object.jpg --json | jq -r '.url')

# Step 1: background removal
RES_BG=$(genmedia run fal-ai/bria/background/remove --image_url "$URL_RAW" --json)
URL_CLEAN=$(echo "$RES_BG" | jq -r '.image.url')

# Step 2: image-to-3D
SUBMIT=$(genmedia run fal-ai/hunyuan-3d/v3.1/pro/image-to-3d \
 --image_url "$URL_CLEAN" \
 --async \
 --json)
REQ=$(echo "$SUBMIT" | jq -r '.request_id')

# Step 3: poll + download
genmedia status fal-ai/hunyuan-3d/v3.1/pro/image-to-3d "$REQ" \
 --download "./out/{request_id}.{ext}" \
 --json
```

## See also

- For text-only generation, see [text-to-3d.md](text-to-3d.md)
- For complete 3D character experiences (rigged GLB + companion creatures + Three.js scene), see the `fal-regenerate-3d` vertical skill
