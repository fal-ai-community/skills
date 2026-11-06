# Camera and craft

Use this reference to convert story material into a compact, coherent H3 scene.

## Thin-premise expansion

This procedure is constructed guidance because the source prompt corpus began
from finished scenes. Apply it before writing the H3 record.

Create exactly four planning rows:

| Row | Required decision | Output use |
|---|---|---|
| Place | One location plus one lighting condition | Shot 1 anchors and ambient bed |
| Cast | One to three people; one visible cue each | Stable continuity descriptions |
| Change | Objective, obstacle, visible hinge, visible consequence | Shot functions and cuts |
| Sound | Environmental bed plus two or three caused events | Soundscape sequence |

Reject any added beat that cannot fit the duration's shot budget. Add staging,
light, and sound freely when they preserve meaning. Do not add biography,
history, costume, props, or behavior that alters the premise.

## Scene selection

For a pasted scene, select one playable causal spine:

1. Establish the minimum place, subject, and spatial relation.
2. Preserve the action or line that initiates change.
3. Preserve the visible hinge or scene-changing answer.
4. End on a visible consequence, decision, escape, or recognition.
5. Remove repeated exposition, greetings, duplicate declarations, decorative
   history, and spectator reactions.
6. Convert one necessary inner state into one visible physical cue.
7. Merge adjacent coverage when it serves the same causal beat.

Translate direction instead of transcribing it. Convert parentheticals into
performance verbs or manner only when they alter the beat. Repair corrupted
text minimally or omit it.

## Shot budgeting

Let `M(D)` be the measured median and `P(D)` the measured upper working bound:

| Duration band | `M(D)` | `P(D)` |
|---|---:|---:|
| 5 | 1 | 2 |
| 6–7 | 2 | 2 |
| 8–11 | 2 | 3 |
| 12–13 | 3 | 3 |
| 14–15 | 3 | 4 |

Start at `S=M(D)`. Increase only for instantly readable inserts, pursuit, or a
true montage. Decrease for sustained verbal pressure. Never exceed four shots.

Before timing, assign each shot one dominant function. Validity depends on a
change of information, power, location, action phase, or point of view—not on
equal division of seconds. Give the final consequence enough time to read.
Keep ordinary spans at least 2.5 seconds when possible and never below 2.

## Shot-type slot grammar

Do not maintain or teach an approved vocabulary of shot types. Compose the
shot phrase from open modifier slots:

`[SIZE?] [MOVE?] [ANGLE?] [TIME-OF-DAY?] [OTHER?] shot`

Each slot answers a production question:

| Slot | Question | Constraint |
|---|---|---|
| SIZE | How much subject or geography must read? | Change scale only for an editorial reason. |
| MOVE | Is locomotion or discovery organizing the view? | Name what the camera follows or reveals. |
| ANGLE | What height or viewpoint relation matters? | State its map, exposure, dominance, or subjectivity purpose. |
| TIME-OF-DAY | Does the temporal light condition clarify the image? | Use only when visually relevant. |
| OTHER | Which open production quality changes the result? | Use a concrete spatial, optical, environmental, or mood-bearing modifier. |

Use one or two modifiers by default. Three or more require independent jobs.
Comparative scale modifiers may mark editorial change between shots. The slots
are productive: invent the exact modifier the requested scene needs.

After the Shot 1 prefix, prefer either grammatical shape:

- `a <slot-composed> shot frames <subject> in <place> as <action>`
- `a <slot-composed> shot inside <place> as <action>`

These are sentence structures, not shot-type lists.

## Camera movement qualifiers

Formal qualifier domain:

- `amplitude in {small, large}`
- `speed in {slow, fast}`
- `speed` is optional.

The combinations are closed: small/slow, small/fast, large/slow, large/fast.
`medium amplitude` and `medium speed` are forbidden; each has zero occurrences
in 21,524 source records.

Choose small amplitude for a local reframe and large amplitude for substantial
spatial travel. Choose slow speed for inspection or pressure and fast speed
for abrupt movement or pursuit. Do not qualify a move merely because a slot is
available. Do not express speed twice, such as with both a speed adjective and
an `at ... speed` clause.

## Cuts and continuity

Use a clean cut by default. Repetition is acceptable. Every cut must name its
landing framing, subject, and visual priority.

Use a continuous push or pull when context and detail must remain spatially
connected. Hold when the dramatic state changes inside an unchanged
composition. Dissolve only across a genuine time, memory, or era change. Label
crosscuts and mediated viewpoints explicitly.

Carry at least one continuity anchor across each cut:

- the active subject;
- a handled object;
- an eyeline;
- continuous motion;
- continuing sound or speech;
- the scene objective.

Bridge every place or time jump through movement, communication, repeated
object, continuing sound, or an explicit temporal transition. Do not hide an
edit inside a numbered shot.

## Visual causality

Write an observable chain: subject acts on object or space, then a visible
condition changes. Name concrete spatial anchors and position people in
relation to them. Reserve the tightest or most selective framing for the
irreversible information.

For silent scenes, use action and sound to carry the causal chain. Nonverbal
breath, effort, laughter, or a gasp may be performance, but do not imply an
unwritten conversation. End on changed state, not redundant coverage.

## Craft validator

- [ ] Every shot has one dominant dramatic function.
- [ ] Every cut corresponds to changed information or state.
- [ ] Every landing view names what must read.
- [ ] Every modifier fills a slot and performs a production job.
- [ ] Every formal amplitude and speed belongs to the closed domain.
- [ ] No move repeats its speed in two forms.
- [ ] Every angle states a viewpoint purpose.
- [ ] At least one continuity anchor crosses every cut.
- [ ] Every internal state has a visible cue or was removed.
- [ ] Every foreground sound has a visible or grounded cause.
- [ ] The final shot has enough duration for the changed state to register.
