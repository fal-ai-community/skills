# H3 format specification

Use this reference as the mechanical source of truth for prompt assembly and
repair.

## Record grammar

The output has exactly three fields in this order:

1. `integrated_multimodal_description:` — all shots, blocking, camera,
   performance, and dialogue.
2. `overall_soundscape:` — one or two sentences of environmental bed and
   action-synchronous sound.
3. `non_diegetic_music:` — `N/A` by default; score only.

Do not put duration, mode, commentary, or extra metadata inside the record.
If an adjustment or non-default music reason must be reported, place one short
sentence before the record.

## Mode invariant

Set mode from input state:

| Condition | Mode | Description start |
|---|---|---|
| No image supplied | `t2va` | `[Shot 1] Live-action, cinematic,` |
| First-frame image supplied | `i2va` | Exact preamble, then `[Shot 1] Live-action, cinematic,` |

The exact `i2va` preamble is:

`For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`

Apply these `i2va` rules:

1. Describe Shot 1 completely; the preamble does not replace visual prose.
2. Make Shot 1's first state coincide with the image.
3. Express motion as emerging from that state.
4. Do not place a hidden cut inside Shot 1.
5. Do not mention Picture 1 after the preamble.
6. Preserve reference-visible identity, wardrobe, props, lighting, and place.
7. Add off-frame details only when continuity requires them.

## Shot and timestamp grammar

Let total duration be integer `D`, `5 <= D <= 15`.

- Shot 1: `[Shot 1] Live-action, cinematic, ...`
- Shot `n > 1`: `[Shot n] At MM:SS.mmm, ...`
- Shot IDs: contiguous integers `1..S`.
- Timestamp values: absolute from clip start, not relative to the prior shot.
- Timestamp grid: fractional part is `.000` or `.500` only.
- Timestamp bounds: `0 < t_n < D`.
- Ordering: `t_n < t_(n+1)`.
- Spans: `t_(n+1) - t_n >= 2`; final span `D - t_S >= 2`.

Treat a timestamp as the start of a new edit. Name its transition and landing
view. Do not place multiple coverage changes inside one numbered shot.

## Dialogue grammar

Wrap one complete utterance per tag:

`<d>[Language] line text</d>`

Use a real language name matching the spoken line. Keep punctuation inside the
tag. Do not wrap narration, camera direction, or nonverbal sound in `<d>`.

Assign speaker IDs by first audible speech:

1. Start at `(S1)` and increment without gaps.
2. On first use, write a visually grounded descriptor ending with stable vocal
   qualities and the ID.
3. On every later use, write the bare ID only.
4. Preserve the same ID through cuts, off-screen speech, radio, or voiceover.
5. Mark the channel when mediated speech could be confused with visible lips.
6. Give no ID to a silent person or sound source.

The grammar controls audible speech but does not warrant claims of exact
transcription, lip-sync, or speaker-identity persistence.

## Dialogue arithmetic

Compute:

- `U_clip = D - B_clip`, where `B_clip` covers entrances, action, pauses, and
  reactions.
- `W_clip <= floor(2.5 * U_clip)`.
- For a dialogue-dominant span only, `W_span <= floor(3 * U_span)`.
- For every shot `i`, `W_i <= floor(2.5 * U_i)` unless the preceding exception
  applies to that shot.

Count words inside dialogue tags only. Contractions count as one word. Trim a
failed budget in this order: filler within lines, redundant lines, whole turns.
Retain causal information over verbal texture.

For calibration, use these measured upper bounds only as ceilings, never as
targets:

| D | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dialogue-word ceiling | 5 | 8 | 12 | 15 | 20 | 23 | 28 | 31 | 36 | 39 | 44 |

The usable-seconds formula is stricter whenever action consumes time.

## Sound grammar

Build `overall_soundscape` as:

`continuous environmental bed + foreground events in screen order`.

Enforce:

1. One or two sentences only.
2. No shot numbers or timestamps.
3. Every foreground sound has an on-screen cause or grounded source.
4. Use material-and-action specificity: surface, object, and audible event.
5. Preserve a continuous bed within one space; change foreground events with
   the edit.
6. For silence, identify the sound that ceases, the residual bed, and the first
   sound that returns.
7. Put visible or implied source music here by default.

## Score decision

Set `non_diegetic_music: N/A` unless either condition is true:

1. The user explicitly requests a song, score, instrument, or musical
   continuation.
2. A discrete visible hinge can govern the cue: a montage, subjective memory,
   reveal, decisive launch, parting, or final fade.

Mood alone is insufficient. When score is permitted, specify only ensemble or
lead instrument, rhythmic behavior, tempo, emotional color, mix relation to
speech, and onset/change at the hinge. Never transcribe lyrics.

## Repair order

When validating an existing prompt, repair in this order:

1. Clamp duration to a legal integer.
2. Restore the exact three-header topology.
3. Restore the conditional preamble and Shot 1 opener.
4. Renumber shots and quantize timestamps.
5. Reduce shots to the duration ceiling.
6. Repair dialogue tags and speaker IDs.
7. Trim dialogue to both timing formulas.
8. Replace forbidden camera qualifier values.
9. Rebuild soundscape causally.
10. Reset music to `N/A` unless a valid reason survives.

For a fully specified prompt destined for fal, recommend turning prompt
expansion off; rewriting preserves structure but reduces timing precision.
