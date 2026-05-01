# Photorealism Recipe

Use this recipe when the brief calls for an image that should read as a real photograph rather than an illustration, render, or AI synthesis. Realism is a discipline: every choice (lens, light, surface, posture, imperfection) compounds, and any one wrong call collapses the illusion.

This recipe does not chase "premium photoreal" through prestige adjectives. It works by naming concrete photographic facts: a focal length, a light source with a direction, a surface with a known wear pattern, a believable camera moment.

## When this recipe applies

- The user wants a single still that should pass as taken with a camera.
- Identity, product, or location must look natural in context, not staged.
- Output is for editorial, lookbook, documentary, candid social, or archival use.

If the brief is multi-shot or campaign-level, treat this as the per-frame style guide and use [storytelling.md](storytelling.md), [commercial.md](commercial.md), or [character-design.md](character-design.md) as the orchestrating recipe.

## Inputs to collect

Ask only when the answer is missing and changes the build:

- **Subject:** human, product, animal, place, scene composition.
- **Photographic genre:** candid phone, editorial portrait, documentary, studio commercial, street, archival/period, food, nature, architectural.
- **Era cue:** modern digital, late-2010s phone, mid-2010s DSLR, 35mm film 1990s, color-negative 1970s, black-and-white 1960s, daguerreotype-style.
- **Aspect ratio and crop:** vertical phone, 3:2 mirrorless, square, panorama.
- **Subject identity rules:** preserve face from a reference, generic person, stock model, age range.
- **Light source:** named (overcast daylight, north-facing window, single bedside lamp, sodium vapor street, fluorescent office, candlelight). Direction matters more than intensity.
- **Surface and texture:** ground, wall, fabric, skin, water, weathered paint. Real surfaces carry wear; named wear sells the shot.
- **Imperfection budget:** clean editorial, mild realism, heavy candid, period grain.

## Endpoint selection

For photoreal output, the curated picks live in [fal-models-catalog/text-to-image.md](../../fal-models-catalog/references/text-to-image.md) under "Premium realism." Default order:

1. `openai/gpt-image-2` at `quality=high`. Best general-purpose photoreal, accurate text inside the frame, identity-preserving with a reference image.
2. `fal-ai/nano-banana-pro`. Strong fallback. Cleaner skin rendering on close portraits in some cases.
3. `fal-ai/nano-banana-2`. Cheaper second pass when GPT Image 2 misses a specific texture cue.
4. `fal-ai/bytedance/seedream/v5/lite/text-to-image`. Best for Asian subjects and Asian-language signage realism.

For edits to an existing photo (relight, swap object, repair), see [image-to-image.md](../../fal-models-catalog/references/image-to-image.md) under "Editing, premium identity-preserving."

For prompt mechanics specific to GPT Image 2, see [fal-prompting/references/gpt-image-2.md](../../fal-prompting/references/gpt-image-2.md).

## Genmedia workflow

```bash
# 1. Inspect schema (only first time per endpoint)
genmedia schema openai/gpt-image-2 --json

# 2. Optionally upload a reference (for identity-preserving generation)
URL_REF=$(genmedia upload ./reference.jpg --json | jq -r '.url')

# 3. Run with structured prompt
genmedia run openai/gpt-image-2 \
  --prompt "<structured prompt>" \
  --image_size landscape_4_3 \
  --quality high \
  --num_images 1 \
  --output_format png \
  --download "./outputs/realism/{request_id}_{index}.{ext}" \
  --json
```

