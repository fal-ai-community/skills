# Prompting GPT Image 2

OpenAI's image model on fal.ai. Excels at detailed images with fine typography. Three modes: text-to-image, edit, and multi-image compositing.

Endpoints:

- `openai/gpt-image-2`: generate from prompt
- `openai/gpt-image-2/edit`: edit one image (or composite up to 16)

## Key strengths

- Superior text rendering and typography (significantly better than 1.5)
- UI / interface design with proper hierarchy
- Detail preservation in photoreal and editorial photography
- Reliable object placement and geometric accuracy in edits
- Up to 16 reference images for compositing tasks

## Prompt structure: five-section template

GPT Image 2 responds to organized, structured input:

```text
Scene: [environment, lighting, time of day]
Subject: [main focus, who/what]
Important details: [materials, texture, lighting, camera angle, mood]
Use case: [editorial photo, product mockup, UI screen, etc.]
Constraints: [no watermark, preserve face, no logos, etc.]
```

The fifth slot is where most mediocre prompts fail silently. Describe the idea without bounding it and the model gets inventive in directions you will regret.

## Anti-slop rules

**1. Visual facts beat vague praise.** Replace "stunning, incredible, masterpiece" with "overcast daylight, brushed aluminum, soft bounce light, 50mm feel."

**2. Style tags need visual targets.** Instead of "minimalist brutalist editorial," specify "cream background, heavy black sans serif, asymmetrical type block, generous negative space."

**3. Say the real thing.** Use explicit language. "transit kiosk", "boarding pass", "preserve the face", rather than mood language.

**4. In edits, separate change from preserve.** Structure edits with clear "change only X" and "keep everything else the same" sections.

**5. Treat text like typography.** Wrap literal text in quotes or ALL CAPS; specify font style, size, color, placement. Spell difficult words letter-by-letter if needed.

**6. One revision per turn.** Small iterative edits outperform giant rewrites.

## Three operational modes

### Mode 1: Generate from scratch

Endpoint: `openai/gpt-image-2`

Use cases: editorial photos, posters, product scenes, UI screenshots, illustrations.

Apply the five-section template above.

### Mode 2: Edit one image

Endpoint: `openai/gpt-image-2/edit`

Use cases: object replacement, clothing changes, background removal, relighting, weather swaps.

```text
Change: [exactly what should change]
Preserve: [face, identity, pose, lighting, framing, background]
Constraints: [no extra objects, no watermark]
```

### Mode 3: Combine multiple images

Label each input by role and reference the labels in the instruction:

```text
Image 1: base scene to preserve.
Image 2: jacket reference.
Instruction: Dress the person from Image 1 using the jacket from Image 2.
Preserve the face, body shape, pose, background, lighting from Image 1.
```

Up to 16 input images supported; always assign a role to each.

## Text-in-image patterns

GPT Image 2 is the strongest fal.ai endpoint for accurate readable text inside generated images. To get clean typography:

- Wrap exact text in quotes: `the sign reads "GRAND OPENING"`
- Or use ALL CAPS for the literal: `text on the cup: HELLO WORLD`
- Specify font: `bold serif, condensed sans, hand-lettered`
- Specify placement: `centered upper third`, `bottom-left corner`
- Add `no extra words`, `no duplicate text`
- Spell hard words letter-by-letter if drift occurs: `"X-R-A-Y"`

## Pattern examples

**Photoreal:** describe the photograph with lens choice, surface wear, ordinary background detail, believable imperfection. Include named light sources and specific materials.

**Product:** material accuracy, lighting consistency, label fidelity, clean use case. Example: "museum archive photograph...under soft overhead museum light...neutral beige backdrop."

**UI / Screenshots:** screen type, hierarchy, exact copy, state, layout logic, typography behavior. Include "clean survival HUD along the bottom, believable UI spacing."

**Edits, three-sentence pattern:**

1. What changes.
2. What stays.
3. Physical realism (lighting match, contact shadow, perspective consistency).

**Style transfer:** name the parts. "Chunky pixel forms, limited arcade palette, bright glow accents, clean silhouette edges, playful 1980s poster energy."

**Character consistency:** first image establishes anchor (clothing, proportions, palette). Second image repeats anchor details with instruction "do not redesign the character."

## Vague vs visual

**Weak:**

```text
A stunning ultra-detailed cinematic masterpiece of a woman in a museum,
beautiful, photoreal, 8K, award-winning.
```

**Strong:**

```text
Scene: museum gallery, late afternoon, soft overhead spotlights.
Subject: a woman in her 30s in a charcoal wool coat standing three meters from
a marble bust, looking sideways at the artwork.
Important details: 50mm lens feel, shallow depth of field, neutral cream walls,
warm tungsten accent on the bust, cool ambient on her face.
Use case: editorial magazine photo.
Constraints: no watermark, no logos, no heavy retouching, single subject in
focus.
```

## Common parameters

Run `genmedia schema openai/gpt-image-2 --json` for authoritative list. Typical:

- `prompt`: the structured prompt above
- `image_size`: `landscape_4_3`, `square`, `portrait_3_4`, custom dimensions
- `quality`: `high` for production; lower tiers for drafts
- `num_images`: quantity per request
- `output_format`: `png`, `jpeg`, `webp`
- `input_fidelity`: for edits, `high` enforces strict preservation
- `image_urls`: array for edit / compositing modes
- `mask_image_url`: optional mask for edit mode

## Quick code example

```bash
genmedia run openai/gpt-image-2 \
 --prompt "<five-section structured prompt>" \
 --image_size landscape_4_3 \
 --quality high \
 --num_images 1 \
 --output_format png \
 --download "./out/{request_id}_{index}.{ext}" \
 --json
```

For edits, swap to `openai/gpt-image-2/edit` and pass `image_urls` (array) plus optional `mask_image_url`.
