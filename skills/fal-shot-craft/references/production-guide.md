# Shot Craft

The prompt is the only direction a video model ever gets. There is no set, no
actor interpreting a note, no editor saving it later — every framing decision,
every camera move and every beat of performance either lives in the prompt text
or does not exist. This skill is the craft layer for writing that text well, for
any generation route, at commercial length.

It was adapted from two sources: a prompting system built for one cinematic
model, and a story-compression method distilled from five screenwriting texts.
The model-specific grammar — required headers, dialogue tags, timestamp formats
— was removed, because it transfers to nothing else. The craft underneath
transfers to everything, and its target here is the 15–30 second ad.

**What this skill does not own.** Timing arithmetic, word budgets and shot
counts belong to `fal-script-writer`; route choice, parameters and cost belong
to `fal-video-generation`; the pipeline joins belong to `fal-video-production`.
This document changes only the *wording* of the visual prompt. It calls no
model and submits nothing.

## Step 0 — How this skill is entered

Two entries, and only one of them ever asks a question.

**Loaded as a reference by a sibling** — `fal-script-writer` Step 4 or
`fal-video-production` stages 1–3. Make **zero** `ask_user_questions` calls;
the caller owns intake. Apply Steps 1–7 to the rows being written, run the
Step 8 validator on each, and return.

**Triggered standalone** — a user asks for a clip prompt or wants an existing
one improved. Output is prompt text only, never a submission; generating the
clip is a hand-off to `fal-video-generation`, passing the finished prompt and
naming any duration or aspect the user stated. At most **one**
`ask_user_questions` card (if your host has no question tool, ask the same questions in one plain message, then in the same turn take the card's
stated no-answer action and say so), and only when the brief is missing something no
prompt can be written without. Its two possible headers are declared here —
`Action` and `Product look` — and both ride the same single card when both
fire. Everything else defaults:

| Unstated | Use | The card asks (header) only when |
|---|---|---|
| What the subject looks like | one invented visible cue, flagged at delivery | (`Product look`) the subject is a brand's product — never invent a product's appearance |
| Where it happens | the least surprising place for the action, flagged | — |
| What physically happens | — | (`Action`) always: an action is the one thing that cannot be defaulted |
| Tone or mood | read it off the brief's own vocabulary | — |

With no answer to that card, deliver the strongest prompt the brief supports
with the gaps named in one line — never stall a text deliverable on a question.

## Step 1 — One clip is one settled state and one continuous action

A generation route renders continuous motion inside one world. It cannot cut,
and it cannot change what things *are* mid-clip. A prompt written as a
transition — becomes, transforms into, morphs, resolves into, turns into,
shifts to, before-and-after — asks one clip to be two shots, and the model
answers by blending or resetting inside the frame, which reads as a glitch.
`fal-video-production` lints for exactly these verbs before submitting (its
precondition P2, added after two reshoot rounds went to this); the craft rule
is what makes the lint's fix correct: **the settled state goes in the still,
the continuous motion goes in the clip, and a change that must be *seen*
needs two clips with the cut between them.**

The same logic caps actions. One row, one physical beat. A row that names two
— tie the bag *and* set it by the window — is not compressed, it is blended,
and a blend of two actions took one production run three paid attempts.
Splitting costs nothing at the script stage and buys two independent tries.

## Step 2 — Expand a thin brief into a shootable micro-scene

Most ad briefs are a product and a feeling. Neither is shootable. Before any
prompt is worded, answer four planning rows — on paper, not in your head,
because the row you skip is the one the prompt turns out to be missing:

| Row | Decide | Where it lands |
|---|---|---|
| Place | one concrete location plus one lighting condition | the frame's anchors, restated in every row |
| Subject | the product, plus at most one person with one visible identifying cue | stable continuity wording |
| Change | the problem made visible → the product acting on it → the payoff state | the shot list's spine — an ad is a want meeting resistance, and the product is the turn |
| Sound | one environmental bed plus two or three sounds caused by visible actions | only when the route generates audio; otherwise skip the row |

Invention is bounded: add staging, light and sound freely, because they make
the premise shootable without changing it. Do not add biography, story-changing
props, or behaviour that alters what the brief claims — an invented detail in
an ad is an unapproved claim wearing set dressing. And reject any beat that
does not fit the shot count the script's arithmetic allows; the author cuts
beats, or nobody does and the render does it badly.

## Step 3 — Compose the framing from slots, not from a shot-name list

There is no approved vocabulary of shot types. Build the framing phrase from
open slots, each of which answers a production question:

`[SIZE?] [MOVE?] [ANGLE?] [TIME-OF-DAY?] [OTHER?] shot`

