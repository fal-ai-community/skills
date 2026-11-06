# Photo editing

Deterministic photo edits run with a local Python script, not through a
generative model. They are pixel-exact, repeatable, and effectively free — a
model run would re-synthesize the whole image and drift everything the user
didn't ask to change.

## Routing

Classify the request first. The test: **could a darkroom or Photoshop slider do
it?** → local workspace. **Does it require inventing new image content?** → generative
edit model.

| Request                                                                    | Route                                                       |
| -------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Brightness, exposure, contrast, saturation, white balance                  | Local Python                                                     |
| Color grading, black & white / monochrome, LUT-style looks, vignette       | Local Python                                                     |
| Crop, resize, rotate, straighten, flip                                     | Local Python                                                     |
| Format conversion (png/jpg/webp), compression, metadata strip              | Local Python                                                     |
| Watermarks, text overlays, borders, compositing images together            | Local Python                                                     |
| Sharpen, mild blur (incl. background blur via mask)                        | Local Python                                                     |
| Background removal / matting                                               | Bria model (see below)                                      |
| Change objects, faces, expressions ("make him smile", "remove the person") | Edit model                                                  |
| Inpainting, outpainting, style transfer ("make it a painting")             | Edit model                                                  |
| Upscaling, restoration, deblur/denoise beyond mild                         | Dedicated model (upscaler/restoration), never PIL resize-up |

Mixed requests split: "make it black and white and add our logo" is all
local workspace; "remove the guy in the back and crop to square" is an edit model for
the removal, then local workspace for the crop.

## Masks come from Bria, everything after is local workspace

The local workspace has **no matting library** — do not attempt segmentation with
opencv (GrabCut etc.); quality is unacceptable. For anything that needs a
subject/background split, run `fal-ai/bria/background/remove` (single job per
image, no batch; completes in seconds). It returns a transparent-PNG cutout —
the alpha channel **is** your mask.

The hybrid recipe for selective edits ("grade the background monochrome",
"blur everything behind her", "replace the background with white"):

1. Bria → cutout URL.
2. One local Python script: download original + cutout, extract
   `mask = cutout.split()[-1]`, apply the adjustment to the full frame, then
   `Image.composite(foreground, adjusted, mask)` (or paste the cutout over a
   new background).
3. Write the final image to the project output folder and inspect it.

If the user only asked to remove the background, the Bria output alone is the
answer — no local workspace step needed.

## Working in the local workspace

- Check local dependencies first: Pillow and numpy; optional image libraries
  depend on the requested operation. Do not assume they are preinstalled.
- **One script per pipeline.** Download inputs, do every step, write the final
  file to the project output folder. Don't round-trip
  intermediate steps through separate tool calls.
- Return the inspected output file through the client's supported file interface.

Key Pillow moves (write real code around these; don't guess at APIs):

- Load with `ImageOps.exif_transpose(Image.open(...))` — always, or phone
  photos come out rotated.
- Tonal: `ImageEnhance.Brightness/Contrast/Color/Sharpness`,
  `ImageOps.autocontrast`, `Image.point` for curves/levels.
- B&W with control: mix channels via numpy (e.g. luminosity weights) rather
  than `convert("L")` when the user cares about the look.
- Geometry: `crop`, `resize(..., Image.LANCZOS)`, `rotate(angle, expand=True)`.
- Compositing: convert to RGBA, `Image.alpha_composite` / `Image.composite`
  with a mask; `ImageDraw` + `ImageFont` for text.
- HEIC/HEIF input (iPhone photos): `pillow_heif.register_heif_opener()`
  before `Image.open` (`pip install -q "pillow-heif>=1.3.0"` if missing).
- RAW input (CR2/NEF/ARW/DNG): decode with `rawpy` (`pip install -q rawpy`
  if missing) — never grade the embedded JPEG thumbnail Pillow shows you.
  `raw.postprocess(use_camera_wb=True, no_auto_bright=True, output_bps=16)`
  is the neutral import; keep the result 16-bit/float through the whole
  pipeline and convert once at export.

## Measure like a colorist — scopes, not eyes

You can see the user's attached images, but only coarsely — vision gives you
semantic reads (subject, composition, "looks backlit"), not fine tonal or
color measurement. Never estimate numbers by eye. Files you create in the
local workspace need both visual inspection and quantitative checks. So
every quantitative decision comes from measured numbers, which is also how
professionals grade: by histogram and scopes, not by squinting. Print your
scopes.

- **Before editing**, run a quick measurement pass and print: per-channel
  p1/p50/p99, mean luminance, % of pixels clipped at 0 and 255, per-channel
  means (a gray-world imbalance = the cast direction), mean saturation.
- **Decide from the numbers**, not vibes: R mean 6% above G → cool it by that
  factor; p99 at 0.82 → there's highlight headroom to stretch; 3% clipped
  blacks → lift before you S-curve.
- **After editing, re-measure** and print before/after side by side. Confirm
  the targets moved as intended and nothing new clipped (>0.5% is a smell)
  BEFORE delivering the output file.

The measurement pass may be its own small Python process when the numbers
decide which aesthetic moves to make; the edit itself stays one script.

## Grading like Lightroom: normalize, then grade

For "fix the colors and make it moody / cinematic / film-look" asks, work in
two passes inside one script — a neutral baseline first, the look second.
Do the math in float32 numpy arrays in [0, 1]; convert to uint8 once at the
end (repeated 8-bit round-trips cause banding).

1. **Normalize** to a clean baseline:
   - White balance: gray-world (scale each channel to the common mean) or
     white-patch (scale so the ~99th percentile is neutral).
   - Exposure/contrast: percentile stretch (clip at ~p1/p99, rescale), or
     `skimage.exposure.equalize_adapthist` (CLAHE, `clip_limit≈0.01`) for
     flat or backlit shots.
2. **Grade** on top of the normalized base:
   - Tone curves: `np.interp` over a few control points per channel — S-curve
     for punch, lifted blacks for matte film looks.
   - Split-toning: shift shadow and highlight hues separately, weighted by a
     smooth luminance mask.
   - HSL-panel moves (targeted hue/sat shifts): `cv2.cvtColor` to HSV, adjust
     the hue range, convert back.
   - `.cube` LUTs: `pillow_lut.load_cube_file` → pass to `Image.filter` for
     any named film/teal-orange style look (`pip install -q pillow-lut` if
     missing).
3. **Match a reference look**: when the user attaches a photo with the look
   they want, `skimage.exposure.match_histograms(img, ref, channel_axis=-1)`
   is the 80% answer in one line — follow with a gentle tone curve to taste.

Show the result and iterate — grading is subjective, so expect a round or two
of "warmer", "less contrast" refinements on the same normalized base.

## Quality rules

- Preserve the input resolution unless the user asked to resize.
- Output PNG whenever transparency is involved; otherwise match the input
  format, JPEG at `quality=95` to avoid visible recompression.
- Change only what was asked — no bonus auto-enhance, no re-encoding pipelines
  that touch untargeted pixels.

## Defaults for ambiguous asks

- **"Remove the background"** → Bria. Deliver the transparent PNG; offer a
  composite (solid color / new scene) as the follow-up.
- **"Enhance / fix this photo"** → deterministic first (auto-contrast, white
  balance, gentle sharpen in one script). If the real problem is detail,
  damage, or faces, say so and offer an upscaler/restoration model instead.
- **"Retouch"** → tonal cleanup is local workspace; blemish/skin/object retouching is
  an edit model.
- Genuinely unclear whether they want a look change or a content change → ask,
  one short question, before running anything.
