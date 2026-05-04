# Product Shot Recipe

Use this recipe when the user has a product image (packshot, packaging photo, transparent PNG) and needs a hero shot in a styled environment. This is a focused subset of [commercial.md](commercial.md), same principles, narrower scope.

## When to use this recipe vs commercial.md

- **product-shot.md**: single hero image from one product reference. Fast, deterministic, e-commerce-grade.
- **commercial.md**: campaign-level production: multiple platforms, lifestyle context, video reveals, ad creative sets.

If the user wants more than one image and there's a story or sequence, switch to `commercial.md` or `storytelling.md`.

## Inputs to collect

- **Product reference**: packshot or transparent PNG. Required.
- **Surface**: pale stone, dark velvet, brushed wood, seamless paper, glass, water surface.
- **Background**: gradient, environmental scene, brand color, neutral void.
- **Lighting style**: softbox, hard rim, natural window, studio strobe, golden hour.
- **Crop / aspect ratio**: square (Instagram), 4:5 (PDP), 16:9 (banner), 9:16 (story).
- **Material cue**: glass / metal / plastic / fabric / food / jewelry (drives lighting choice).

## Flow

```bash
URL_PRODUCT=$(genmedia upload ./product.png --json | jq -r '.url')

genmedia run fal-ai/nano-banana-pro/edit \
 --image_urls "$URL_PRODUCT" \
 --prompt "<structured product hero prompt>" \
 --download "./outputs/product-shot/{request_id}_{index}.{ext}" \
 --json
```

For top-quality output, the recommended endpoint order is:

1. `fal-ai/nano-banana-pro/edit`, fast, strong product fidelity
2. `openai/gpt-image-2/edit`, best for text-on-packaging accuracy
3. `fal-ai/bytedance/seedream/v5/lite/edit`, alternative when above fail

See [fal-models-catalog/image-to-image.md](../../fal-models-catalog/references/image-to-image.md) for the full editing endpoint table.

## Prompt template

Apply commercial prompt build order, condensed to product-shot specifics:

```text
[exact product] preserved exactly from the reference image as the only hero
object, [material and color], placed on [surface], [background], [lighting
setup matched to material], [camera angle], [lens feel], [crop],
premium product photography, accurate packaging, no extra text, no warped
label, no extra products
```

## Material-driven lighting

| Material | Lighting recipe |
|----------|----------------|
| **Glass / liquid** | Backlight + thin rim light along edges, transparent caustics, controlled reflections |
| **Polished metal** | Hard strip highlights, dark flags off-camera to control specular |
| **Plastic / matte** | Soft directional key, clean shadow, no over-gloss |
| **Fabric** | Side light to reveal weave, gentle natural folds, accurate color |
| **Food** | Soft directional key, plausible steam/condensation only |
| **Jewelry / small precious** | 100mm macro feel, dark cards behind subject, crisp pinpoint sparkle |

## Background and surface combinations

- **E-commerce PDP**: seamless white or light gray paper, even softbox.
- **Premium beauty**: pale stone, warm beige, single key from upper-left.
- **Athletic / launch**: concrete, high-contrast strobe, slight motion dust.
- **Food editorial**: matte ceramic or natural wood, window-style light, plausible scatter (crumbs, sauce).
- **Tech / minimal**: gradient void, single rim, polished surface reflection.

## Examples

### Skincare bottle on stone

```text
amber glass skincare serum bottle preserved exactly from the reference, matte
black dropper, standing on pale travertine, soft diffused key light from upper
left, thin rim light on glass edges, subtle water condensation, warm beige
background, square crop, premium beauty product photography, no added text,
no extra bottles
```

### Sneaker hover

```text
single white running sneaker preserved exactly from the reference, blue
outsole accents intact, three-quarter side view, suspended just above clean
concrete, sharp shadow under sole, crisp studio flash, slight motion dust
behind heel, athletic launch campaign style, 4:5 crop with safe space upper
right for headline
```

### Coffee mug background swap

```text
preserve the uploaded ceramic coffee mug exactly, replace background with a
bright Scandinavian kitchen counter, soft morning window light from left,
realistic contact shadow and reflection on counter, warm lifestyle product
photography, no new logo, no deformation, no text
```

### Watch macro

```text
luxury watch preserved from reference image, brushed steel case, three-quarter
top-down macro, thin strip light reflected along the bevel, black velvet
surface, shallow depth of field on dial face, dark commercial grade, square
crop, no added text
```

## Quality bar

Before returning:

- Product geometry, packaging, label, and color are not invented or distorted.
- Lighting matches the material (glass gets backlit, metal gets specular highlights).
- Background does not compete with the product, it supports it.
- Composition leaves room for platform crop / copy if requested.
- No extra products or extra text in frame.
- Output paths come from `downloaded_files[]`.

## Common refinements

If the first output drifts:

- Logo distortion → re-upload at higher resolution; switch to `openai/gpt-image-2/edit` for better text fidelity.
- Wrong material feel → name the lighting recipe specifically (rim + caustics for glass, etc.).
- Background fights the product → simplify to a gradient or single-color void.
- Color shift → mention the exact color in the prompt and add "do not shift product color".

For multi-shot product narratives (hero + lifestyle + reveal video), graduate to [commercial.md](commercial.md) or [storytelling.md](storytelling.md).
