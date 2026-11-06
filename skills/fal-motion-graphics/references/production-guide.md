# Motion Graphics

**Revision 2026-10-28a.** Name this revision in the delivery; an upload that
cannot quote it is an older copy of this skill.

A cut can be edited well and still look cheap, and the place it looks cheap is
the graphics: bitmap-default type that pops on and off in one frame, no plate,
no grid, no relationship to the brand or the footage. This skill owns the
**design and motion of everything burned over the picture** — and it is written
to be executed, not interpreted: every measurement derives from one unit, every
motion is a keyframe formula, and two agents following it produce the same
frames.

**What this skill does not own.** The strings come from the brief or
`fal-script-writer` and are never written here. *When* graphics burn — last,
after every re-rendering step — is `fal-video-production` stage 8's ordering
rule. Caption *timing* from spoken audio comes from scribe-v2 word timings as
`fal-audio-generation` describes; inside a pipeline this skill burns those
captions as the Caption block (Step 5), in the same encode as every other
overlay. A standalone caption job with no stage-8 burn goes to
`video-compositing`.
Logo clear space and any minimum width come from the brand files or the
brand's official site, as `branded-graphics` sources them. This document calls no model.

## Step 0 — How this skill is entered

**Loaded as a reference by `fal-video-production` stage 8**: make zero
`ask_user_questions` calls — the pipeline's intake already ran. Apply Steps 1–5
to every `overlay` row and, when stage 8b asks for captions, to the Caption
block, and print the Step 6 lines.

**Triggered standalone** ("animate my titles", "these graphics look basic"): at
most **one** card, header `Look`, and only when there is no style direction at
all — no brand kit, no supplied colours or fonts, no reference (on a host with no question tool,
one plain message, then in the same turn proceed on the defaults and say so).
With no answer,
proceed on the defaults below and say so at delivery — never stall a burn on a
style question. If captions are also owed on the same file, the whole burn
goes to `video-compositing`, with Steps 1–3 and 5 here as the design spec
(video-compositing renders it as HTML text; Step 4 does not apply except 4a, run on the source before rendering, and 4d, run on the rendered
MP4).

| Unstated | Default used |
|---|---|
| Colour | sampled from the footage (Step 1.4), stated at delivery |
| Font | the Step 1.2 ladder's best real TrueType, named at delivery |
| Motion | `fade-rise` for text, `scale-settle` for the end card |
| Platform | the delivery aspect decides the safe areas (Step 1.5) |

## Step 1 — The design system

Motion cannot rescue a badly designed frame. Settle these five, in order, once
per ad — not per overlay.

### 1.1 The unit grid — everything derives from cap height

Let `S` = the frame's short edge in pixels and `C` = the title's cap height:
**`C = 0.12 × S`** for a title (legal band 9–16%), **`0.03 × S`** for an
eyebrow, **`0.055 × S`** for a lower-third name line.
Every other measurement is a multiple of the overlay's own `C`:

| Measurement | Value | Why a ratio |
|---|---|---|
| Plate padding | `0.9C` horizontal, `0.6C` vertical | breathing room scales with the type it protects |
| Corner radius | `0.25C` | a fixed radius looks bulbous on small plates and sharp on large ones |
| Eyebrow-to-title gap | `0.5C` of the title | — |
| Shadow offset | `0.04C`, blur `0.08C`, black at 60% alpha | — |
| Stroke (only on unplated type) | `max(2, round(0.05C))` px | plated type gets no stroke — the plate is the separation |
| Max text width | `0.8 ×` frame width, minus safe areas | a line that spans the frame reads as a banner ad |
| Tracking | uppercase eyebrows `+8` to `+12%`; display titles `−2` to `0%`; body and captions `0%` | open caps read as a label, tight display type reads as one shape |

A pixel value chosen by eye at one resolution is wrong at every other one; a
ratio survives. The numbers above are the whole scale; there is nothing
further to load.

### 1.2 The font ladder — and the one font that is banned

**PIL's `load_default()` is forbidden.** It is a tiny bitmap face that cannot
scale, and it is the single most likely cause of "the graphics look very
simple" — an agent under momentum reaches for it because it needs no file. The
ladder, in order, with the choice printed:

