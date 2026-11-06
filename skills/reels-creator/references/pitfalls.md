# Pitfalls: symptom → cause → fix

Things that go wrong in presenter-led videos, and what fixes them. Look up the symptom first; most have a measurable check. Scene-building faults (blended counters, labels off-centre, glyph gaps, seek-order bugs) are in animation-craft.md §3.

## 1. The presenter on camera

| Symptom | Cause | Fix |
|---|---|---|
| The lips speak at a different tempo from the voice, or the clip's voice isn't the take | a reference-to-video talking-head model (for example Seedance with the take as `@Audio1`) re-performs the line at its own tempo and with pauses the take doesn't have, so the take can't sit on its lips | make host clips with H3 Max Lip Sync from the take itself (voice-and-host.md §4) |
| The face stutters, races or repeats frames | the clip was retimed to fit the voice (frames picked, skipped or blended), or a 24 fps clip was cut at 30 fps (every 5th frame repeats; a 60 fps source drops frames in a 2:3 pattern) | never retime the face; a 24 fps master; `host_check.py` counts repeated frames and must pass |
| The face shifts by a pixel every few frames during a slow push | the zoom used whole-pixel crop boxes | a sub-pixel crop (host_reel.py's `push` does this); `host_check.py` r ≥ 0.95 |
| A review says the face "jumps to a closed mouth" mid-sentence | usually a pause in the take, where the mouth closes as it should | read the take's level at that moment (a pause sits 30 dB or more under the speech) before regenerating anything |
| The voice sits early or late on the lips | the take was put back at a guessed offset | `host_lipsync.py measure` gives `take_at` (correlation ≥ 0.98); run `host_check.py` with the edit's own plan, since a plan rebuilt with guessed in-points shows false offsets of about a frame |
| A check or an agent says "lip sync matches", but it looks off | matching word times is not lip-sync, and an automated claim may not have looked | a 10 fps mouth strip (crop the mouth, tile 15–20 frames) next to the voice level per 0.1 s, then watch it at full speed |
| The presenter flashes on screen for under a second | a fallback (a card, a cutaway) with no minimum on-camera time | keep the presenter on camera for at least 1.5 s with matching lips, or drop the presenter from that moment |
| A host segment starts on a repeated frame (`host_check.py`: one repeated at the first frame, or r well under 0.99) | the clip's in-point fell between two frames, so the decoder filled the first frame twice | the current host_reel.py snaps every in-point to the frame grid: use it, not an older copy |
| The room, light or framing changes between host clips | each clip came from a different still | one presenter still per set, reused for every host clip (voice-and-host.md §3) |
| The video feels like a talking head | host clips over about 15 % of the runtime | the presenter opens and closes; in between only where the story needs a face (voice-and-host.md §1) |

## 2. Voice, cuts and captions

| Symptom | Cause | Fix |
|---|---|---|
| The first sound of a word is clipped ("ine" for "nine") | cuts were set from Scribe's word times, which mark a word's start 0.01–0.11 s after its sound begins (about 0.05 s typically) | set every voice cut from the take's sound, in its silence; the plan's cut check lists any cut inside a word |
| The presenter seems to stutter on a phrase | the take was split inside connected speech and a gap opened | split a take only at real pauses (≥ 40 dB under its speech level); the cut check lists splits inside connected speech |
| A brand name or foreign word comes out wrong | the model guessed the spelling's sound | respell it in `tts` (the screen form stays in `text`), then confirm it with Scribe on every take |
| A cloned voice drifts to another accent in another language | the clone leans to the accent of its source recording | an accent tag at the start of `tts` (for example `[American accent] `), kept out of `text` and the captions; check the first take with Scribe so the tag is never read aloud |
| A caption's tail lands on a UI scene | a phrase ran past its segment | `"captions": false` on the scene's segment; the review sheet must show no captions on UI scenes |
| A caption hangs over the first frames of the next shot | a phrase stays up to 0.45 s after its last word | the current host_reel.py ends every phrase at the next cut |
| The voice sits 20–50 ms off the lips after a part join, worse with every join | the parts' AAC tracks were joined directly, and each part's encoder priming adds up | join parts with `host_reel.py --join` (assembly.md §2), which joins the raw mixes and encodes the sound once |
| A take looks band-limited above 16 kHz | ElevenLabs MP3 takes carry nothing up there | expected: judge takes by ear, not by the top of the spectrum |

## 3. Picture and footage

| Symptom | Cause | Fix |
|---|---|---|
| A scene sits still for seconds | key moments placed with nothing moving between them | no scene stays still for more than 1 s: keep a quiet, continuous motion and land the key change on its word; measure it: a whole-frame difference under 0.05 for more than 1 s flags one, then compare that run's first and last frames, since a small object moving slowly can measure as low |
| A clip restarts, slows down or freezes to fill its window | the window was longer than the clip | one shot is one unbroken take: dock it into a card, morph it, or cut to a second clip |
| Logos or text appear inside generated footage | the prompt left room for them, or the model added them | say so in the prompt, look at every clip's frames, and regenerate or crop |
| Generated footage shows the wrong object for the story (the modern version of a historical thing, the wrong model of a machine) | the prompt named the category, not the exact object | name the exact object, era and material in the prompt; check the frames before the edit |
| Text covers the presenter's face or hair | the text was placed by the frame's centre | on a 9:16 talking head, use the plain area below the captions (design.md §2) |
| A regenerated shot still shows the old version in the video | the edit still points at the old file | after any retake, compare the edit's file with the new generation (sha256) and look at that shot on the review sheet (assembly.md §3) |

## 4. Sound and the ending

| Symptom | Cause | Fix |
|---|---|---|
| The video stops on the last spoken word, with the music fading under it | no end card in the edit | a 3–4 s end card after the last line while the music resolves on a final chord (sound.md §1) |
| The music dips for half a second at a part join | a part before the last kept the music's `fade_out` (2 s by default), or a part after the first kept its `fade_in` (0.3 s) | `"fade_out": 0` on every part but the last and `"fade_in": 0` on every part but the first; the plan prints a `MUSIC` line when one is left |
| The end card's last seconds stand still | the card's motion ends early | keep a slow drift running to the card's last frame |
| The finished video has no sound effects | SFX were skipped to save time | SFX are part of the video: list each scene's few, price them, and put them in the edit (SKILL.md step 9) |
| A sound feels shrill or cheap | whooshes, risers or bright synthetic hits | soft, physical sounds for things that land, dock or settle; listen to every SFX in context |

## 5. The script

| Symptom | Cause | Fix |
|---|---|---|
| The lines sound machine-written | a teaser opener, a negation run ("This cat doesn't exist. Neither does this dog."), a fragment triad ("No camera. No actors. No set.") | plain declaratives built on facts, at most one question; run the device list in voice-and-host.md §1 before showing lines |

## 6. Runtime checks

Keep intermediate files and approved scripts in a persistent local project folder.
Check actual execution limits and split long renders when needed. If a price or
account permission cannot be verified, report it before a paid call. Save pending
request IDs and resume those requests rather than submitting replacements.

## 7. Checks that mislead

| Symptom | Cause | Fix |
|---|---|---|
| A contact sheet seems a couple of seconds off | ffmpeg `fps=1/4` samples at about 4n + 2 s, not 4n | label each tile with its real time, or pick exact times with `select` |
| `host_check.py` reports a whole-frame voice offset on a clean render | the plan it read wasn't the one the video was rendered from | check against the plan written by the render itself |
