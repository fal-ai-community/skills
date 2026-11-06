# Script, voice and the presenter on camera

## 1. The script

**Shape.** A presenter-led video is mostly voice-over over scenes. The presenter's face frames it.
- **The hook:** the presenter on camera, 1–2 sentences. It states the question or the surprising fact.
- **Sections:** voice-over, one idea each, each with its scene (an animation or b-roll).
- **The presenter in the middle, only when needed:** a verdict or a personal judgement the pictures can't carry, or the turn between the two halves of a long video. Never out of habit between sections.
- **The close:** the presenter's last line: the verdict or the one takeaway. At most one question, and only as the very last spoken line.
- **The end card:** 3–4 s after the close (below). The video never ends on its last spoken word.
- **Lengths:** ask for one. Without an answer, propose 90–150 s for a 9:16 reel and about 2 min for a 16:9 explainer. Plan 4–7 b-roll clips or scenes per 30 s of voice-over.

**How much presenter.** A face in the hook keeps viewers watching; too many appearances in between slow the story down. Keep host clips to about 15 % of the runtime or less:
- a reel under 45 s: the hook and the close only, one short sentence each;
- up to about 2 min: the hook, the close, and at most one appearance in the middle;
- longer: at most two in the middle.

**The end card.**
- One more animation scene in the video's own look (design.md), 3–4 s, placed as a `card` segment after the last line (assembly.md §1).
- It shows the video's main object, or the ground it ended on, at rest, plus one short line: the takeaway in at most six words, or the user's handle or channel name when they gave one.
- Optionally, a small "Follow for more" in the video's language under that line. Set it quiet, in the card's own type: not a button, a badge or an animated arrow. Never invent a handle, a URL or any other call to action.
- It moves: the object settles and the line lands within the first second, then a slow drift carries the rest. A still image would be a freeze.
- No voice and no captions. The music resolves on a final chord over it (sound.md §1). At most one soft SFX, as the object settles.

**Writing.** Use plain declaratives built on checked facts, numbers and dates. Run this device list over every line before showing it:
- **Teaser openers:** "Nothing you're about to see ever happened." Start on the first fact instead.
- **Negation runs and fragment triads:** "This cat doesn't exist. Neither does this dog." / "No camera. No actors. No set." Say what happened.
- **"Not X but Y" and maxim closers:** a second sentence that repeats the first as a slogan. Cut it, unless both halves are facts the video established.
- **The straw man:** "It's tempting to think X. It isn't." If someone really held the wrong belief, name who and when.
- **Aphorisms, PR closers and taglines** with no fact in them. At most one closing line, built from the video's own material.
- **Reveal punchlines and payoff fragments:** "Now there is." Explain in full sentences instead.
- **Hype words and "imagine":** amazing, incredible, surprising, picture this. Give the fact with its number instead.
- **Stacked rhetorical questions:** one question at most, and never before the first fact.
- **Meta and agenda lines:** "In this video I'll…". Start on the first real fact or action.
- **Disclaimers:** no "made with AI" line unless the user asks for one.
- **Determination filler:** "they never gave up". Let a fact carry the effort.

**Facts.**
- Research on the day, and put the sources (URLs with the date read) in `script.json`.
- Say each fact at its source's strength. A number on screen needs its source line in the scene.
- No praise for a company or product unless the user asks for it; let the facts speak.

**`text` and `tts`.**
- `text` is the screen and caption form ("2019", "84%").
- `tts` is what the voice reads ("twenty nineteen", "eighty-four percent", a name respelled the way it is said).
- `host_reel.py` maps the captions back to `text` through difflib.