1. **A brand font file** — supplied by the user or named in the brand assets
   the user supplied. Use it for everything.
2. **A real grotesque already on the machine.** Find one:
   `fc-list | grep -iE "inter|helvetica|arial|roboto|dejavu"` (or on hosts
   without fontconfig, look in the standard system font directories). Prefer
   them in that order; take a Bold or SemiBold weight for titles, Regular for
   eyebrows.
3. **DejaVu Sans Bold** — ships with almost every PIL install, serviceable and
   never embarrassing. If even this is missing, say the burn ran without a
   scalable font and mark the type check failed — do not fall through to the
   bitmap default.

One family per ad, two weights maximum, loaded with `ImageFont.truetype` at a
pixel size that yields the Step 1.1 cap height (measure a capital "H" with
`getbbox` and scale the point size until it matches `C` within 2 px — point
size is not cap height, and assuming it is produces type ~30% smaller than
specified).

### 1.3 Something legible sits behind the type

Raw type on moving footage reads as an afterthought. One treatment per ad,
reused, with these specs:

| Treatment | Spec | Use when |
|---|---|---|
| Gradient scrim | transparent → black at 65% alpha, ramp height `2.2×` the text block, darkest at the frame edge the text sits near | text near an edge over busy footage |
| Blur plate | the footage under the plate, Gaussian blur radius `0.010 × S`, darkened 25%, rounded `0.25C`, plus the text block's padding | mid-frame lower thirds — keeps the picture present |
| Solid bar | flat brand-colour panel at 100% alpha, same padding and radius | strongest hierarchy: prices, offers, end cards |

The pipeline's clearance check (contrast against what is behind the overlay)
still runs; the treatment is how a `not clear` region gets fixed without moving
the lockup.

### 1.4 Colour comes from somewhere real, never per-ad whim

In order: colours from the brand files or the brand's official site, as
`branded-graphics` sources them → colours the user stated → **sampled from
the footage**: take the hero
shot's mid-frame, downscale to 64×64, take the most common hue bucket as the accent, clamp its saturation to
0.5–0.8 so a grey frame does not yield a grey accent. A sampled colour is an
accent, not a brand colour; say so at delivery. Type colour is
mechanical, not aesthetic: relative luminance of the plate under it `< 0.45` →
white type; otherwise near-black `#111111`. Pure `#000000` on video looks like
a hole; pure white on a white plate is invisible — the luminance rule prevents
both. Name the source used at delivery.

### 1.5 Vertical deliveries respect platform chrome

On 9:16 feeds, platform UI sits on top of the ad: engagement rail on the
right, caption and CTA across the bottom, account name top-left. Keep every
overlay inside the middle band — clear the **bottom 25%, the right 12% and the
top 8%** — and treat those zones as unusable even when they look empty in the
file. On 16:9 and 1:1, a plain 5% title-safe inset on all sides. These insets
are platform conventions, not constants; when the platform is known, check its
current spec rather than trusting these figures.

## Step 2 — The motion vocabulary, keyframe-exact

**Every overlay gets an entrance and an exit.** Type that cuts on and off in a
single frame is the strongest "no design happened here" signal. A hard cut-in
is permitted as a deliberate beat — a price slam — and is named as a choice in
the delivery, never left as a silent default.

Two easing functions cover everything. With `u = t / D` clamped to `[0, 1]`:

```
ease_out(u) = 1 - (1 - u)**3        # entrances: fast start, soft landing
ease_in(u)  = u**3                  # exits: soft start, fast leave
```

Linear motion reads mechanical; spring-with-overshoot reads like a template.
Neither is used. Each vocabulary item is a set of property tracks — opacity
`α`, vertical offset `y` (relative to final position), scale `s`, reveal mask
`m` — evaluated per frame from the eased progress `p`:

