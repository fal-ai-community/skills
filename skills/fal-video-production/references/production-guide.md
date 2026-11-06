# Video Production

A pipeline, not a router. It sequences skills that already exist and owns only the
four things none of them own: the **timing contract** between script and audio,
the **review fence** after the clips render, the **assembly**, and the **final
watch-and-listen** on the file that is about to be delivered.

Every generation call belongs to a sibling. This skill's job is to make sure
nothing between the steps gets dropped — which is the failure it was written for.

## What this exists to prevent

Two real production runs of a coffee-brand ad produced seven defects. Six happened
*between* steps rather than inside one, and the seventh is the reason the last
stage exists.

- The script computed a word budget and a voiceover window per shot. The audio
  step generated **one continuous read** instead, so the words bunched into the
  opening seconds and the rest played to silence.
- The pipeline ran animate → voiceover → mix without stopping, so **nobody saw
  the clips** until the cut was finished and paid for.
- Shot 1 came back **frozen**, caught only because a human watched it.
- Shot 5 took **three attempts**, because its shot seed asked for two actions.
- The script specified lower-thirds. **None were burned in.** Every clip rendered,
  the mix completed, and the words never appeared.
- Music level and ducking were decided ad hoc, differently each time.
- **A 30-second ad shipped with 21 seconds of audio, then one with 18.** Nothing
  in the pipeline objected, because the only timing check asked whether each line
  *fitted inside* its window, and a two-second read in a six-second window fits
  perfectly. The check could only fail in one direction.

That last one is the pattern worth naming, and it has a sharper second half.

**A check that can only fail in one direction will pass the opposite failure** —
the same shape as a preservation check approving a frozen clip. But the obvious
correction, demanding that speech *fill* the runtime, is also wrong, and the first
attempt at this skill made it. **Eighteen seconds of speech in a thirty-second ad
is a good ad**: read at a comfortable pace, each line on the shot it describes,
air around it. It is a bad ad only when those eighteen seconds run consecutively
and the last twelve play to nothing. The word count was never the defect. **Where
the silence ended up was.**

So the checks below are deliberately **asymmetric**. Too many words for a window
is a defect, because no later step can manufacture time. Too few is a pacing fact,
and the pipeline's job is to place the spare seconds rather than to fill them.
The measurement that separates the good case from the bad one is the **largest
single gap**, not total coverage — coverage is identical in both.

## Stage table

Each stage names the skill or endpoint that owns it. The fallback column is what
to do when the owner is unavailable — never "do it here anyway, unlabelled".

| # | Stage | Owner | Fallback when the owner will not load |
|---|---|---|---|
| 1 | Script, shot list, per-shot windows | `fal-script-writer` | Draft the shot list here and **label it undrafted by the specialist**; keep the window arithmetic, it is this skill's contract |
| 2 | Opening stills — **mandatory for hero shots**, optional elsewhere | `recommend_model` text-to-image pick (default `google/nano-banana-2.1`) | Animate from text and say so, noting that the hero shot was never approved as a frame |
| 3 | Animate one clip per shot | `fal-video-generation` | **No fallback — stop.** Clips are the deliverable; there is no degraded version worth billing for |
| 4 | **Clip review fence** | this skill | None. The fence does not degrade |
| 5 | Voiceover, **one file per fragment, unconcatenated and unpadded** | `fal-audio-generation` | Deliver silent with the manifest attached, and say the voiceover is outstanding |
| 6 | Music bed | `fal-audio-generation` | Accept a user-supplied track, or deliver without music and say so |
| 7 | Mix, duck, normalise | this skill, in the sandbox | None needed — local work |
| 8 | Burn on-screen text, last | **this skill, in the sandbox** — *not* a caption pass, which times captions off transcribed speech and cannot place script-driven text | None; never skip, never ship silently untexted |
| 8b | Captions of the voiceover, if asked for | scribe-v2 word timings per `fal-audio-generation`, burned as the `fal-motion-graphics` Caption block in the same stage-8 encode | `fal-ai/elevenlabs/speech-to-text` (v1 Scribe, same `words`); if that also fails, or `fal-motion-graphics` will not load, skip and say so — captions are an optional extra deliverable, not the lower-thirds |
| 9 | **Watch and listen to the finished file** | `fal-ai/video-understanding` + `fal-ai/elevenlabs/speech-to-text/scribe-v2` | `fal-ai/sa2va/8b/video` for the vision pass; `fal-ai/elevenlabs/speech-to-text` (v1 Scribe, same `words`) for the transcript; if that also fails, say the placement check could not be run |
| 10 | Deliver with the measured figures | this skill | — |

**Stages 3 and 8 both re-render pixels, and 8 must follow every one of them.**
That ordering is why burn-in is stage 8 and not stage 5.

## Step 0 — One intake card

Call `ask_user_questions` **once** (if your host has no question tool, ask the same questions in one plain message and wait for the
reply before spending; that reply counts as the card). Drop any question the brief already answers;
if it answers all of them, make zero calls and start at stage 1.

1. **Brief** (header `Brief`, free text) — the product, the audience, what the ad
   has to land. Default is to read it from the message that triggered this skill.
2. **Runtime** (header `Length`) — total finished duration. Default **20s**.
   Offer `15s`, `20s`, `30s`, plus free text.
