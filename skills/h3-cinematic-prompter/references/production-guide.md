# H3 Cinematic Prompter

## Mandatory entry behavior

Turn the user's material into a finished prompt ready to paste into MiniMax
Hailuo H3 on fal. Write the prompt only. Do not submit, poll, or promise a
video file.

Detect the mode without asking:

- If a first-frame image is present, use `i2va`.
- Otherwise, use `t2va`.

If the request concerns expanding, outpainting, resizing, or padding an image,
do not claim the attachment for this workflow. Route it to an image-expansion
workflow.

Resolve missing creative details yourself unless one choice would materially
change the user's intent. If duration is missing, apply the Defaults. If it is
invalid, replace it with the nearest legal integer and state the adjustment
before the prompt.

## Contract invariants

1. Set duration `D` to an integer satisfying `5 <= D <= 15` seconds.
2. Emit exactly these three headers, once each, in this order:
   `integrated_multimodal_description:`, `overall_soundscape:`,
   `non_diegetic_music:`. Emit no fourth field.
3. In `i2va`, begin the description value with this byte-exact line:
   `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
   In `t2va`, omit it entirely.
4. Open Shot 1 with `[Shot 1] Live-action, cinematic,`. Give Shot 1 no
   timestamp. Number shots contiguously from 1.
5. Open every later shot with `[Shot N] At MM:SS.mmm,`. Make timestamps
   absolute, zero-padded, strictly increasing, on the half-second grid
   (`.000` or `.500`), and `< D`.
6. Wrap every spoken utterance as `<d>[Language] line text</d>`. Use the
   language actually spoken.
7. On first speech, identify a speaker with a descriptor phrase ending in
   vocal qualities plus contiguous ID `(S1)`, `(S2)`, and so on. On later
   speech, use only the bare ID. Never assign an ID to a nonspeaker.
8. Default to `non_diegetic_music: N/A`, byte-exact. Depart only when the user
   authorizes music or a discrete visible hinge requires score; state that
   reason before the prompt.
9. When formal camera qualifiers are used, amplitude is `small` or `large`
   and speed is `slow` or `fast`. `medium amplitude` and `medium speed` are
   forbidden; both occur zero times in 21,524 records.
10. Treat shot type as a composition, never a pick-list. Build
    `[SIZE? + MOVE? + ANGLE? + TIME-OF-DAY? + OTHER?] + shot`; normally use
    one or two production-meaningful modifiers.

Read [format-spec.md](format-spec.md) before drafting whenever the
request includes dialogue, an image, music, or an existing prompt to repair.
Read [camera-and-craft.md](camera-and-craft.md) for multi-shot work,
screenplay condensation, thin premises, or deliberate camera direction. Read
[examples.md](examples.md) only when a worked pattern is useful.

## Workflow

### Step 1 — Fix the duration and mode

Set `D` and detect `t2va` or `i2va`. Never ask which mode. In `i2va`, make the
first described state coincide with the supplied frame; do not invent an
earlier action or refer to Picture 1 again.

### Step 2 — Expand a thin premise before prompting

Construct a miniature scene that answers four questions:

1. Where and when: one concrete place and one lighting condition.
2. Who: one to three characters, each with one visible identity cue.
3. What changes: one objective meets one obstacle, turns at a visible hinge,
   and ends in a visible consequence.
4. What is heard: one environmental bed plus action-caused foreground sounds.

Limit this scene to the shot budget before writing prose. Add only
production-facing connective detail; do not invent story-changing biography,
props, or behavior.

### Step 3 — Compute the shot budget

Use `M(D)` as the default and `P(D)` as the ceiling:

| D | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M(D) | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 3 |
| P(D) | 2 | 2 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 |

Set `S = M(D)`. Permit `S <= P(D)` only for a montage, pursuit, or instantly
readable insert. Reduce `S` for sustained verbal pressure. Assign one dramatic
function to each shot. Cut only when information, power, location, action
phase, or point of view changes. Keep every shot span at least 2 seconds;
reserve 2–2.5 seconds for simple inserts or reactions.

**Worked 15-second timeline:** `D=15`, so `M(15)=3`, `P(15)=4`; choose three
beats at `00:00`, `00:05.500`, and `00:11.000`, yielding spans of 5.5, 5.5,
and 4 seconds. The final beat begins at `11/15=73%`, leaving time for the
consequence to read.

### Step 4 — Compute the dialogue budget

Let `U = D - B`, where `B` is seconds reserved for entrances, physical
business, pauses, and reactions. Enforce `dialogue_words <= floor(2.5 * U)`.
Allow up to `3 * U` only inside an intentionally dialogue-dominant span. Also
enforce each shot's words `<= floor(2.5 * that shot's usable speech seconds)`.

Prefer short lines. If dialogue fails either test, trim lines first, then drop
whole turns. Preserve the initiating line, scene-changing answer, and final
consequence before greetings, repetition, exposition, or spectator reactions.
Never cut a necessary shot merely to preserve excess dialogue.

### Step 5 — Draft picture, motion, and cuts

After the required Shot 1 prefix, establish place, lighting, subjects, spatial
relations, and immediate action. For later shots, state what the cut lands on
and why that view matters. Carry a subject, prop, eyeline, sound, movement, or
objective across each cut. Translate internal states into visible behavior.

Compose shot modifiers by slot. Motivate every move and angle. If a move uses
formal qualifiers, choose only one legal amplitude and at most one legal speed;
do not duplicate speed in both the move adjective and formal slot.

### Step 6 — Write sound and music

Write `overall_soundscape` in one or two sentences: continuous environmental
bed first, then a short screen-order sequence of material-specific sounds
caused by visible actions. Put diegetic music in the soundscape by default.
Use silence by naming what stops, what remains, and what returns.

Keep `non_diegetic_music: N/A` unless invariant 8 permits a score. If permitted,
describe the smallest sufficient palette and tie its onset or change to the
visible hinge. Keep it subordinate to speech.

### Step 7 — Emit and validate

Return the three-field prompt as plain text. A carefully specified H3 prompt
should be sent with prompt expansion turned off because expansion costs timing
precision.

Run this validator against the draft:

- [ ] `D` is an integer and `5 <= D <= 15`.
- [ ] Header sequence equals the three required headers; header count is 3.
- [ ] `i2va` has the byte-exact preamble; `t2va` has no preamble.
- [ ] Shot 1 has the exact opener and no timestamp.
- [ ] Shot numbers equal `1..S` with no gaps.
- [ ] Every later timestamp matches `MM:SS.(000|500)` and `0 < t < D`.
- [ ] Later timestamps strictly increase; every shot span is at least 2 seconds.
- [ ] `S <= P(D)` and every shot has one distinct dramatic function.
- [ ] Every utterance has one complete language-tagged `<d>` span.
- [ ] Speaker IDs start at S1, are contiguous, and use full descriptor once.
- [ ] Dialogue passes both whole-clip and per-shot word formulas.
- [ ] Neither forbidden medium qualifier occurs.
- [ ] Every shot type is slot-composed; every move, angle, and cut is motivated.
- [ ] Soundscape is 1–2 sentences, screen-ordered, and causally audible.
- [ ] Music equals `N/A`, or its permitted reason was stated.
- [ ] No claim of submission, generation completion, or output file appears.

## Defaults

- **Duration:** 10 seconds.
- **Mode:** Detect from image presence.
- **Shots:** `M(D)`.
- **Dialogue:** None unless speech is necessary to the causal spine.
- **Music:** `N/A`.
- **Transition:** A clean cut that names its landing view.

## Consistency and guardrails

- Preserve user-supplied story facts; invent only what makes them shootable.
- Keep `i2va` subjects, wardrobe, props, light, and location consistent with
  the reference; minimize invention outside the frame.
- Do not claim word-accurate speech, lip-sync, or speaker-identity fidelity.
- Keep every timestamp below requested duration; output may run slightly long,
  but that overshoot is not timing headroom.
- Prefer one causal micro-scene over disconnected coverage.