For edit-mode (preserving an existing image's geometry):

```bash
genmedia run openai/gpt-image-2/edit \
  --image_urls "$URL_REF" \
  --prompt "<edit-mode structured prompt>" \
  --input_fidelity high \
  --download "./outputs/realism/{request_id}_{index}.{ext}" \
  --json
```

## Prompt build order

Realism prompts answer six questions in order. Skipping a question is fine; reordering them is not.

1. **Who or what.** Subject in plain noun form. Avoid stock-photo phrasings ("a person", "a businessman"). Use specific roles: "a fruit vendor in his fifties", "a teenage daughter mid-conversation".
2. **What they are doing.** Verb in continuous tense. Avoid frozen poses. "Adjusting her sleeve while listening" beats "standing".
3. **Where, with one anchoring detail.** Location plus one concrete physical thing that proves the location is real. "A municipal pool changing room with chipped sky-blue tiles" beats "a pool".
4. **Light.** Named source, direction, time of day, temperature. "Overcast 11am window light from camera left, cool blue cast" beats "soft natural light".
5. **Camera.** Focal length feel, distance, framing, shutter feel. "50mm at portrait distance, locked-off, mid-shutter so the hand has a hint of motion" beats "35mm lens".
6. **Imperfections.** Two or three concrete real-camera artifacts that anchor the image: lens vignette, mild barrel distortion at wide ends, light bloom near practical lights, JPEG compression character, sensor noise, film grain, hair fly-aways, skin pore visibility, fabric creases, dust on a lens, condensation on glass, paint chipping, fingerprint smudges.

## Two orthogonal axes: genre and era

A realism prompt is a combination of two independent choices:

- **Genre** answers "what kind of photo is this?" (a candid, an editorial portrait, a documentary frame, a studio shot, food, nature, architecture, street).
- **Era and stock** answer "when and on what was it captured?" (today on a phone, 2018 on a mirrorless, 1995 on Portra 400, 1972 on Kodachrome, 1962 on Tri-X, 1880s tintype).

The two are independent. A 1990s 35mm look can be applied to a candid, an editorial portrait, a food shot, or a street frame. A modern phone look can be candid or editorial. Pick one from each axis and commit. Mixing inside an axis (two genres at once, two eras at once) produces the AI-render look.

## Genre families

Each family is a coherent set of camera, light, posture, and imperfection choices. Pick one and commit.

### Contemporary phone candid

The default for "photo of a real moment". Reads as a Pixel or iPhone shot from the last few years.

- Lens feel: 24-26mm equivalent, slight wide perspective, faint barrel distortion at frame edges.
- Light: ambient, color-mixed, often slightly overexposed at window-facing surfaces.
- Sensor character: heavy computational HDR, shadow lift, slight halo around high-contrast edges.
- Posture: candid, off-axis, subject not facing camera dead-on.
- Imperfections: motion blur on hands, mild rolling-shutter on motion, autofocus locked on the wrong point occasionally, JPEG noise in shadows, screen reflections, lens flare from a specific source.
- What to avoid: studio rim lights, perfect skin, symmetrical composition, magazine framing.

### Editorial portrait

The default for "professional but real human" briefs.

- Lens feel: 85-105mm portrait length, compressed perspective, shallow depth (subject sharp, background creamy).
- Light: large soft source from one side at a 30-45 degree elevation, weak fill from the opposite side, optional rim from behind.
- Color: subtle warm-cool split (warm subject, cool ambient), neutral skin.
- Posture: directed but lived-in. Subject looks like they breathed between frames.
- Imperfections: visible skin pores at portrait distance, individual hairs separated against the background, fabric weave readable, single catch-light in each eye.
- What to avoid: flat front-on key light, plastic skin, pupils centered, both eyes equally lit.

### Documentary / photojournalism

For street, interior, or in-the-moment captures.

- Lens feel: 28-35mm wide-normal, deep enough focus that environment reads.
- Light: only what is in the scene. No fill. If it is night, the image has shadows where shadows belong.
- Color: faithful, sometimes muddy, frequently mixed temperatures.
- Posture: people doing their thing. The photographer is not the subject's focus.
- Imperfections: a foreground element partially blocks the subject (a passerby's shoulder, a doorframe edge), focus is on the subject but the depth of field is honest, tilt is slightly off.
- What to avoid: clean backgrounds, posed expressions, lit-from-everywhere, magazine grade.

### Studio commercial photoreal

For product hero shots, fashion lookbook, beauty.

- Lens feel: 50-100mm depending on subject, careful subject-to-background isolation.
- Light: shaped, named, directional. "Octa key from upper left at 45 degrees, white v-flat fill on right, edge light from behind on subject's hair."
- Surface: deliberate. Backdrop is paper, fabric, set, or location, named.
- Posture: directed. Subject knows the camera exists.
- Imperfections: a shadow exists somewhere visible, a single hair out of place, the subject's hand has texture, the edge of the backdrop curves.
- What to avoid: floating subjects with no shadow, backdrop seamlessly merged into infinity, skin that has been retouched into a smooth surface.

### Food

- Lens feel: 50mm or 100mm macro, downward angle 30-60 degrees, depth shallow enough to taste.
- Light: window light from one side, no flash. Steam and condensation only when plausible.
- Surface: real plate or fabric, slight crumbs or sauce drips visible.
- Imperfections: an unfilled corner of the plate, a slightly off chopstick, a thumbprint on the rim.

### Nature / landscape

- Lens feel: 16-35mm for environment, 70-200mm for compression.
- Light: time of day named precisely. "Blue-hour 20 minutes after sunset, sky still bright at the horizon, foreground rocks in deep shadow."
- Imperfections: dust on the sensor visible in sky, lens flare from the actual sun direction, slight haze in distant midground.

### Architectural / interior

- Lens feel: 24mm for full room, 17mm tilt-shift for full geometry control.
- Light: motivated. Every brightness in the frame has a source visible or implied.
- Imperfections: a power outlet, a smudge on a window, a slightly bent picture frame, the imperfect ceiling line where two paint shades meet.

## Era and stock cues

This is the second axis. Pick one stock and stick to it. The cues below are starting points; for any specific year, lens, or film not listed, name it concretely and the model will follow.

### Modern digital (default for "current" briefs)

- **2024-2025 flagship phone (Pixel 9, iPhone 16, Galaxy S25)**: heavy computational HDR, sharp center, slight halo on high-contrast edges, deep shadow recovery, slightly cool color science, 24mm equivalent, sometimes a 48mm "portrait mode" with synthetic bokeh.
- **2024-2025 mirrorless (Sony A7, Canon R, Fuji X-T)**: clean color, accurate skin, optional film simulation, full-frame depth-of-field separation, shutter feel from a real lens.
- **2024-2025 cinema camera (RED, ARRI, Sony FX)**: log color profile, deeply graded look, organic motion blur, no computational HDR.

For a "looks like a photo I just took" output, default to the flagship phone cue. For "professional shoot today," default to mirrorless.

### Late-2010s digital (the social-media-native era)

- **2018-2020 phone (iPhone X-12, Pixel 3-5)**: noticeable HDR halo, warmer skin tones, slight chromatic aberration at corners, 28mm equivalent, less aggressive computational fill than current phones.
- **2015-2019 DSLR (Canon 5D Mark IV, Nikon D850)**: clean files, deeper bokeh than phones of the era, neutral or warm color science, real lens character.
- **2017-2020 mirrorless (Sony A7 III, Fuji X-T3)**: sharp, color-accurate, popular for editorial work of the period.

### Early-2010s digital (the start of high-quality social capture)

- **2011-2014 phone (iPhone 4s-6, Galaxy S3)**: lower dynamic range, blown highlights more common, simpler color processing, square crop popular (early Instagram), occasional flash use indoors that looks harsh.
- **2010-2014 DSLR (Canon 5D Mark II, Nikon D700)**: shallow depth-of-field obsession, warmer color, popular for the wedding-and-portrait look of the period.

### Late-2000s digital (the point-and-shoot era)

- **2005-2010 compact (Canon PowerShot, Olympus, Casio Exilim)**: small sensor character, visible noise above ISO 400, on-camera flash with hard shadow behind subject, JPEG-only with mild compression artifacts, slightly soft 35mm equivalent.

### Early-2000s digital (the first wave)

- **2001-2005 entry digital (Canon Rebel XT, Nikon D70, Sony Cyber-shot)**: 4-8 megapixel resolution feel, visible noise even at base ISO, white balance that misses warm interiors, on-camera flash dominant indoors, time stamps in lower-right corner consistent with the era.

### 1990s 35mm film

- **Kodak Portra 400 (warm portraits, weddings)**: faint warm shift, low-saturation greens, smooth grain, soft highlight roll-off, mild halation around lit edges.
- **Kodak Gold 200 (consumer/family)**: punchier saturation, magenta-leaning, visible grain at scan-size crop.
- **Kodak Tri-X 400 (B&W documentary)**: high mid-tone contrast, gritty grain in shadows, deep blacks.
- **Fuji Superia 400 (consumer/Japanese)**: greener cast, cooler shadows.
- **Disposable camera**: harsh on-camera flash, red-eye, vignette, color shifts, scratches and dust on the scan.

### 1980s

- **Polaroid SX-70 / 600**: square format, milky highlights, soft focus, visible white border, color drift.
- **35mm consumer color (Kodachrome 64, Ektachrome 100)**: Kodachrome's saturated reds and slow film stillness; Ektachrome's cyan-leaning shadows.
- **Direct-flash snapshot**: hard shadow behind subject, eyes red, foreground over-lit, background under-exposed.

### 1970s

- **Color negative on faded paper**: orange-magenta cast, lifted blacks, soft overall contrast, paper-grain visible at edges, occasional yellowed top corner.
- **National-Geographic-style 35mm**: Kodachrome 64 saturation, deep daylight blue, warm skin, sharp 50mm normal lens.

### 1960s

- **Tri-X 400 newspaper-style B&W**: high contrast, paper grain, square or 6x6 medium-format crop, posed stillness from slow shutter requirements.
- **Slide film (Kodachrome 25)**: super-saturated, low ISO, very sharp at base, bright sunny outdoor work.

### 1950s and earlier

- **Mid-century B&W (large-format Speed Graphic)**: 4x5 sheet film grain, deep tonal range, formal posing, on-camera flash bulb with hard shadow.
- **1940s tabloid B&W**: high contrast, hard flash, journalistic angles.
- **1900-1920 sepia / silver gelatin**: warm tone, soft optics, unsmiling formal posture, visible plate edges.
- **1850s-1880s daguerreotype / tintype**: silvered plate tone, tunnel vignette, frozen pose from minutes-long exposure, plate damage at edges.

### Combining genre and era

Examples of combinations the model handles cleanly:

- Editorial portrait genre + 2024 mirrorless era = a current professional headshot.
- Editorial portrait genre + 1995 Portra 400 era = a wedding portrait that reads as 1995.
- Documentary genre + 1962 Tri-X era = a Pulitzer-style mid-century news photo.
- Candid phone genre + 2024 flagship era = a "shot just now" feed image.
- Food genre + 1985 Kodachrome era = a vintage cookbook photo.
- Architectural genre + 1972 color negative era = a faded brochure interior.

If the brief does not name an era, default to **2024 flagship phone** for candid genres and **2024 mirrorless** for editorial, studio, food, nature, and architectural genres.

## Anti-AI-look checklist

Run through this before submitting any "realistic" prompt. Each item is a common AI tell.

- **Skin is a single smooth surface.** Demand pores, faint discoloration, asymmetry, freckle pattern, texture variation across the cheek.
- **Hair is a hat.** Demand individual flyaways, separation against background, color variation in different lights.
- **Eyes are perfect mirrors.** Demand a single specific catch-light source, capillaries, slight redness, asymmetric eyelid weight.
- **Hands are too many or too few.** Specify count and position. Realism prompts that mention hands at all should anchor them.
- **Light comes from everywhere.** Name one primary source. Shadows on the subject must be consistent with that one source.
- **Backgrounds are seamless gradients.** Demand a real wall, a real surface, a real depth, a corner, a shadow.
- **Compositions are dead-center.** Off-center subject, asymmetric balance, accidental framing.
- **Everything is in focus.** Pick what is sharp and what is soft, name the focal plane.
- **Subjects look at the camera.** Most candid moments do not. Specify gaze direction.
- **Color palettes are uniform.** Real scenes have temperature mixing. Name two sources at minimum if both should appear.
- **Posture is symmetric and centered.** Real bodies are weighted on one leg, leaned, half-turned.
- **No one is mid-action.** Real candids catch motion. Specify the verb.

## Identity preservation

When the brief includes a specific person (uploaded reference, named character, recurring subject):

- Use `openai/gpt-image-2/edit` with `input_fidelity=high` and the reference uploaded.
- In the prompt, lead with: "Preserve the face, hair color and texture, body proportions, and identity from the reference image. Change only [scene / pose / wardrobe / lighting]."
- Avoid re-describing facial features in the prompt; the reference does this. Verbal description fights the reference and produces drift.
- For multi-shot character continuity, see [character-design.md](character-design.md) for the anchor system.

## Examples

### Contemporary phone candid

```text
Subject: a man in his late thirties, lightly stubbled, navy work jacket, holding a coffee cup with the lid slightly askew.
Action: laughing at something off-frame, head turned a few degrees away from camera, free hand gesturing.
Setting: a small bakery counter at 9am on a Tuesday, marble counter scratched at the edges, a glass case of pastries reflecting the back-of-shop fluorescent.
Light: window light from camera right, slightly blown highlights on the counter edge, mixed warm-fluorescent ambient inside.
Camera: 26mm equivalent, smartphone height, autofocus on the cup not the face, subject slightly off-center.
Imperfections: motion blur on the gesturing hand, a sliver of someone's elbow at the right edge of frame, JPEG halo around the lit counter edge, faint screen reflection visible on the glass case.
Constraints: no studio lighting, no rim light, no model-style posing.
Aspect: 4:3 vertical phone crop.
```

### Editorial portrait

```text
Subject: a woman in her fifties, short silver-grey hair, dark olive shirt, light makeup so skin texture reads, a single small silver earring.
Action: mid-pause in a sentence, lips just parted, looking past the camera at someone the viewer cannot see.
Setting: a quiet office with one large window, books in soft focus behind her, a brass desk lamp visible in the upper-right corner.
Light: north-facing window from camera left at 45 degrees elevation, subtle warm fill from the brass lamp on the right side of her face, weak rim from a back-of-room fluorescent.
Camera: 85mm portrait length, head-and-shoulders crop, eyes on upper third, depth shallow enough that the books behind are creamy but the earring stays sharp.
Imperfections: visible pore detail on the cheek closest to camera, individual hair strands separated against the background, single warm catch-light in each eye, a faint line where her glasses sometimes rest.
Constraints: no full smile, no straight-to-camera gaze, no flat front lighting.
Aspect: 4:5.
```

### Archival 35mm 1990s

```text
Subject: two children, brother and sister, ages around 8 and 11, in summer clothes, the boy holding a half-melted popsicle.
Action: standing in front of a station wagon, the girl mid-laugh, the boy looking at the popsicle with concern.
Setting: a gas station forecourt in late afternoon, beige stucco walls, a hand-lettered sign in the background partially out of focus.
Light: golden-hour sun from camera right, long shadows extending to camera left, warm light reflected off the beige stucco onto subjects' faces.
Camera: 35mm film point-and-shoot equivalent, modest depth of field, slight barrel distortion at frame edges, frame slightly tilted.
Imperfections: visible Portra-style grain, mild halation around the brightest highlights, color shifted toward warm orange in the shadows, edge of frame slightly soft on the right side, a date stamp or absence of one consistent with a 1990s family snapshot.
Constraints: no digital sharpness, no smooth gradients, no contemporary clothing brands.
Aspect: 3:2 horizontal.
```

### Documentary night street

```text
Subject: a flower vendor closing up his stall, a man in his sixties, jacket zipped, breath visible in the cold air.
Action: lifting the last bucket of unsold roses, half-turned away from camera, one hand bracing the bucket from below.
Setting: a city sidewalk at 11pm in late autumn, sodium-vapor streetlight overhead, a closed bakery's grille pulled down across the storefront behind him, wet pavement reflecting amber.
Light: only the sodium-vapor lamp, directly above, hard shadows under the brim of his cap, warm-amber color cast saturating the entire scene.
Camera: 28mm wide, low shutter speed so motion is honest, photographer is across the street and the roses are softly between camera and subject in the lower frame.
Imperfections: motion blur on the lifting hand, sodium-vapor color cast eating skin tones, a passerby's leg cropped into the right edge of frame, slight handheld tilt, grain in the dark areas.
Constraints: no fill light, no rim light, no clean color separation.
Aspect: 3:2 horizontal.
```

## Quality bar

Before returning, walk through the anti-AI-look checklist. If any item fails, do not iterate on the prompt with more adjectives. Instead:

- Add concrete imperfections by name.
- Re-read the light description and force a single primary direction.
- Re-read the posture and verb. If the subject is "standing," replace with what they are doing in the half-second the photo was taken.
- Cut every prestige adjective. "Beautiful," "stunning," "cinematic-quality," "photorealistic" are signals to the model that the prompter does not know what to ask for.

If a result still fails realism, switch to edit-mode against a real reference photograph rather than text-to-image. Photoreal text-to-image is honest about its limits at the edges of the genre (specific named locations, copyrighted faces, complex hand interactions). Edit-mode handles those by anchoring the synthesis to a real frame.

## Common parameters

```bash
genmedia schema openai/gpt-image-2 --json
genmedia schema fal-ai/nano-banana-pro --json
genmedia schema openai/gpt-image-2/edit --json
```

Frequently exposed:

- `prompt`: the structured prompt above.
- `image_size`: realistic ratios are `landscape_4_3`, `portrait_3_4`, `square`, or custom (`1920x1280`, `1080x1350`).
- `quality`: `high` for any output that should pass as photographic. Drafts at lower quality are misleading.
- `num_images`: generate 2-4 variants and pick. Realism is partly luck of the seed.
- `output_format`: `png` for archival, `jpeg` for shipped social.
- `input_fidelity` (edit only): `high` to preserve a reference's geometry.
- `seed`: lock once you have a winning frame so micro-iterations stay in the same neighborhood.

## Cross-references

- Endpoint selection: [fal-models-catalog/text-to-image.md](../../fal-models-catalog/references/text-to-image.md), [image-to-image.md](../../fal-models-catalog/references/image-to-image.md).
- Prompt mechanics for the dominant family: [fal-prompting/references/gpt-image-2.md](../../fal-prompting/references/gpt-image-2.md).
- For cinematic film-still framing (different goal, related vocabulary): [cinematography.md](cinematography.md).
- For multi-shot narratives that demand realism on every frame: [storytelling.md](storytelling.md).
- For commercial / product realism specifically: [commercial.md](commercial.md), [product-shot.md](product-shot.md).
- For preserving a specific person across multiple realistic frames: [character-design.md](character-design.md).