| Name | Entrance (`p = ease_out`) | Exit (`p = ease_in`) | In / out duration | Use |
|---|---|---|---|---|
| `fade-rise` | `α = p`, `y = (1-p) × 0.3C` below final | `α = 1-p`, `y = -p × 0.2C` (continues up) | 300 ms / 200 ms | the default for lower thirds and eyebrows |
| `slide-in` | enters from nearest edge: `x = (1-p) × (edge distance)` , `α = min(1, 2p)` | reverse of entrance | 350 ms / 250 ms | badges and banners tied to an edge |
| `scale-settle` | `s = 0.96 + 0.04p`, `α = p` | `α = 1-p`, `s` stays 1.0 | 500 ms / 300 ms | end cards, logo cards — weight without bounce |
| `wipe-reveal` | mask sweeps left→right: `m = p ×` text width; type static | `α = 1-p` | 400 ms / 200 ms | titles over a clean field |
| `word-pop` | word `i` starts at `i × 130 ms`: over 110 ms, `s = 0.9 + 0.1p`, `α = p` | all words `α = 1-p` together, 200 ms | per word / 200 ms | TikTok-style kinetic captions |

The plate animates **with** its type as one group — a plate that arrives on a
different curve from its text reads as two mistakes. One text motion and one
card motion per ad, reused; mixing entrances within one ad is noise. The
Caption block's `word-pop` and its stroke-and-shadow treatment do not count
toward the one text motion or the one treatment.

`word-pop` synced to the voiceover takes its per-word start times from the
scribe-v2 transcript (`type == "word"` entries, per `fal-audio-generation`) —
never guessed from duration. Script-driven
text with no audio to sync divides its window evenly and says so.

## Step 3 — The timing arithmetic

Motion spends seconds the window has to contain:

- **Hold**: full-opacity time `≥ max(1.0 s, characters ÷ 15)` — the reading
  floor. Below it the viewer sees motion but not the message.
- **Fit**: `entrance + hold + exit ≤ the overlay's window`.
- **Word-pop fit**: `(word count × 130 ms) + pop + hold + exit ≤ window` — the
  stagger is part of the entrance and it is the term that overflows first.

When they conflict, shrink the motion to half its stated duration **before**
touching the hold. If it still does not fit, the window is too short for the
string — that goes back to the manifest as a window change or a shorter
string, decided there, not absorbed here by flashing text nobody can read.

## Step 4 — Render deterministically, in one pass

**Type and logos never pass through a generative model** — an edit model
redraws, it does not composite, and a redrawn wordmark is the oldest failure in
this corpus. All motion renders locally: free, repeatable, provably untouched.

**4a. Probe the cut first, and print it.** `ffprobe` the delivered cut for
width, height, fps and duration; print all four. Every frame count below is
`duration × this fps`, and rendering at a guessed 30 fps onto 24 fps footage
stutters exactly once per five frames — visible, and invisible in any still.

**4b. Render each overlay as a full-frame RGBA PNG sequence.** For each frame
`k` of the overlay's window: compute `t = k / fps`, decide which phase it is in
(entrance / hold / exit), get eased `p`, evaluate the property tracks, and draw
plate then type at the computed position, opacity and scale onto a transparent
canvas the size of the frame. Baking position into full-frame frames — rather
than positioning a small image at overlay time — is deliberate: it makes the
ffmpeg step below trivial and identical for every overlay, which is one
mechanism instead of two. Frames land in the run's work directory, named
`ov3_0001.png` style, and are kept with the stems: a styling change is then a
re-render of PNGs, never of video.

**4c. Burn every overlay in ONE ffmpeg encode.** Chained re-encodes degrade the
footage a little each time and five overlays burned sequentially is five
generations of loss — the same shape as the house rule against chained edits.
One `filter_complex`, all sequences as inputs, each shifted to its window and
overlaid in sequence:

```
ffmpeg -i cut.mp4 \
  -framerate {fps} -i ov1_%04d.png \
  -framerate {fps} -i ov2_%04d.png \
  -filter_complex "\
    [1:v]format=rgba,setpts=PTS-STARTPTS+{t1}/TB[o1];\
    [2:v]format=rgba,setpts=PTS-STARTPTS+{t2}/TB[o2];\
    [0:v][o1]overlay=0:0:eof_action=pass[v1];\
    [v1][o2]overlay=0:0:eof_action=pass[v]" \
  -map "[v]" -map 0:a -c:a copy -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4
```

