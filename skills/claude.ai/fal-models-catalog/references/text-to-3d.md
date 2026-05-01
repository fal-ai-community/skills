# Text-to-3D Endpoints

Curated picks. Output is typically GLB / OBJ / PLY. **Meshy 6** and **Hunyuan 3D Pro** are the premium picks; **Tripo P1 / H3.1** offer alternatives. Verify with `genmedia models --endpoint_id <id> --json` before running.

## Premium

- `fal-ai/meshy/v6/text-to-3d`: Meshy 6
- `fal-ai/meshy/v6-preview/text-to-3d`: Meshy 6 Preview
- `fal-ai/hunyuan-3d/v3.1/pro/text-to-3d`: Tencent · Hunyuan 3D v3.1 Pro
- `fal-ai/hunyuan3d-v3/text-to-3d`: Tencent · Hunyuan 3D v3
- `tripo3d/p1/text-to-3d`: Tripo · P1
- `tripo3d/h3.1/text-to-3d`: Tripo · H3.1

## Fast / rapid variants

- `fal-ai/hunyuan-3d/v3.1/rapid/text-to-3d`: Tencent · Hunyuan 3D Rapid

## Tips for best results

- **Simple, well-defined objects work best.** Complex scenes don't reconstruct well.
- **Single-object framing**: "a medieval sword with ornate handle" works; "a knight in a forest" struggles.
- **Generation takes 1-5 minutes**: always run with `--async`, then poll `genmedia status`.

## Async pattern

```bash
SUBMIT=$(genmedia run fal-ai/meshy/v6/text-to-3d \
 --prompt "a medieval sword with ornate handle" \
 --async \
 --json)
REQ=$(echo "$SUBMIT" | jq -r '.request_id')

genmedia status fal-ai/meshy/v6/text-to-3d "$REQ" \
 --download "./out/{request_id}.{ext}" \
 --json
```

## Common parameters

```bash
genmedia schema fal-ai/meshy/v6/text-to-3d --json
```

Frequently exposed:

- `prompt`: object description
- `art_style`: `realistic`, `cartoon`, `low-poly` (model-specific)
- `seed`: reproducibility
- `output_format`: `glb`, `obj`, `ply`

## See also

- For image-derived 3D, see [image-to-3d.md](image-to-3d.md)
- For 3D character experiences (rigged GLB + Three.js scene), see the `fal-regenerate-3d` vertical skill