**The script** as one JSON document in the project (the line ids become the edit's `lines`; save it in the local workspace as `./project-work/script.json`):
```json
{"voice": "<ElevenLabs voice id>", "language_code": "en", "stability": 0.5, "similarity_boost": 0.95, "seeds": [101, 202, 303],
 "topic": "…", "sources": ["https://… (read <date>)", …],
 "lines": [{"id": "H1", "kind": "host", "text": "Honey sealed in a jar can stay edible for centuries."},
           {"id": "V1", "kind": "vo", "text": "Its water content is about 17%.", "tts": "Its water content is about seventeen percent."}, …]}
```

**Approval (gate 1).** Show the lines with the scene list (per line, what the screen shows) and the whole video's estimated cost. Make no takes before the user says yes. The presenter's lines especially need approval, because the presenter's own mouth will say them.

## 2. Voice takes

- **Takes:** one `fal-ai/elevenlabs/tts/eleven-v4` call per line and seed (101, 202, 303): `text` = the line's `tts` (or `text`), `voice`, `stability` 0.5, `similarity_boost` 0.95, `language_code`, `seed`, `output_format` `mp3_44100_192`. The cost is $0.08 per 1,000 characters × 3.
- **Files:** download each take into the local workspace as `./project-work/vo/<id>_s<seed>.mp3`.
- **Scribe:** one call per take (`language_code` `eng`, `tag_audio_events` true, `diarize` false). Save the result JSON as `./project-work/vo/<id>_s<seed>.scribe.json`. `host_reel.py` and `wordtimes.py` read these files.

**Settings.**
- The voice is the ElevenLabs voice id given for this video, with stability 0.5 and similarity 0.95. Fix `language_code` now.
- No `[softly]` or whisper tags: they sound affected. A light `[curious]` is the most a narrator gets.
- **Accent:** when a cloned voice reads with an accent the user doesn't want, an Eleven v4 audio tag at the start of `tts` steers it (`[American accent] `, `[British accent] `…). Keep the tag out of `text` and the captions, and run Scribe on the first take to make sure the tag isn't read aloud before recording the rest.

**Picking (gate 2).**
- Send the takes as one numbered clip or a few files, and the user picks.
- Measure first:
  - Scribe text against the script, to catch dropped or added words;
  - length: the faster take is not automatically better.

**Names and brand words.**
- Respell them in `tts` until they sound right. IPA between slashes (`/ˈnaɪki/`) works in Eleven v4, but at the start of a sentence it can add an odd pause: use a plain respelling there.
- Let the user hear every brand instance in context, in one numbered clip, **before paying for host clips**.

## 3. The presenter and the set

**Identity.**
- The presenter's character in Assets if there is one. Otherwise ask for three photos: front, a second front and a three-quarter view.
- Keep what the presenter wears on camera (glasses, clothes) the same across the video.

**The presenter still.** H3 Max Lip Sync animates one still (§4), so the room, the light, the clothes and the framing are the still's, and every host line made from it matches.
- **One per set, made once:** the presenter in the set, mouth closed, eyes open, looking into the lens, framed for the format (9:16: head and shoulders in the upper half, a plain area below where the captions sit; design.md §2). Keep it as `./project-work/refs/<set>_still.jpg`, saved as an output, and reuse it for every host line in that set.
- **Strongest likeness:** frame 0 of a Seedance 2.5 US reference-to-video clip made from the presenter's three photos and the set described in words (desk, lamp light, bookshelf, clothes), taken before the model starts to speak (models.md §9; 4 s at 1080p is about $4.70, once per set).
- **Cheaper:** a Nano Banana Pro still from the same photos ($0.15). Likeness varies more; compare it with the photos.
- **The user's yes first:** whichever way it was made, show the still and get a yes on the likeness before the first lip-sync clip.
- **A little variety:** another frame of the same Seedance clip, mouth closed, gives a host line a slightly different pose in the same set.

**Third parties.** Never show public figures. Any other real person, and any voice cloned from one, needs that person's consent. Stock ElevenLabs voices need none.

**Language.** Lip-sync makes host clips language-specific, so the language is fixed before the first paid clip.

## 4. The presenter on camera: H3 Max Lip Sync with the voice take

`minimax/h3-max/lip-sync/image-to-video` animates the presenter still (§3) so that the presenter says the picked take. The lips are made from the take itself, so nothing is retimed in assembly: the clip plays 1:1 and the take goes back on where it sits.
- **Audio:** `python3 tools/host_lipsync.py prep vo/H1_s101.mp3 refs/set_still.jpg clips/H1` (from `./project-work`) places the take's speech (from 0.04 s before its first sound to 0.12 s after its last) at 0.30 s, adds 0.40 s of silence and pads to the model's 5 s minimum. The level is untouched. The clip lasts exactly as long as this audio.
- **Inputs:** `image_url` (the still; aspect ratio 0.4–2.5), `audio_url` (that wav), `resolution: "1080P"` (the default is 768P), `enable_transcription: true` (the model transcribes the audio to guide the lips). There is no prompt.
- **Output:** 1080×1920 from a 9:16 still, 24 fps, as long as the audio. The head, the eyes and the hands move naturally, the mouth closes in the take's pauses, and the set stays the still's. The clip's sound is the wav resampled to 32 kHz: the mix uses the take itself.
- **Price:** about $0.16/s at 1080P (the pricing API can show 0 while a model is in early access; never quote 0), so about $0.80 for a 5 s line. Past 15 s each second costs 1.2×.
- **Into the edit:** `python3 tools/host_lipsync.py measure vo/H1_s101.mp3 clips/H1.mp4 H1` cross-correlates the clip's sound with the take. It prints `take_at`, where the take's 0 s sits in the clip (0.30 − (first sound − 0.04), usually 0.20–0.29 s), with a correlation of at least 0.98 (lower means the clip isn't that take), and the host segment for the edit: `{"kind": "host", "line": "H1", "clip": "clips/H1.mp4", "take_at": 0.28, "lead": 0.12, "tail": 0.25, "push": 0.03}`. host_reel.py plays the clip 1:1 (`"sync": "clip"`, the default) and puts the take back on at `take_at`.
- **Check:** run `host_check.py` on the finished video (assembly.md §3). Each host segment's picture is compared with its clip (r ≈ 0.99, no frame off) and the voice with the clip's own sound (within ±20 ms). Then watch every host segment at full size: lips, identity, hands.
- **A closed mouth in a pause is right.** An automatic video analysis can call the mouth closing in the take's pauses a "jump". Look at the take's level there before regenerating a clip.
- **Language:** the lips follow whatever language the take speaks; nothing else to set.

**Never retime the presenter's face.** No speed-up, slow-down, frame skip, frame blend or warp to fit a voice. A retimed face reads as broken video and loses the voice's own rhythm. Anything that changes how the presenter looks or sounds waits for the user's yes.

**Other lip-sync routes** (models.md §9) need the user's yes, like any change to how the presenter looks or sounds. Before using one, make a single line with it and check its output frame rate and size: a clip that isn't 24 fps repeats or drops frames in the master, and the face is where that shows. A reference-to-video model given the take as an audio reference (Seedance's `@Audio1`) re-performs the line at its own tempo, so the take can't sit on its lips; use it for presenter stills (§3).

## 5. Host segment keys (the edit)

| Key | What it does | Used |
|---|---|---|
| `take_at` | where the take's 0 s sits in the clip, from `host_lipsync.py measure` | required |
| `lead` / `tail` | seconds kept before the take's first sound and after its last | 0.12 / 0.25 (0.4–0.6 on the last host clip: a breath before the end card) |
| `push` | slow zoom-in across the segment, with a sub-pixel crop (whole-pixel steps make the face jump every few frames) | 0.03 |
| `sync` | `"clip"`: the clip plays 1:1 and the take goes on at `take_at`. `"video"` and `"audio"` are for clips that re-voiced the line: they retime the face or cut the take, so they need the user's yes | `"clip"`, the default |

The plan ends with the cut check: every voice cut, b-roll ones too, must fall in a real pause of its take, because Scribe marks word starts 0.01–0.11 s after the sound begins. A `CUT` line is a cut inside a word or inside connected speech; fix it before rendering (at a b-roll join, move the line's `words` split to a word followed by a real pause). A host segment in clip mode never cuts its take.

## 6. Non-English videos

Everything above holds, with these settings:
- The script: the language's `language_code` (`"de"`, `"es"`, `"tr"`…). Respell foreign words the way the language would say them, write a lone letter out as a word, and listen to every name.
- Scribe with the language's code for the takes.
- The host clips are made from those takes (§4); nothing else changes for them.
- Captions: `"caption_func_words"` in the edit lists the language's function words (its words for and, with, a, this…), so no phrase ends on one (assembly.md §1). Check that the caption font has every letter the language uses (for example İ and ı in Turkish, ł and ż in Polish, ő and ű in Hungarian).
- Scene pages: run `check.py` on every string. Some display faces lack accented capitals.