`eof_action=pass` is what lets a short sequence end without freezing its last
frame over the rest of the cut; `-c:a copy` keeps the stage-7 mix untouched, so
this step cannot un-duck the music.

**4d. Prove the burn landed.** Extract one frame from the middle of each
overlay's hold and confirm the overlay is present and fully opaque there —
programmatically (the region differs from the pre-burn cut) rather than by
glance. Print one line per overlay. The pipeline's stage-9 vision pass is the
backstop, not the check.

The one legitimate generative path: a **card the user wants brought to life
generatively** — the poster treatment, parallax on an end frame — has no
published owner. Never imitate it here with a video model: render the card with
the Step 4 burn under this skill's type and safe-area rules, and say so.

## Step 5 — The component library

Named components, so "add a lower third" resolves to one spec instead of a
fresh improvisation. Position anchors are after safe-area insets (Step 1.5).

| Component | Layout | Type levels | Treatment | Motion |
|---|---|---|---|---|
| Lower third | anchored lower-left, baseline at 72% of frame height on 9:16 (above the chrome zone) | eyebrow + name line | blur plate | `fade-rise` |
| Title | optical centre, 40% of frame height | title, optional eyebrow above | gradient scrim or none on a clean field | `wipe-reveal` or `fade-rise` |
| Price / offer badge | upper-right inside safe area | one line, title scale × 0.7 | solid bar | `slide-in` from right |
| CTA banner | centred, 65% of frame height — never in the bottom chrome | one line | solid bar | `fade-rise`, holds to the cut's end |
| End card | near-empty field, title low and centred, eyebrow above, logo with its brand clearspace | eyebrow + title + logo | solid field in brand colour or footage still with scrim | `scale-settle` |
| Caption block | centred, baseline at 55% of frame height on 9:16; on 16:9, 1:1 and any other shape, baseline at 85% of frame height inside the 5% title-safe inset | one level, title × 0.6, max 4 words a line | none — stroke + shadow carry it | `word-pop` |