3. **Shape** (header `Shape`) — default **9:16**, with `16:9` and `1:1`.
4. **Voiceover** (header `Voice`) — default **yes, one narrator**. `None` skips
   stage 5 and the ducking half of 7.
5. **On-screen text** (header `On-screen text`, free text) — the exact strings for
   lower-thirds, plus any end card. **Default none**, never drafted here: a
   misspelt brand name burned into a finished cut is worse than no text.
6. **Review** (header `Review`) — `Pause after the clips` (**default**) or
   `Run straight through, do not pause`. This is the only place the fence can be
   waived, and it is waived *before* anything is spent, never during.
7. **Native clip audio** (header `Clip audio`) — `Discard` (**default**) or
   `Generate and keep it as a stem`. H3 routes, the default, have no audio
   switch, so the card decides only whether any soundtrack an H3 shot returns is
   kept as a stem or discarded. Seedance, Veo, LTX 2.5, Kling, Flux 3 and
   Wan routes default audio on (Veo and Kling charge 50–100% more for it), so the pipeline
   pins it off: an ad gets a written voiceover and a chosen bed, and the model's guess at
   room tone is thrown away. **But it is thrown away permanently.** Wanting it
   later means re-rendering every shot at full price, which costs far more than
   generating it once would have. So the question is asked here, with that
   asymmetry stated, and whichever way it goes the delivery says so. If the ad has
   any diegetic sound in the brief — a pour, a door, footfalls that should be heard
   rather than replaced — recommend keeping it.

**Three further headers are declared here and fire later.** They ride their own
card at the stage that needs them, because they ask about work that does not exist
yet. Each states what happens with no answer:

- **`Approve structure`** — the story gate at stage 1c, before anything renders.
  **No answer means stop**, beat map delivered, nothing rendered. Waivable only
  here, alongside `Review`.
- **`Approve clips`** — the fence at stage 4. **No answer means stop**, clips
  delivered, remaining stages unrun.
- **`Reshoot`** — which clip numbers to redo. No answer means stop, as above.
- **`Music`** — mood or a supplied track, asked only when `Voice` is on and the
  brief named no music. No answer means **deliver without a bed**, which is a
  complete ad, so this one never blocks (on a host with no question tool, one plain
   message, then in the same turn deliver without a bed and say so).

Stage 9 asks nothing. It measures, and reports what it measured.

## Stage 1 — The timing contract

This is the artefact both failed runs threw away. Before a single clip renders,
build a manifest with one row per shot and keep it as the pipeline's spine:

| field | meaning |
|---|---|
| `n` | shot number, the handle the user reshoots by |
| `start`, `dur` | its window in the finished cut, in seconds. **`dur` must be renderable** — see the quantisation rule below |
| `render_dur` | what the route will actually return: about `dur` on H3 Max (up to ~0.7s over), usually longer on a fallback |
| `action` | **exactly one** physical beat |
| `look` | lighting, grade and time of day, **and what it inherits from the row above** |
| `vo` | the script fragment for this shot, or empty |
| `vo_words` | word budget for `dur`, at ~2.4 words/second |
| `vo_start` | where this fragment's audio actually starts, set in stage 1b — **not** the same as `start` |
| `overlay` | text **and any image asset** burned over this window, or empty |

**`render_dur` must be a length the route can render. `dur` is what the cut
uses, and it may be shorter.** Every generation route here has a minimum: H3 Max,
the default, takes any number of seconds from `0.92` to `15` (the output can run
about 0.7s longer than asked); most fallbacks floor higher (Wan 3.0 Prime
takes integers from `2`; LTX 2.5 takes only 6, 8 or 10) — Seedance 2.5 takes
whole seconds from `4` to `30` (2.0 stops at `15`), Veo 3.1 Fast only `4s`, `6s` or `8s`, base
MiniMax H3 integers `5` to `15`. A shot shorter than the floor is therefore not
impossible, it is a **planned trim**: render at the floor, cut to `dur`. What a
run must never do is discover the floor at assembly — one that planned
`2/4/8/8/5/3` as render lengths came back `4/4/8/8/6/4` and had to be rescued by
improvised trims, because its contract had conflated the two columns.

