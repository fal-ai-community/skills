# Virtual Try-On Recipe

Use this recipe to apply a garment onto a person photo. The default endpoint is single-call (`fal-ai/fashn/tryon/v1.5`), but the recipe wraps it with optional pre-processing (background cleanup) and post-processing (upscale) for production-quality output.

## Inputs to collect

- **Person image**: URL or local path. Clear full-body or upper-body shot works best.
- **Garment image**: URL or local path. Plain or white background gives best results.
- **Garment type**: `top`, `bottom`, `full-body`, or `dress`. Helps placement; auto-detected if omitted.
- **Quality preference**: `speed` for drafts, `balanced` for default, `quality` for final delivery.

## Single-call flow

```bash
URL_PERSON=$(genmedia upload ./person.jpg --json | jq -r '.url')
URL_GARMENT=$(genmedia upload ./dress.jpg --json | jq -r '.url')

genmedia run fal-ai/fashn/tryon/v1.5 \
 --model_image "$URL_PERSON" \
 --garment_image "$URL_GARMENT" \
 --garment_type "dress" \
 --download "./outputs/tryon/{request_id}_{index}.{ext}" \
 --json
```

Inspect schema first, field names may evolve:

```bash
genmedia schema fal-ai/fashn/tryon/v1.5 --json
```

## Full pipeline (pre-clean + tryon + upscale)

For e-commerce-grade output, chain three steps:

### Step 1: garment background removal

If the garment image has a busy background, the tryon model may pick up artifacts. Remove the background first:

```bash
URL_GARMENT_RAW=$(genmedia upload ./garment.jpg --json | jq -r '.url')

# Discover or use a known background-removal endpoint
RES_BG=$(genmedia run <bg-removal-endpoint> --image_url "$URL_GARMENT_RAW" --json)
URL_GARMENT_CLEAN=$(echo "$RES_BG" | jq -r '.image.url')
```

For background-removal endpoint discovery:

```bash
genmedia models "background remove" --json
genmedia models --endpoint_id fal-ai/bria/background/remove --json
```

### Step 2: try-on

```bash
URL_PERSON=$(genmedia upload ./person.jpg --json | jq -r '.url')

RES_TRYON=$(genmedia run fal-ai/fashn/tryon/v1.5 \
 --model_image "$URL_PERSON" \
 --garment_image "$URL_GARMENT_CLEAN" \
 --garment_type "top" \
 --quality "quality" \
 --json)
URL_TRYON=$(echo "$RES_TRYON" | jq -r '.image.url')
```

### Step 3: optional upscale for final delivery

```bash
genmedia run <upscale-endpoint> \
 --image_url "$URL_TRYON" \
 --download "./outputs/tryon/{request_id}_{index}.{ext}" \
 --json
```

For upscale endpoint selection, see [fal-models-catalog/image-to-image.md](../../fal-models-catalog/references/image-to-image.md).

## Garment type guidance

| Type | Use for |
|------|---------|
| `top` | T-shirts, blouses, jackets, sweaters |
| `bottom` | Pants, jeans, skirts, shorts |
| `full-body` | Suits, jumpsuits, overalls |
| `dress` | Dresses, gowns, robes |

If unsure, leave it out and let auto-detect handle it. Specify when results misplace the garment.

## Quality bar

Before returning:

- Garment fits the person's body proportions (no float, no oversized warp).
- Original face, hair, and pose are preserved.
- Garment color matches the source (no color shift).
- Logos / patterns on the garment are not distorted.
- Lighting on the garment matches the rest of the person.
- Output paths come from `downloaded_files[]`.

## Tips

- **Person photo:** clear full or upper body, neutral pose, plain background. Avoid heavy occlusion (arms across chest).
- **Garment photo:** flat-lay or mannequin shots work best. Patterned garments can show banding, try a cleaner reference.
- **Background removal first** if the garment image has a busy or colored background; quality jumps significantly.
- **Color accuracy:** if the result shifts color, increase `quality` or try a different garment image (some compressed JPEGs lose color fidelity).

## Common parameters

Always inspect:

```bash
genmedia schema fal-ai/fashn/tryon/v1.5 --json
```

Frequently exposed:

- `model_image` / `garment_image`. URLs of inputs
- `garment_type`: `top`, `bottom`, `full-body`, `dress`
- `quality`: `speed`, `balanced`, `quality`
- `seed`: reproducibility

## Discovery for alternative tryon models

```bash
genmedia models "virtual tryon" --json
genmedia models "garment transfer" --json
genmedia docs "virtual tryon" --json
```