| Slot | The question it answers | Use it only when |
|---|---|---|
| SIZE | how much of the subject or the geography must read? | scale changed for an editorial reason |
| MOVE | is locomotion or discovery organising the view? | you can name what the camera follows or reveals |
| ANGLE | what height or viewpoint relation matters? | it buys layout, dominance, or subjectivity |
| TIME-OF-DAY | does the light condition clarify the image? | it is visible in frame |
| OTHER | which one production quality changes the result? | it is concrete — spatial, optical, or atmospheric |

**One or two modifiers is the working norm.** Three or more must each be doing
an independent job, or the phrase is decoration and the model averages it into
mush. Then put the composed phrase into a sentence that stages the world:

- *a [slot-composed] shot frames [subject] in [place] as [action]*
- *a [slot-composed] shot inside [place] as [action]*

These are sentence shapes, not templates to fill verbatim — the point is that
framing, subject, place and action all arrive in one clause, so the model
cannot honour half of them.

## Step 4 — Motivate the motion, or lock the frame and say so

One camera idea per clip. A move exists to follow something, reveal something,
or press on something; if you cannot finish the sentence *the camera moves
because…*, the shot is locked off — and a locked frame is written explicitly
("locked off, no camera move"), because an unpinned camera drifts and the
drift reads as indecision.

When a move is qualified, qualify it concretely and once. A local reframe or a
substantial travel; a slow inspecting creep or a fast pursuit. Middling
qualifiers — moderate, medium, somewhat — are averaging instructions, and the
model averages. And never state speed twice ("a slow push-in, moving slowly"):
duplicated direction does not reinforce, it just spends words the action
needed.

## Step 5 — Cut only on change, and carry an anchor across every cut

A cut is a claim that something changed: information, power, location, action
phase, or point of view. If nothing changed, it is the same shot continued and
the rows should merge. Each shot gets **one dramatic function** — establish,
pressure, turn, payoff — and a shot that cannot name its function is padding.

Every cut carries at least one continuity anchor, named in both rows:

- the active subject,
- a handled object,
- an eyeline,
- continuous motion,
- continuing sound,
- or the scene's objective.

In this corpus the anchor lives in the script table's `Carries in` column and
the production manifest's `look` field — this step is the craft reason those
columns exist. And because every clip is rendered blind to its neighbours, the
anchor is *restated inside the receiving row* in absolute terms; a row that
says "same kitchen as before" generates a different kitchen.

Two sequencing rules that do the most work at ad length:

- **Meaning lives between clips.** A reaction shot placed after a reveal writes
  the emotion without a word of copy, and a held, silent reaction is often the
  strongest beat in the piece. If the ad has one human in it, spend a shot on
  their face *after* the product acts, not while it acts.
- **Vary the framing.** No two adjacent shots of the same subject at the same
  size and angle; reserve the tightest framing of the whole piece for the one
  piece of irreversible information — the product doing the thing, the payoff
  state — so scale itself marks what matters.

## Step 6 — Compress the story to ad scale

- **One main event.** Thirty seconds carries one change, told once. Every beat
  added past that subtracts legibility from all the others — cram is the
  single most reliable way to make a generated ad feel like noise. If the
  brief wants three ideas, that is three ads.
- **Fast pacing multiplies cuts, not ideas.** A frenetic cut is still one main
  event, told as a run of 1–2.5 second fragments — each fragment one settled
  state with one action, all of them sharing anchors so the run reads as one
  thing accelerating rather than several things interrupting. Cram is a second
  idea, never a sixth shot.
- **Enter late, leave early.** No arrivals, no greetings, no establishing the
  day before the point. The first frame is already mid-action, and the last
  frame leaves the moment the changed state has had time to read — the final
  shot needs real seconds for that, which is the script's arithmetic problem
  but this skill's reason.
- **The engine is resistance.** Someone or something wants a result and is not
  getting it; the product is the turn. Show the want *failing* before the
  product and *satisfied* after it — shown as behaviour, never narrated as a
  feeling.
- **The mute test.** Play the piece silent in your head: the problem, the
  turn and the payoff must still track, because most feeds autoplay muted and
  because a story that needs its words has not used its pictures. Copy earns
  its place on top of a legible silent film, not instead of one.
- **End on the strongest image.** The last shot is the one the viewer keeps.
  It shows the changed state — never a recap, never a second helping of a
  beat already played.

## Step 7 — Words that render

- **The specific gesture, never the named emotion.** No actor exists to
  interpret "she looks relieved". Write what a camera would see: *her
  shoulders drop and she sets the phone face-down*. Every internal state
  either becomes one visible behaviour or comes out of the prompt.
- **Three concrete setting details per frame.** A place is not a noun; it is
  the two or three touchable things that make it this place and no other.
  Fewer and the model invents them, differently in every shot.
- **Present tense, active voice, screen order.** Describe what is happening,
  in the order the eye should find it.