So build the contract in this order: **choose the route (H3 Max by default, including photoreal people; a shot it refuses moves to Veo 3.1 Fast per `fal-video-generation`'s moderation rule, so quote that row's possible Veo cost: the next Veo length (4s, 6s or 8s; 8s for a reference row) at Veo 3.1 Fast's `get_pricing` rate (the with-audio rate; say the silent render is lower when Clip audio is Discard); a row Veo cannot take goes back to the user if refused), write each row's
`render_dur` from its legal durations, then write `dur` from the pacing the
brief asks for.** Consequences to state at delivery:

- **Pacing sets the shot count; the floor sets the price.** At default pacing
  `dur ≈ render_dur` and a 30-second ad holds about 7 shots. A fast-paced brief
  — TikTok, frenetic, montage — plans `dur` at 1–2.5 seconds per shot. On H3 Max
  `render_dur` can match `dur`; on a fallback route each shot pays the floor:
  eight quick shots in a 15-second cut bill roughly 32 rendered seconds on
  Seedance or Veo. That is a legitimate ad and a quoted cost, never a refusal;
  the choice is made here, priced on the sum of `render_dur`, not discovered at
  assembly.
- **Where `render_dur > dur`, the trim is planned, not improvised.** Say which end
  you trim from — take it from the tail unless the action resolves there, in which
  case trim the head and note it. And write the row's `action` for the seconds
  that survive: a 2-second cut of a 4-second render must land its beat inside
  the kept window, so the beat is prompted early, not at the render's midpoint.
- **The quote uses the rendered figure.** You paid for `render_dur` seconds and
  used `dur`; a fast cut costs more per finished second, and the quote says so.

Route choice therefore drives timing granularity. H3 Max's decimal durations
land closest (allow about 0.7s of overrun); Seedance's whole-second enum comes
next; Veo's three-value enum forces every
shot to 4, 6 or 8 and makes trimming the norm. Say which you took and why.

**One action per `action` field, enforced here rather than hoped for.** If a row
names two beats — tie the bag *and* set it by the window — split it into two rows
and re-run the arithmetic. Models do not refuse a second action, they blend it,
and the blend reads as a mistake. Two short clips also cost what one long clip
costs and give two independent attempts.

**`look` exists because every shot is rendered blind to the others.** Each clip is
a separate call with no memory of the last one, so lighting and grade do not carry
unless you carry them. A run whose shot 4 was deep red and dark returned a shot 5
in ordinary daylight — the sip that was supposed to be the payoff of an escalating
mood arrived looking like a different ad, and it cost a relight, a re-animate and a
swap to fix after the fact.

So write the look into every row **in absolute terms, not relative ones**. "Deep
red key from screen-left, dark falloff, practicals only" renders; "same as before
but darker" does not, because the model cannot see "before". Where the mood is
meant to build across shots, each row states its own point on that curve, and the
row also names what it inherits so a human reading the manifest can see the ramp.
Then check the ramp before rendering: any row whose `look` could be read as a reset
of the previous row's mood is the defect — catch it here, where it is a sentence,
not at the fence, where it is three calls.

**`vo_words` is a ceiling with a comfort floor, and they are not symmetric.**

- **Ceiling:** `dur × 2.7` words. Above that the line cannot be read in the window
  without rushing, and rushing is audible. A row over the ceiling is fixed here,
  while it is free, by moving a clause to a neighbouring shot or shortening `dur`
  elsewhere and giving the seconds to this row.
- **Comfort floor:** `dur × 1.9` words. Below this the window holds more air than
  speech. **That is a signal, not an error** — it means this shot is carrying the
  picture more than the words, which is often right. It is handled by *placing*
  the air (stage 1b), never by inventing words to fill it.

The asymmetry is the point. Too many words is a defect, because no downstream step
can create time. Too few is a pacing decision, and the pipeline's job is to spend
the spare seconds deliberately rather than let them pool at the end.

## Stage 1b — Split the script across the clips, then spread the air

**A script shorter than the runtime is normal, and it is not a defect.** Eighteen
seconds of speech in a thirty-second ad is a perfectly good ad — read at a
comfortable pace, each line landing on the shot it describes, air around it. The
same eighteen seconds becomes a defect only when it is delivered as one block and
the last twelve seconds play to nothing. **The problem is never the word count.
It is where the silence ends up.** Do not pad the script to fill time, and do not
speed anything up. Distribute.

**First, cut the script to the clips.** Take the script as written and split it at
**natural boundaries** — sentence ends first, then clause breaks at commas,
conjunctions and dashes. Never split mid-phrase, never split a brand name or a
URL across two clips. Assign one fragment per shot, in order, matching what the
fragment says to what the shot shows: the line about the roast date belongs on the
shot of the stamped bag. A fragment may be empty — some shots are meant to carry
the picture alone — and a fragment may span two shots only if those two shots are
one continuous idea, in which case say so.

Size each fragment against its shot's `dur` using the band above. If a fragment is
over the ceiling for its shot, move a clause to the neighbouring shot rather than
cutting words; if the script simply has more to say than the runtime allows, that
is a script problem and it belongs back at stage 1.

**Then spread the air deliberately, one shot at a time.** The air is a resource to
place, not a remainder to leave lying at the end. Place it *within each shot's own
window*, never by running a clock across the whole timeline:

```
slack    = dur − (spoken duration of this fragment)
vo_start = start + 0.35 × slack
```

Roughly a third of the spare time goes in front of the line, the rest behind it.
Record `vo_start` per row. That, not the row's `start`, is where stage 5 places
the audio.

**Do it per shot for a reason.** The obvious alternative — total the air, divide it
among the gaps, and run a cumulative clock — was tried and is subtly wrong: on a
worked 30-second example it put the last fragment's first word at `24.90` when its
own shot did not begin until `25.0`, so the line opened a tenth of a second before
its picture. Small, inaudible, and a direct breach of the boundary rule two
sections down. Deriving `vo_start` from the shot's own `start` makes that
impossible by construction rather than by a check.

It also spreads correctly on its own. Because the word band keeps each fragment
roughly proportional to its shot, taking a fixed share of each shot's slack leaves
even gaps without any global arithmetic. On that same example — 18 seconds of
speech across six shots in a 30-second ad — it yields a `0.98s` lead-in, a largest
gap of `2.38s`, a `0.91s` tail, and speech in all three thirds. The identical
script read as one continuous block yields a single 12-second hole.

Two edges to handle explicitly:

- **A shot with an empty fragment** is a deliberate silence, and it will show up as
  a long gap. That is fine and it is *not* a defect — but say so at delivery, so a
  long quiet stretch reads as a choice rather than a fault.
- **Negative slack** means the fragment is over the ceiling for its window. That is
  the overrun path above; fix it there, not here.

**Then check the distribution, which is the check that matters.** Total coverage
is the wrong measurement on its own — it cannot tell 18 seconds spread evenly from
18 seconds in a block, and those are a good ad and a broken one. Check instead:

- **Largest single silence** — no gap longer than **2.5s** anywhere in the cut,
  and none longer than `1.5s` at the tail. One long gap is the whole failure mode.
  A gap that falls inside a shot with a deliberately empty fragment is exempt, and
  is reported as intended silence rather than counted against this limit.
- **Per-shot presence** — every shot whose fragment is non-empty has speech inside
  its own window.
- **No empty third** — speech is present somewhere in each third of the runtime.

A cut can pass a coverage figure and fail all three. Report the largest gap next
to the coverage number, always, so the two are read together.

## Stage 1c — The story gate, before any pixels

**Stop here and get the structure signed off.** This is the cheapest gate in the
pipeline and the one that saves the most, because the structural shape of a piece
is the single most expensive thing to change after clips exist — and it is the
thing a reader can only judge once they see it stated plainly.

A run whose brief storyboarded a gradual in-kitchen escalation was executed
faithfully, and the author then rewrote the core structure **twice** after watching
rendered clips — moving to a smash cut, then adding a beat. That was not a defect
in the brief or the execution; it was a better idea arriving late, which is normal.
What was wrong is that it arrived *after* animation instead of before, so each
revision cost renders instead of costing a sentence.

Present the spine as a short numbered beat map — shot number, the one action, the
`look`, and the VO fragment — plus the three questions that decide its shape:

1. **Is the change gradual or a smash cut?** State which the beat map implements
   and where the pivot sits.
2. **Which beats did the shot budget drop?** From `fal-script-writer`'s triage, in
   priority order.
3. **What is the payoff shot, and does anything build into it?** Name the shots
   either side of the pivot and what carries.

Ask with one card, header `Approve structure`, declared in Step 0. Offer
`Approve — start rendering`, `Change the structure` (free text), or
`Stop, I'll revise the brief`.

**No answer means stop**, with the beat map delivered and nothing rendered.
Stopping needs no input, so this gate is safe without a reply; it needs one only to
spend money, which is the correct direction. Like the clip fence, it is waivable
only from intake — and if it was waived, the delivery says the structure was never
approved before rendering.

## Stages 2–3 — Render the clips

**Before wording or critiquing anything visual, load `fal-shot-craft`.** It
carries the craft this pipeline's checks enforce mechanically: the reason
behind precondition P2 (one settled state per clip), the slot grammar for
framing, the motivated-or-locked camera rule, and the
gesture-not-the-named-emotion rule that separates a renderable action from a
mood word. Use it when reviewing stage-1 rows that arrive undrafted by the
specialist, when critiquing a hero still, and when phrasing the motion brief
handed to `fal-video-generation`. If it will not load, the manifest fields and
P1–P3 below are the minimum, and the delivery says the craft reference was
unavailable.

**Generate a still first for every hero shot, and iterate on the still.** A hero
shot is the one the piece is built to arrive at — the payoff, the reveal, the
product moment, the frame someone will screenshot. Text-to-video gives you one
expensive attempt at composition, subject and world all at once, and if the
landscape comes out shapeless or the subject is badly placed you pay a full clip to
find out. A still is a fraction of the cost and can be regenerated until it is
right, and animating an approved frame then only risks the motion.

This is not a quality nicety, it is where "the terrain looks simple and flat" gets
fixed. Get the frame from `recommend_model`'s text-to-image pick, with
`aspect_ratio` set to the intake Shape (the H3 Max image route takes the
still's canvas), look at it, say what is wrong in
concrete terms — silhouette, scale, depth, how many planes the landscape has, where
the horizon sits — and regenerate until it holds. **Then** animate it.

Hero shots go through this. Ordinary shots may skip it. If you skip it on a hero
shot, say so in the delivery, because the composition was then never approved by
anyone before it was animated.

### Three preconditions. Print them, per row, before you submit anything

Each of these existed as advice in an earlier version of this skill and each was
skipped by a capable agent under momentum. They are steps now, and each produces a
line you must print, because a check whose only output is your own confidence
leaves no evidence of not having run.

**P1 — An image overlay on a shot that animates is composited into the still, not
burned afterwards.** A logo burned onto moving footage rides the frame like a
sticker while the picture moves underneath it, and no amount of care at stage 8
fixes that: the overlay has to be part of what the motion model sees. So for every
row whose `overlay` carries an image asset **and** whose shot is animated, the
asset is composited into the stage-2 still, and the row may not be submitted for
animation until it is. Print `row n: image overlay composited into still — yes/no`.
A `no` is a hard stop on that row, not a note.

**P2 — One settled state per clip. No transformation verbs.** A single clip renders
one continuous motion, not a change of state. Prompts written as transitions —
"resolves into a skull", "pre-fire to fire", "becomes", "transforms into", "morphs",
"turns into", "shifts to" — ask one clip to be two shots, and the model answers by
cutting or resetting inside the frame, which reads as a glitch. Two reshoot rounds
went to this. **Treat those verbs as a lint failure on the prompt before submit**:
scan each prompt for them, and if one is present, the fix is not a reword but a
split — the settled state goes in the still, the continuous motion goes in the clip,
and if the brief needs the change to be visible it needs two rows. Print
`row n: transformation verbs found — none/[list]`.

**P3 — The route matches the content, decided up front.** See the content
constraint in `fal-video-generation`'s routing notes. On a Seedance pick,
photorealistic human likenesses and other moderation-sensitive frames go to
Veo 3.1 Fast from the first attempt if they pass the Veo fit test, and are
otherwise tried once on Seedance; on H3 Max they are tried once; a
refusal moves the shot to Veo 3.1 Fast if it passes `fal-video-generation`'s
Veo fit test, and otherwise back to the user with a re-cut, rewrite or drop to
choose from. Three separate 422 rounds were spent
discovering this by collision. Print `row n: route chosen for content — <route>,
because <reason>`.

Hand each row to `fal-video-generation` with its `action`, `dur`, `look` and the
shape from intake — and the still's URL where stage 2 produced one, so the route is
image-to-video rather than text-to-video. That skill owns route choice, cost quoting and its own ceiling of one retry
per shot; **do not override it into a third attempt** — a shot that fails twice
goes to the fence marked failed, and the user decides.

Then, before the fence, **measure every clip for motion**.
`fal-video-generation` specifies the measurement and how to calibrate its floor
with a frozen control and a moving control per route, because a fixed threshold is
how this check passes a still image. Carry three numbers per clip into the fence:
the measured minimum one-second window, the frozen control, and the floor.

A clip below the floor is **flagged, not silently rejected** — it may be a slow
push-in the user wants. The fence is where that is decided.

## Stage 4 — The clip review fence

**Everything before it is cheap and reversible; everything after it costs money
and compounds.**

**First, reconcile the look ramp against the rendered clips — this is mandatory and
it is not the stage-1 check.** Stage 1 checked the ramp you *intended*. This checks
the ramp you *got*, which is the only one the viewer sees. A run wrote a correct
manifest and never ran this, and shot 5 came back warm between a deep-red shot 4
and a fire-lit payoff — the pivot of the whole piece, visually disconnected from
both sides.

Sample a mid-frame from every clip, in order, and measure each one's mean hue,
saturation and luminance. Print the three numbers per shot as a table. Then judge
the sequence, not the individual frames: **any shot whose numbers step back toward
the opening's values, where the manifest said the mood should build, is a reset**
and goes into the card below marked `LOOK RESET`. The manifest's `look` column is
the reference; a clip that does not match its own row is flagged even if it looks
fine alone.

Then present the clips as a numbered list, one line each: number, the `action` it
was meant to show, its motion figure against the floor, its hue/saturation/luminance
against the row above, its cost, and a plain `LOOKS STATIC` or `LOOK RESET` where
either check is under. Then ask **one** `ask_user_questions` card, header
`Approve clips`:

- `Approve all — continue` → stages 5 onward.
- `Reshoot some` → follow with the `Reshoot` header, free text, taking clip
  numbers. Reshoot only those, re-measure, return to this fence. It repeats.
- `Stop here, give me the clips` → deliver the clips and the manifest.

Three rules that make this a fence rather than a courtesy:

1. **A message cannot return an answer.** It must be a card (on a host with no question tool, one plain message, then wait for the reply). "Let me know if
   these look right" is not a checkpoint.
2. **No answer means stop** — deliver the clips, say which stages did not run, end
   the turn. Stopping needs no input, so the fence is safe without a reply; it
   needs one only to *continue*, which is the right direction for a spend gate.
3. **It is skippable only from intake.** If `Review` was waived, say in the
   delivery that no clip was reviewed before the audio spend.

## Stage 5 — Voiceover, one clip per line

**Generate one audio clip per fragment, and place each at its own `vo_start`.**
Never one continuous read.

A single read has to be cut apart afterwards by detecting silence, which assumes
the speech engine left detectable gaps. It is a rescue, not a design, and it fails
quietly by bunching every word into the opening seconds.

**Two things must be turned off in the hand-off, because the sibling does them by
default and both are correct outside this pipeline.** `fal-audio-generation`
generates one request per part and then (a) **concatenates the parts** with a fixed
0.35s of silence between them, and (b) **appends digital silence** when the audio
comes in shorter than its window. Standalone, that is exactly right. Here it is the
defect: you get one welded file with 0.35-second gaps and every spare second pooled
at the tail, which is how eighteen seconds of speech became a front-loaded
thirty-second ad. The gaps in this pipeline are not 0.35s — on the worked example
they are 1.6s to 2.4s, derived from each shot's own slack.

So the hand-off must say, in these terms: **return the parts unconcatenated, as one
file per fragment, and do not pad any of them.** Placement and padding belong to
this skill, which is the only place that knows the shot boundaries. If the sibling
returns a single joined file anyway, do not accept it and split it on silence —
that is the rescue this stage exists to eliminate. Re-request per fragment.

**Pin the voice once, before the first call, and send that same voice identifier
on every fragment.** This is what makes per-fragment generation safe: separate
calls with a default or drifting voice produce an ad that changes narrator between
shots, which is far more obvious than any timing fault. If the route cannot pin a
voice, that is a reason to change route, not a reason to go back to one long read.
Fix the speaking rate, tone and language the same way — one setting, reused.

Then check each segment against its window. The two directions are **not**
symmetric, and treating them as if they were is what produced a padded script:

- **Overrun** — segment longer than its window. A defect. Re-generate shorter, or
  trim the line, or take seconds from a neighbour per the boundary rule below.
  Never speed the read up: it is audible, and "just have the voiceover read
  faster" is what produced a rushed cut once already.
- **Underrun** — segment shorter than its window. **Not a defect.** It is spare
  time, and stage 1b already decided where it goes. Re-centre the fragment on its
  `vo_start` and carry on. Do **not** lengthen the line, do not stretch the audio,
  and do not let the leftover collect at the end of the ad.

After placing every fragment, **re-measure the three distribution checks from
stage 1b against the real segment lengths** — largest gap, per-shot presence, no
empty third. The planned figures came from an estimate of speaking rate; these
come from audio that exists. If the real lengths have opened a gap wider than
2.5s, redistribute the air now, before mixing, by shifting `vo_start` values. That
is free. Discovering it at stage 9 is not.

**If the audio has to be cut, cut on a scene boundary.** When a line genuinely
overruns and trimming words is not acceptable, the seconds come from somewhere,
and the only safe place is a window edge. Move the boundary between two shots and
re-derive both `start` values — never let a line bleed across a cut, and never
fade a word mid-syllable to make an arithmetic problem go away. A voiceover that
finishes a sentence over the next scene reads as a mistake even when every
individual asset is good. If moving the boundary means a clip is now longer than
what was rendered, that is a re-render and it goes back to the fence; say so
rather than stretching or looping the footage.

Silence between rows is correct. Silence at the end is the cut running long.

## Stages 6–7 — Music and the mix

Ask `Music` only if needed, per Step 0. Then assemble in the sandbox with ffmpeg:

1. Concatenate the approved clips in manifest order.
2. Lay each voiceover segment at its **`vo_start`** — not at its shot's `start`.
3. **Duck the bed with sidechain compression keyed to the voiceover** — not with
   a static gain, and never with a gate. A fixed multiplier was tried and it
   buried the narration: it cannot know how loud the bed's own material is
   moment to moment, so a fixed `0.15` leaves a busy passage still sitting on
   top of the words. Use ffmpeg's `sidechaincompress` with the VO stem as the
   key, a moderate ratio around 4:1, a fast attack and a release around
   250–400 ms so the bed comes back up between lines instead of pumping.
   **A duck is a dip, not a mute.** Real runs shipped ads where the music
   audibly stopped under every line and restarted after it, which reads as a
   broken file rather than a mix. Aim the settings at **6–9 dB of gain
   reduction** during speech; past 12 dB the music has stopped, whatever the
   filter was called.
4. **Then verify the ducking by measuring, not by listening once — in both
   directions.** The first version of this check could only fail one way, and a
   bed muted to silence sailed through it — the same one-directional shape as
   the timing check this skill opens with. Compute loudness over the voiceover
   regions and over the bed-only regions, on the mix and on the bed stem, and
   print both results:
   - **Bed too loud** — speech sits at least **9 LUFS above** the bed underneath
     it. Below that the duck did not work: a bed that merely got quieter overall
     passes a casual listen and still buries a quiet line.
   - **Bed vanished** — the bed under speech stays within **12 dB of its own
     bed-only level** and remains measurably present, never digital silence.
     Deeper is a mute wearing a duck's name; the music plays *through* the
     line, just lower.
5. **Normalise the finished mix to −16 LUFS.** A mix that is merely "not clipping"
   is not normalised. Normalise **after** ducking, never before: normalising first
   re-raises the bed you just ducked.

Both figures are defaults, stated here so they stop being decided fresh each time.
Report the numbers used — a mix whose levels are undocumented cannot be matched by
the next ad in the campaign.

## Stage 8 — Burn the on-screen text, last

Run only after every re-rendering step is complete. Extend, reframe, restyle,
upscale and re-concatenation all redraw pixels, and burned text does not survive
them.

Drive it from the manifest's `overlay` column, not from memory of the brief. For
each row with an `overlay`, burn it over that window.

**An overlay is text *or* an image, and the image is the one that gets forgotten.**
A run burned the wordmark as type and **never placed the logo file at all**, because
the column was called `text` and a logo is not text — so nothing in the manifest
could hold it and nothing noticed it was missing. If the user supplied a logo, a
badge, a QR code or any other asset, it is an overlay row with a file path, and it
is checked at the end of this stage exactly like a string is.

**Then check the overlay does not land on the subject.** The same run put the logo
and the end-card type on top of the man standing on the mountain, which passed every
check because every check asked whether the text was *present*, not whether it was
*legible against what is behind it*. Before burning:

1. Sample the frame at the middle of the overlay's window.
2. Measure the region the overlay will occupy — busyness and contrast against the
   overlay's own colour.
3. If the region is not clear, **fix the picture, not the text**: reframe or scale
   the underlying shot to move the subject out of the overlay's area, the way that
   run finally did with a ~1.25× zoom and a horizontal shift. Moving the overlay
   instead is the second choice, because a lockup that wanders between ads is a
   brand problem.

A reframe here re-renders pixels, so it happens **before** the burn, never after —
which is the same ordering trap as stage 8 itself, one level down.

**Set the type to a system, not by eye.** An overlay drawn with default font sizes
and a guessed position looks exactly like what it is, and "the end card looks
plain" is the result. `fal-motion-graphics` carries the system this stage needs;
use these numbers:

- **Cap height as a percentage of the short edge**, never a pixel size — an eyebrow
  at 2.5–3.5%, a title at 9–16%. A pixel size that looked right at 1080 is wrong
  at every other delivery size.
- **Tracking bands** — uppercase eyebrows opened +8 to +12%, display titles at −2
  to 0%.
- **Computed stroke and shadow**, scaled off the type itself:
  `stroke_width = max(2, round(0.05 × cap_px))`, shadow offset `0.04 × cap_px`.
- **A layout chosen deliberately.** For a product end card: near-empty field,
  title low and centred, eyebrow directly above.
- **A logo gets clearspace, not a guess.** Take the lockup's clear space and any
  minimum width from the brand files or the brand's official site, as
  `branded-graphics` sources them; honour both, and if the frame cannot give the mark its clearspace, the mark is
  too big for the frame.

Load `fal-motion-graphics` for the full system — the unit grid, the font ladder,
plate opacity — rather than reproducing it from memory. If it will
not load, the five bullets above are the minimum, and say the type was set without
the full system.

**Then do the burn in the sandbox, with PIL and ffmpeg. Do not treat it as a
caption job.** The two jobs look alike and are not. *Captions* take their
timings from transcribing the video's own audio — never estimated from a
script, never guessed from duration — and a caption pass stops rather than
falling back to evenly spaced captions. Lower-thirds, a brand name and an end card are none of
those things: they are script-driven text at author-chosen windows, with no spoken
words to transcribe. Asked to place them, a correct caption pass would
refuse, and a careless one would invent timings. Neither is what this
stage wants.

A caption pass **is** right for one thing here: burning captions of the
*voiceover* (stage 8b) if the user asked for captions as well. That is a separate, optional
deliverable, it transcribes the mixed audio after stage 7 (demux it first:
`prepare_media_transform` `extract_audio`, or 9a in the sandbox; run
`fal-ai/elevenlabs/audio-isolation` first when a music bed sits under the
voice, as `fal-audio-generation` says), and it burns in the
same encode as the lower-thirds rather than instead of them.

**Never deliver a cut with an unburned `overlay` row silently** — that includes an
image asset as much as a string, since the logo is the one that went missing. If it truly
cannot be burned, it is an undelivered part of the request; say which strings are
missing.

## Stage 9 — Watch and listen to the finished file

**Nobody has seen the ad yet.** Every check so far measured a component. This stage
is the first and only look at the thing being delivered, and it exists because a
pipeline whose parts all pass can still assemble into something wrong.

Run both passes on the **final** file, after stage 8.

**Watch.** Send the delivered video to `fal-ai/video-understanding` with
`detailed_analysis: true` and a prompt that asks for what you can check rather
than for an opinion: the number of distinct scenes, what physically happens in
each, any on-screen text read back verbatim, and whether any shot appears static.
Then reconcile against the manifest — scene count equals row count, each `action`
is described, each `text` string is read back correctly. A vision pass is **not** a
substitute for the per-clip motion measurement; it is a check on the assembly.

**Listen. Step one is demux, and it is a step because a warning did not work.**
An earlier version of this skill said, in bold, that `scribe-v2` takes an
`audio_url` and that an `.mp4` 422s — citing the run that lost a step to it. The
next run sent the `.mp4` anyway. Emphasis is not enforcement (rule 28), so:

**9a. Demux the mix to an audio container. Print the output path and its size.**
Then and only then, 9b uploads it and 9c sends the URL. If you are about to call
the transcript route with a path ending `.mp4`, you have skipped 9a.


`scribe-v2` takes an `audio_url`, and an `.mp4` handed to it **422s**, which is how
one run lost a step. Extract the mix to a bare audio container in the sandbox
(`ffmpeg -i cut.mp4 -vn -acodec libmp3lame mix.mp3`), upload that, and send its
URL. "The mixed audio" means an audio file, not the video that contains it.

Then send it to `fal-ai/elevenlabs/speech-to-text/scribe-v2`, which returns
word-level `start` and `end` times. That transcript is what makes the timing claims measurable instead of
asserted. From it, compute and report:

- **Largest silence** — the biggest gap between consecutive words, and where it
  falls. **This is the check that matters, and the one that catches an
  eighteen-second voiceover sitting in the front of a thirty-second ad.** No gap
  over `2.5s` anywhere, none over `1.5s` at the tail. Report the figure and its
  timestamp every time, pass or fail.
- **Speech coverage** — total speech time over runtime, reported *next to* the
  largest gap and never on its own. Coverage alone cannot tell a well-spread ad
  from a front-loaded one: eighteen seconds of speech in thirty is a good ad when
  the gaps are even and a broken one when they are not, and the coverage figure is
  identical in both cases. A low coverage number with small gaps needs no fix.
- **Per-fragment placement** — the first word of each fragment against its
  `vo_start`, and the last word against the end of its shot's window. A fragment
  whose words fall outside its own window has crossed a scene boundary, which
  stage 5 forbids.
- **Empty thirds** — whether any third of the runtime contains no speech at all.
- **Transcript fidelity** — the words heard against the words scripted. A speech
  engine that dropped or mangled a brand name is a defect no visual check sees.

**What this stage does when something fails.** It reports, with the numbers, and
does not silently re-render — re-rendering costs money and the user is entitled to
the choice. Name the failure, say which fix it needs (a longer line, a moved
boundary, a re-recorded segment, a re-burn), and deliver the file with the finding
attached. Never describe a cut as finished when this stage found a fault in it.

**Do not use `google/gemini-omni-flash` for this.** It is a text-to-video
*generator* — its input is `prompt`, `duration` and `aspect_ratio`, and its output
is a new video. Sending the finished ad to it produces an unrelated clip and
reviews nothing. The name suggests an omni-modal reviewer and it is not one; the
two endpoints above are.

## Stage 10 — Deliver

**Hand back the stems, not just the cut.** Every one of these already exists on
disk as a byproduct, so keeping them costs nothing — and not keeping them is what
turns "make the music quieter" into a re-render. Deliver alongside the final file:

- the **picture cut with no audio at all**,
- each **voiceover fragment** as its own file, named by shot number,
- the **music bed** before ducking,
- any **sound-effect** files,
- the **manifest** itself, including every `vo_start`, `render_dur` and trim,
- and the **native clip audio** as a stem if intake chose to keep it.

With those, any later change of mind about levels, ducking, a line's placement or
the bed is a free re-mix in the sandbox. Without them it is a re-generation. A run
that had to relight, re-animate and swap one shot, and separately re-do the whole
mix for ducking, would have been minutes of local work instead of new calls.

Then state, in one short block:

- Runtime, shape, and the route each clip used.
- **Per clip:** its motion figure, the floor, and the frozen control — so a reader
  can tell a measurement from an opinion.
- **Largest silence measured at stage 9**, with its timestamp, and speech coverage
  beside it — the two are read together or not at all.
- Per-fragment placement: each fragment's measured first word against its
  `vo_start`.
- Mix: the **measured speech-to-bed separation in LUFS** against the 9 LUFS floor,
  the **bed's duck depth against the 12 dB cap** (the music dipped, it did not
  stop), and the final programme loudness. A duck setting is not evidence the
  duck worked.
- Overlays: each string, that the vision pass read it back, **each image asset and
  where it was placed**, and the clearance check on the region behind it.
- **Timing honesty:** each shot's `dur` against its `render_dur`, and which end any
  trim came from. A cut that lands at 30s by trimming is fine; one that lands there
  silently is not.
- **Look continuity:** the `look` of each shot in order, so a broken ramp is visible
  in the record rather than only on screen.
- **Native clip audio:** kept as a stem, or discarded — and if discarded, that
  recovering it later means re-rendering every shot.
- Total cost, and the count of reshoots.

Anything the user chose that weakened a check — waiving the fence, accepting a
flagged-static clip, shipping without music, accepting a coverage figure under the
floor — is named here once, without argument. They made the call; the record shows
it.

## Guardrails

Each states the action it takes on its own, with no further input required.

- **Never invent on-screen text, a brand name, a price, a claim or a URL.** Those
  come from the brief or the `On-screen text` field. With neither, the ad ships
  with no text and the delivery says so.
- **Never fix a timing overrun by speeding up the read**, and never fix an
  underrun by stretching or looping audio. Change the words or change the window.
- **Never pad the script to fill the runtime.** A script shorter than the ad is a
  pacing fact, not a shortfall. Spread the air (stage 1b); do not write filler
  sentences, repeat the brand name, or add a line nobody asked for. Words invented
  to fill time are words nobody approved, and on an ad they are a claims risk as
  well as a quality one.
- **Never generate the voiceover as one continuous read**, and never let the voice
  drift between fragments. Pin it once and reuse it.
- **Never let a voiceover line cross a scene boundary.** Move the boundary and
  re-derive the manifest, or trim the line.
- **Never continue past the fence without an answer.** Stop and deliver.
- **A re-cut cancels every downstream step already planned or queued.** After a
  reshoot or a re-mix, a pending burn-in, transcript or QC step was queued against
  a file that no longer exists, and a row parked as failed earlier is now
  meaningless. One run finished with two stale steps still pending — an old
  text-burn the re-cut had already done, and a dead retry — and clearing them was
  manual. On every re-cut: **name what it supersedes, drop those steps, and say
  which you dropped.** A queue that outlives its input duplicates work at best and
  burns onto the wrong cut at worst.
- **A reshoot always invalidates the mix.** Re-mix from the stems; never patch the
  old mix. Stems make that free (stage 10), which is why they are delivered.
- **Never call a cut finished before stage 9 has run on it.** If stage 9's owners
  are both unavailable, deliver and say plainly that the finished file was never
  watched or listened to — that is a real gap in the deliverable, not a formality.
- **A shot that fails twice is not attempted a third time.** It goes to the fence
  marked failed, with the failure named.
- **Do not re-implement a sibling's job when it fails to load.** Take the stage
  table's fallback, label the output as not the specialist's, and name the missing
  skill. Stage 3 has no fallback on purpose.
- **Human faces:** any real person's likeness needs their documented consent.
  No ad ships with a recognisable real person who was not in the brief.

## Which house rules do not apply here

Every clip render is a sibling's. This skill's own model calls are the stage-2
still (`recommend_model`'s text-to-image pick), the stage-8b transcription and
the stage-9 analysis endpoints; the model-routing rules apply to those, and
each carries a named fallback in the stage table.

Its own sandbox work — concatenation, ducking, loudness normalisation, text
burn-in — is local ffmpeg and PIL, and is verified by measuring the output rather
than by trusting the command that produced it.
