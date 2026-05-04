# Image Restoration Recipe

Use this recipe to restore and enhance image quality, fix blur, noise, haze, faces, or documents. The recipe is a **smart dispatcher**: pick the right specialist endpoint for the dominant defect, optionally chain a second pass.

## Inputs to collect

- **Source image**: URL or local path.
- **Dominant defect**: blur, noise, haze, distorted face, damaged document, low resolution. Ask the user if not obvious.
- **Output quality vs fidelity tradeoff**: for face restoration, fidelity (1.0) preserves identity better; lower fidelity (0.0-0.5) produces a higher-quality but more "synthetic" result.

## Smart dispatch by defect

| Defect | Endpoint |
|--------|----------|
| Motion blur, focus blur | `fal-ai/nafnet/deblur` |
| Sensor noise, ISO grain | `fal-ai/nafnet/denoise` |
| Atmospheric haze, fog | `fal-ai/mix-dehaze-net` |
| Distorted, low-res, or damaged face | `fal-ai/codeformer` |
| Scanned document (text legibility) | `fal-ai/docres` |

If multiple defects are present, run them in sequence (denoise → deblur → upscale, or face-fix → upscale).

## Flow

### Single-defect restoration

```bash
URL=$(genmedia upload ./damaged.jpg --json | jq -r '.url')

# Pick endpoint based on dominant defect
genmedia run fal-ai/nafnet/deblur \
 --image_url "$URL" \
 --download "./outputs/restored/{request_id}_{index}.{ext}" \
 --json
```

### Face restoration with fidelity control

```bash
URL=$(genmedia upload ./bad-face.jpg --json | jq -r '.url')

genmedia run fal-ai/codeformer \
 --image_url "$URL" \
 --fidelity 0.7 \
 --download "./outputs/restored/{request_id}_{index}.{ext}" \
 --json
```

`fidelity` is typically 0.0-1.0:

- **0.0** → maximum quality, identity may drift
- **1.0** → maximum identity preservation, less aggressive cleanup
- **0.5-0.7** → good balance for most portraits

### Document restoration

```bash
URL=$(genmedia upload ./scan.jpg --json | jq -r '.url')

genmedia run fal-ai/docres \
 --image_url "$URL" \
 --download "./outputs/restored/{request_id}_{index}.{ext}" \
 --json
```

DocRes is tuned for text legibility, it removes paper texture, fixes contrast, and straightens scans without inventing characters.

### Chained restoration

For a noisy + blurry photo, chain two passes:

```bash
# Pass 1: denoise
URL1=$(genmedia upload ./input.jpg --json | jq -r '.url')
RES1=$(genmedia run fal-ai/nafnet/denoise --image_url "$URL1" --json)
URL2=$(echo "$RES1" | jq -r '.image.url')

# Pass 2: deblur the cleaned-up result
genmedia run fal-ai/nafnet/deblur \
 --image_url "$URL2" \
 --download "./outputs/restored/{request_id}_{index}.{ext}" \
 --json
```

For an old portrait scan: face-fix → upscale.

```bash
# Pass 1: codeformer for face
RES1=$(genmedia run fal-ai/codeformer \
 --image_url "$URL1" --fidelity 0.7 --json)
URL2=$(echo "$RES1" | jq -r '.image.url')

# Pass 2: upscale (see fal-models-catalog/image-to-image.md for upscale endpoints)
genmedia run <upscale-endpoint> \
 --image_url "$URL2" \
 --download "./outputs/restored/{request_id}_{index}.{ext}" \
 --json
```

## Discovery for unusual defects

For defects not covered above (artifacts, color shifts, JPEG compression):

```bash
genmedia models "image restoration" --json
genmedia models --category image-to-image --json | jq '.models[] | select(.tags[]? == "restoration")'
genmedia docs "image restoration enhance" --json
```

## Quality bar

Before returning:

- The fix addressed the actual dominant defect, not a guess.
- For faces: identity is preserved (eyes, face shape, hair). If drift, raise `fidelity`.
- For documents: text is more legible than the source, no characters invented or dropped.
- For chained passes: the intermediate result was acceptable before adding the next step.
- Output paths come from `downloaded_files[]`.

## Tips

- **Source format matters.** PNG / lossless source produces cleaner results than re-compressed JPEG.
- **One defect at a time** in early iterations. Diagnose before chaining.
- **Don't over-restore.** Heavy CodeFormer at low fidelity makes everyone look like the same generic AI face.
- **Compare side-by-side.** Always show before/after to the user; restoration is subjective.

## Common parameters

Inspect each endpoint:

```bash
genmedia schema fal-ai/nafnet/deblur --json
genmedia schema fal-ai/codeformer --json
genmedia schema fal-ai/docres --json
```

Frequently exposed:

- `image_url`: source
- `fidelity` (CodeFormer only), 0.0-1.0, identity preservation
- Some endpoints expose `output_format` (`png`, `jpeg`)