- **Self-contained rows.** Everything a row needs — wardrobe, location, prop,
  light — is written in that row in absolute terms, every time, however
  repetitive it reads. Repetition is the mechanism of consistency; see Step 5.
- **No lettering in the prompt.** On-screen text is burned in the edit, last —
  models render type unreliably, and a misspelt brand name in a paid clip is a
  reshoot. `fal-script-writer` carries the same rule; the prompt describes the
  clean plate.
- **No spoken lines unless the route renders speech.** Whether it does is a
  schema fact `fal-video-generation` owns, not an assumption; a prompt written
  with dialogue for a silent route spends words on the inaudible.

## Step 8 — The validator, printed

Run against every finished prompt or row, and **print one line per check** —
a check whose only output is confidence leaves no trace of not having run.
An inapplicable check prints n/a, which is a pass.

1. `settled state:` no transformation verbs (becomes, transforms, morphs,
   resolves into, turns into, shifts to) — print `none` or the list found.
2. `one action:` the row names exactly one physical beat.
3. `framing:` the slot-composed phrase, and each modifier's job in two or
   three words.
4. `camera:` the move's motivation, or `locked off — stated in prompt`.
5. `anchor:` what carries in from the previous row, restated here in absolute
   terms — or `opening row`.
6. `function:` this shot's one dramatic function, one word.
7. `gesture:` no bare emotion adjective doing a behaviour's job — print the
   offender or `none`.
8. `setting:` the three concrete details, listed.
9. `mute test:` (whole piece, once) problem, turn and payoff each visible with
   the sound off — name the shot number carrying each.
10. `lettering and speech:` no text in frame, no dialogue on a silent route.

**Worked pair — the same 6-second beat, so the checks can be seen failing.**
The flat version is the known-bad artefact; keep it, because a validator only
proven on good prompts has never been asked to say no.

> **Flat (fails 1, 3, 4, 7, 8):** *A tired woman in a kitchen becomes happy
> and relieved as the smart kettle makes her morning better, cinematic,
> beautiful lighting, 8k.*

> **Craft:** *A waist-level medium shot inside a narrow galley kitchen at
> grey dawn frames a woman in a creased work blazer as she stops jabbing at a
> chirping oven clock, turns to the matte-black kettle already pouring, and
> her shoulders drop; steam rises past the window's rain. Locked off, no
> camera move.*

Line one earns its failures in the log: `settled state: becomes` ·
`framing: none composed` · `camera: unstated` · `gesture: happy, relieved` ·
`setting: one detail`. The craft version prints clean, and the difference is
the whole skill.

## Hand-offs

All pipeline hand-offs, one line each: `fal-script-writer` owns the table this
craft is applied to — its durations, word caps and beat budget are the
contract, and nothing here re-derives them. `fal-video-generation` receives
one finished prompt per clip and owns route, parameters and cost.
`fal-video-production` receives nothing from this skill directly; it loads
this document while wording or reviewing rows. If a sibling that should load
this document cannot, its own row minimums stand and the delivery says the
craft reference was unavailable.

## Guardrails

Each states the action it takes on its own, with no answer required.

- **Never invent a claim, a statistic, a price, a brand line, or on-screen
  text.** Those enter through the brief or the script, with the script
  skill's substantiation rules. A prompt that seems to want one proceeds
  without it, and the reply names the gap in one line.
- **Never invent a product's appearance.** Stage it, light it, move around
  it — its look comes from the brief or a supplied image, and with neither
  the prompt describes placement and light only and says so.
- **Invention stops at staging.** Light, weather, surfaces and sound may be
  invented freely; biography, story-changing props and behaviour that alters
  the brief's premise may not. Where the premise cannot be made shootable
  inside that boundary, deliver the prompt with the minimum invention flagged
  rather than stalling.
- **Never promise what rendering cannot deliver** — legible lettering,
  lip-sync, or identity fidelity across shots. Wording affects odds, not
  guarantees, and the reply never claims otherwise.
- **A recognisable real person who is not in the brief does not enter a
  prompt** — not as a named likeness, not as a described one. This skill's
  safe action is simply to write the scene without them.
- **The user's explicit instruction beats any rule here.** If they want the
  emotion named or four modifiers stacked, write it their way and note the
  craft cost in one line — this document is leverage, not law.

## Which house rules do not apply here

This skill calls no endpoint, names no parameter and generates nothing, so the
schema, optimise-flag, upload and liveness-measurement rules do not apply, and
with no route there is no fallback to name — every generation lands on
`fal-video-generation`, which owns its own routing table and fallbacks. The
rules this document does apply: one mechanism per outcome (framing is composed
by slots and nowhere else), intake that can go to zero calls, guardrails that
act without answers, checks that print artefacts, and pipeline hand-offs that
say what travels and in what shape.
