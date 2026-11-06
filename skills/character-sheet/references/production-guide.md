# Character Sheet

Produce one character design/reference sheet — hero pose, turnaround views, expressions, and detail panels — as ONE image from ONE generation call. The sheet is the identity anchor for everything downstream: every later image or video call attaches it as a reference and repeats its descriptor tokens verbatim.

**THE ONE-IMAGE LAW applies: all views and panels render together in a single call — that is WHY they match.** Never generate views as separate images; separate calls cannot share a canon.

Load references as needed:
* `references/sheet-patterns.md` — worked sheet prompts (AAA design sheet, 4-column turnaround, expression sheet, from-photo mode) and downstream binding clauses

## Inputs to collect

Ask only for what changes the sheet; default the rest and say so.
* Sheet type: full design sheet (hero + turnaround + details + palette, 16:9) or clean turnaround reference (4 columns, no text — for video identity refs).
* Source: text brief, or an existing image (edit mode — identity comes from the upload).
* Style anchor (e.g. "anime realism, premium game artbook" vs "photoreal") and any name/title text to render (goes in quotes).

## Core contract

```text
CHARACTER ANCHOR: face geometry + skin + eyes + hair (cut, color) + build +
                  signature wardrobe items (named one by one) + props
SHEET VARIABLE:   layout, views, detail panels, palette swatches
```

Descriptor tokens are permanent: "golden amber eyes" stays "golden amber eyes" in every future prompt — never paraphrase. Repair rule: drift between views → regenerate the whole sheet with a tightened anchor; never patch one view.

## Model routing (picks per fal's published routing, Oct 2026)

Inspect the model's schema and use only supported fields.
* Sheet generation: `google/nano-banana-2.1` (fal's published default, 1K–4K; with reference images use `google/nano-banana-2.1/edit` and `image_urls`; check every panel for identity drift) → `fal-ai/nano-banana-pro` when named or for an approved Pro look → fallback `openai/gpt-image-2` (long structured prompts; renders quoted name/title text cleanly) → draft `fal-ai/nano-banana-2`
* Sheet FROM an existing image: `google/nano-banana-2.1/edit` (upload = identity source; "keep the facial features exactly the same as Image 1") → `openai/gpt-image-2/edit` (`quality: "high"`)
* Angle variants of one existing render: `fal-ai/qwen-image-edit-2511-multiple-angles` (96 poses)
* Panel extraction: model-side re-render for the hero portrait ("extract the front portrait, render it full-frame"); deterministic local crop for reference thumbnails

## Workflow

1. Write the CHARACTER ANCHOR; pick a layout pattern from `sheet-patterns.md`; put any name/title text in quotes.
2. Generate ONE sheet in one call at 2K+ (4K when detail panels matter).
3. QC against the quality bar; on identity drift regenerate the whole sheet.
4. Extract panels as needed and record a local `manifest.json`: anchor text, sheet file, source references, endpoint, seed and final prompt. Reuse these files in later sessions; no hosted entity registry is required.
5. Downstream binding: attach the sheet image to every later call and scope it — "Use Image N (its position in the reference list) only for the character's final identity, wardrobe, and props."

## Retry & budget

Change ONE rung per retry: 1) anchor specificity — name each wardrobe item, count the views explicitly; 2) determinism lever — seed, or the approved sheet as an edit reference; 3) workflow tier — text → from-image edit mode; 4) fallback model. Max 3 attempts per sheet, then surface the best candidate and the next change.

## Quality bar — reject when

* Face, hair, or any named wardrobe item differs between views.
* View count or order doesn't match the requested layout (front/side/back missing or duplicated).
* Views were generated as separate images instead of one sheet.
* Name/title text renders garbled (quote it; describe the typeface, never name fonts).
* Anatomy errors (extra limbs, deformed hands), or a cluttered background when the sheet is meant as a clean reference.
* Style drifts from the anchor — photoreal creeping into an anime sheet or vice versa.

## Output contract

Report: sheet file, endpoint, seed, final prompt, the CHARACTER ANCHOR text verbatim (reusable), extracted panels, manifest path.

## Scope

This skill owns one character's identity sheet and its anchor text. Scene storyboards, multi-character boards, and animating the character are out of scope.