**Caption cues.** Take scribe-v2 (or v1 Scribe) `words`, keep only `type == "word"`, and group
them in order into lines of at most 4 words, and fewer when the line would
exceed Max text width (Step 1.1). Start a new line after a word ending in
sentence punctuation or a gap of more than 0.4 s between words. A line shows
from its first word's `start` until the earlier of `max(last word's end,
last word's start + 0.3 s, first word's start + 0.5 s)` and the next line's first `start`; `word-pop`
keys each word to its own `start` instead of the 130 ms stagger, and the line
exits over the 200 ms starting at its end time, cut short by the next line's
first `start` (a hard cut there is exempt from Step 2's exit rule). Drop words whose `start` or
`end` is null. Caption lines are exempt from Step 3 (reading floor, fit and
word-pop fit); Step 6 prints n/a for `hold:` on them. The Caption block is one
overlay spanning the first to the last cue; 4d samples a cue line whose end time is at least 150 ms after its last word's
`start` + 110 ms, midway between the two. When a script exists, pass its names and numbers as `keyterms` (scribe-v2 only, +30% transcription price;
v1 has no such field); a caption word
takes the script's spelling only when it is the same spoken word (case,
punctuation, numerals, a keyterm's spelling) and keeps Scribe's timing; a script
token that spans several heard words ("twenty nineteen" → "2019") replaces
them as one word, from the first word's `start` to the last word's `end`; any
other mismatch keeps the heard word and is listed at delivery. With no script, burn the transcript as heard and list any
uncertain names at delivery. Never time captions from the
script or from duration; if there are no word timings, skip the captions and
say so.

## Step 6 — Checks, printed

One line per overlay row; a check whose only output is confidence leaves no
trace of not having run. An inapplicable check prints n/a.

1. `probe:` the cut's fps, resolution and duration, from 4a.
2. `font:` family, weight, file source (brand / system / DejaVu), and the
   measured cap height vs `C`. `load_default` anywhere is an automatic fail.
3. `motion:` the vocabulary item with in/out durations — or
   `hard cut-in — deliberate, because <reason>`.
4. `hold:` full-opacity seconds vs the reading floor for this string's length.
5. `path:` the animated bounding box at entrance start, hold and exit end —
   inside the frame *and* the safe areas whenever `α ≥ 0.5`. A mark sliding in
   is off-frame by design at `t = 0`; the rule is fully inside for the whole
   hold and never clipped while at half opacity or more.
6. `treatment:` which plate/scrim, and the colour source (brand files / official site / user-stated / sampled), with the type-colour luminance decision.
7. `burn:` all overlays in one encode — print the count — and the 4d mid-hold
   presence line per overlay.
8. `consistency:` (whole ad, once) one text motion + one card motion + one
   treatment + one family across all overlays (the Caption block's `word-pop`
   and stroke-and-shadow treatment exempt), or the exception named.

**Worked example — one lower third, so the arithmetic is visible.** A 1080×1920
cut at 24 fps; row 4's overlay is eyebrow "SINGLE ORIGIN" + name "Nine Fathoms
Roastery", window 12.0–17.0 s. `S = 1080`; name-line `C = 0.055 × 1080 ≈ 59 px`,
eyebrow `C ≈ 32 px`. Blur plate: padding 53×36 px, radius 15 px. `fade-rise`:
entrance 300 ms = frames 288–295 (`t = 12.0` → `u` 0→1, `α = ease_out(u)`,
`y` from 18 px below final to 0), hold to 16.8 s — 4.5 s against a reading floor
of `max(1.0, 31 ÷ 15) ≈ 2.1 s`, pass — exit 200 ms = frames 403–407. 120 RGBA
frames rendered, shifted to 12.0 s with `setpts`, burned in the single 4c pass.
The known-bad twin — same strings through drawtext with the bitmap default, no
plate, no motion — fails checks 2, 3 and 6 in the log, which is what proves the
checks can fail.

## Hand-offs

All pipeline hand-offs, one line each: `fal-video-production` stage 8 loads
this skill and owns burn ordering and the clearance/logo checks — if this skill
will not load, its stated fallback is a static type burn, labelled as such.
Generative card animation stays a static Step 4 render. The user's brand
files (sourced as `branded-graphics` describes) supply palette, logo clear space
and any minimum width. scribe-v2 word timings from `fal-audio-generation` feed
voiceover-synced `word-pop`; this skill burns the captions in the stage-8
encode. `video-compositing` handles caption jobs outside the pipeline.

## Guardrails

Each states the action it takes on its own, with no answer required.

- **Never write, reword or extend a string.** Styling may set case (an
  uppercase eyebrow is a treatment) but brand names keep their exact casing,
  and a missing string is a gap named in the delivery, never drafted here.
- **No generative model touches type or a logo.** The safe action is the Step 4
  render; a request for generative motion on a card gets the static render
  and the reply says generative card animation is not done here.
- **Never `load_default()`.** With no scalable font at all, the burn stops and
  the delivery says which component is waiting on a font — a bitmap-default
  burn is worse than no burn, because it ships looking finished.
- **One encode.** Overlays are never burned in sequential ffmpeg passes; a new
  overlay added later means re-running the single 4c pass from the kept stems
  and frames, which they exist to make free.
- **Motion never sacrifices the message.** If the window cannot fit the reading
  floor, the overlay does not flash faster — it goes back to the manifest as a
  window or copy problem, and the delivery says which row is waiting on it.
- **A mark in motion obeys the same rules as a mark at rest** — fully in frame
  and clear of platform chrome for its entire visible hold, checked by the
  printed path line, never fixed by cropping the mark.
- **The user's explicit style wins.** If they want linear motion, five fonts,
  or type in the bottom chrome zone, do it their way and note the cost in one
  line — this document is leverage, not law.

## Which house rules do not apply here

This skill calls no endpoint and submits nothing (the one parameter it names,
`keyterms`, rides `fal-audio-generation`'s scribe-v2 call), so the
schema, optimise-flag, upload and generative-liveness rules do not apply, and
with no route there is no fallback to name — rendering is local and
deterministic, and the one generative job in scope (card animation) is
answered with the static render. What this
document does apply: one mechanism per outcome (full-frame sequences, one
encode), intake that can go to zero calls, guardrails that act without
answers, printed checks proven able to fail, and hand-offs that say what
travels and in what shape.
