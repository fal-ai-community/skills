# Audio Generation

One router for six jobs: **Voiceover**, **Voice swap**, **Dub**, **Sound effect**,
**Music**, **Transcript**. Decide the job, take its route, run its verification.

Two things go wrong more than everything else combined. **A voice is a stored
decision, not a taste call made fresh each time** — clip four does not match clip
one because nobody wrote down what clip one used. And **speech length is set by
the words**, because not one speech endpoint on fal has a duration parameter.

## Step 0 — Intake, once, up front

One `ask_user_questions` call (if your host has no question tool, ask the same questions in one plain message and wait for the
reply before spending; that reply counts as the card). Drop any question the request already answers, and
any question that does not apply to the job (audio plus "make this Spanish" is a
Dub — do not ask about voice or length). If every field is already answered, make
**zero** calls and state the four resolved values in one line before starting.

1. **Job** (header `Audio job`) — `Voiceover`, `Voice swap`, `Dub`,
   `Sound effect`, `Music`, `Transcript`. *Default:* infer — text alone is
   `Voiceover`, audio plus a target language is `Dub`, audio alone is
   `Transcript`; if still ambiguous, `Voiceover`.
2. **Voice** (header `Voice`) — `Reuse the project voice`, `Warm male narrator
   (Brian)`, `Bright female narrator (Rachel)`, `Conversational young female
   (Jessica)`, `Deep authority (George)`, `A voice I supply` (gated by
   **Whose voice**, next section). Free text takes any preset name or a raw
   ElevenLabs voice ID.
   **A real person's name is not a voice value.** An answer naming a real
   person — `David Attenborough`, the CEO, a streamer — is not a registry miss
   to resolve or a string to submit: it trips the impersonation limit in the
   next section, before any routing. *Default:* the registry entry if one
   exists, else `Brian`. *Applies to:* Voiceover, Voice swap. `n/a` elsewhere.
3. **Length** (header `Length`) — `No target`, `Match a clip I gave you`,
   `Exact seconds`. *Default:* `No target`.
   *Applies to:* Voiceover, Sound effect, Music. `n/a` elsewhere.
4. **Delivery** (header `Delivery`) — `MP3 128k`, `MP3 192k`, `WAV / PCM 44.1k`.
   *Default:* `MP3 128k`. *Applies to:* everything but Transcript.

If the user says `just make it`, take all four defaults and skip the card.

**Words on a commercial asset.** A voiceover in a convincing human voice carries
the weight of a printed claim. If the script holds a health, safety,
environmental, financial or superlative claim (`clinically proven`, `#1`,
`FDA approved`, `carbon neutral`, `guaranteed returns`), ask on the same card
whether the user holds evidence. Having typed the sentence is not the same as
being allowed to say it aloud. Do not soften it yourself — it is confirmed and
read verbatim, or it leaves the script.

## Whose voice — the limit, read off the request before any route

This gate is about **whose voice is being asked for**, never about the
mechanism it was asked through. A supplied sample, a name typed into the Voice
field, "whichever preset sounds most like him", or performance settings tuned
toward how a particular person sounds are all the same request, and they all
land here — with or without a sample, on every job that produces speech.

**Refuse, every time, whatever the mechanism:**

- The voice of a named real person the user does not own or hold documented
  permission to use — politician, executive, celebrity, streamer, colleague —
  however the request is framed, including parody, satire, "internal only" and
  "it's only a test".
- Any script putting words in a real speaker's mouth that they did not say,
  where a listener could take it as genuine: statements, endorsements,
  confessions, announcements, instructions.
- Any sample whose origin the user cannot state.

The determination is made from the request and the script, by this skill — a
user's framing never makes it. "It's parody, so it's allowed" and "internal-only,
so it's fine legally" are the user's opinion about the law, not a consent
record, and the file outlives the meeting it was made for. Consent exists in
exactly two forms — `"consent": "owner"` or `"consent": "written permission
from <name>"` — and a legal assurance is neither.

**The safe action, taken on this skill's own authority — never blocked on a
reply:** state the refusal in one line, then carry on with the job using an
ordinary preset chosen for the brief's register — a documentary read wants a
warm measured narrator, and that need is legitimate. The genre may be honoured;
the person may not. Never shop the preset list for the closest match to the
refused person, keep the registry's neutral parameters rather than tuning
toward how anyone in particular sounds, and put no imitation instruction in
`text`. Record the choice and its reason in `audio/voices.json` so no later
clip inherits a resemblance rationale. If the user then picks a preset by name,
that pick stands — the one rationale that may not justify it is resemblance.

If a refused name was nonetheless sent as `voice`, the resulting
`422 Voice not found` is not a lookup failure to repair: do not ask for a
corrected ID, and never ask for an audio sample of that person.

## The voice registry

Write `audio/voices.json` the first time a voice is settled, and read it before
Step 0 on every later run. The path is relative to the **project root** — the
directory the project's other assets live in, the same file every run. A copy
in a per-run scratch directory defeats the registry's entire purpose, which is
that clip four can find what clip one used. Keys are **roles in the project**
(`narrator`, `host`, `villain`), not preset names; a second voice gets a second
role key, never `narrator2`:

```json
{"narrator": {"endpoint": "fal-ai/elevenlabs/tts/multilingual-v2",
  "voice": "Brian", "stability": 0.5, "style": 0.0, "speed": 1.0,
  "rate_wps": 2.82, "sample_url": "...", "consent": null}}
```

- `voice` on every ElevenLabs endpoint is a string that is **either a preset name
  or an ElevenLabs voice ID** — both verified accepted. Store what the user gave,
  verbatim. Verified preset names: `Aria`, `Roger`, `Sarah`, `Laura`, `Charlie`,
  `George`, `Callum`, `River`, `Liam`, `Charlotte`, `Alice`, `Matilda`, `Will`,
  `Jessica`, `Eric`, `Chris`, `Brian`, `Daniel`, `Lily`, `Bill`, `Rachel`.
- **Always send `voice` explicitly.** Omitted, it silently defaults to `Rachel`,
  and a run that never chose a voice then looks like one that did.
- An unknown value returns `422 Voice not found: <name>`. Stop and ask — unless
  the value named a real person, which is **Whose voice** territory, not a
  lookup to repair. A silent substitution is how a project ends up with two
  narrators.
- MiniMax is a separate namespace: `voice_setting.voice_id`, from `Wise_Woman`,
  `Friendly_Person`, `Deep_Voice_Man`, `Calm_Woman`, `Casual_Guy`, `Patient_Man`,
  `Elegant_Man`, `Lively_Girl`, `Sweet_Girl_2`, or a `custom_voice_id` from a
  clone. ElevenLabs names are invalid there.
- `rate_wps` is measured, never assumed. See Step 2.

## Routing

| Job | Primary | Named fallback |
|---|---|---|
| Voiceover, one narrator | `fal-ai/elevenlabs/tts/multilingual-v2` | `fal-ai/elevenlabs/tts/turbo-v2.5` — same schema, faster, flatter. |
| Voiceover, heavy performance | `fal-ai/elevenlabs/tts/eleven-v3` | `fal-ai/elevenlabs/tts/multilingual-v2`, when v3's missing controls matter more than its delivery. |
| Two or more speakers | `fal-ai/elevenlabs/text-to-dialogue/eleven-v3` | `fal-ai/elevenlabs/tts/multilingual-v2` per line, concatenated in the sandbox. |
| Voice swap | `fal-ai/elevenlabs/voice-changer` | Transcribe with `fal-ai/elevenlabs/speech-to-text/scribe-v2`, re-speak the exact transcript through `multilingual-v2`. Loses the original timing; say so. |
| Dub | `fal-ai/elevenlabs/dubbing` | Transcribe with `scribe-v2`, translate the text, re-speak through `multilingual-v2` with `language_code` set to the target. |
| Sound effect | `fal-ai/elevenlabs/sound-effects/v2` | `sonilo/v1.1/text-to-sound-effects` — required above 22 s, up to 180 s. |
| Music | `fal-ai/elevenlabs/music` | `fal-ai/minimax-music/v2.6` for a song with written lyrics; `fal-ai/lyria3/pro` for a one-line prompt with no length control. |
| Transcript, word timings | `fal-ai/elevenlabs/speech-to-text/scribe-v2` | `fal-ai/elevenlabs/speech-to-text` — v1 Scribe, same `words` shape. |
| Transcript, plain text | `nvidia/nemotron-asr-multilingual/asr` | `fal-ai/cohere-transcribe`, then `fal-ai/wizper`. |
| Cleaning a noisy recording | `fal-ai/elevenlabs/audio-isolation` | none — on failure, report and continue on the raw audio. |

`eleven-v3` earns its "heavy performance" row only when the **delivery is the
content** — the script carries acting directions, emotional turns or laughs
that a flat read would lose. A plain narration, however funny the words, stays
on `fal-ai/elevenlabs/tts/multilingual-v2` at registry settings. Performance
controls shape a read; they are never a channel for sounding like a particular
person (see **Whose voice** above).

Burning captions into video is **not** this skill. Produce the transcript here
(send `diarize: false` and `tag_audio_events: false`) and filter `words` to
`type == "word"`; the "Caption cues" rule in `fal-motion-graphics` groups them
into lines on the `fal-video-production` and `video-compositing` paths
(`reels-creator` keeps its own caption rules). Inside `fal-video-production`, stage 8 burns them as the `fal-motion-graphics`
Caption block in its one encode; a standalone caption job goes to
`video-compositing`, which burns the captions and any other text owed on that
file in one pass.

## Per-endpoint parameters

Fetch the schema for a route before its first call of a session.

| Endpoint | Inputs | Gotchas |
|---|---|---|
| `fal-ai/elevenlabs/tts/multilingual-v2`, `fal-ai/elevenlabs/tts/turbo-v2.5` (identical) | `text`*, `voice`, `stability` 0–1 d0.5, `similarity_boost` 0–1 d0.75, `style` 0–1 d0, `speed` **0.7–1.2** d1, `timestamps` d false, `previous_text`, `next_text`, `language_code` (639-1), `apply_text_normalization` auto/on/off | No output-format field — always MP3. Set `apply_text_normalization: "on"` for prices, dates, units, model numbers; `auto` decides for itself and reads `$1,299` inconsistently. |
| `fal-ai/elevenlabs/tts/eleven-v3` | `text`* (**max 5000 chars**), `voice`, `stability`, `timestamps`, `language_code`, `apply_text_normalization` | **No `speed`, `style`, `similarity_boost`, `previous_text` or `next_text`.** Carry performance in the text with `[excited]`, `[whispers]`, `[laughs]`, `[sighs]`. With no continuity fields, never chunk a v3 script — stay under 5000 chars or route to `multilingual-v2`. |
| `fal-ai/elevenlabs/text-to-dialogue/eleven-v3` | `inputs`* — array of `{text, voice}` turns; `stability` (rounds to 0.0/0.5/1.0), `use_speaker_boost`, `seed`, `language_code` | No speed, no per-turn timing. `voice` per block takes a name or an ID. |
| `fal-ai/elevenlabs/voice-changer` | `audio_url`*, `voice`, `remove_background_noise` d false, `seed`, `output_format` d `mp3_44100_128` | Enable noise removal only on audibly noisy source; on a clean take it thins the voice. |
| `fal-ai/elevenlabs/dubbing` | `target_lang`* (639-1), `video_url` **or** `audio_url` (video wins if both sent), `source_lang` (auto), `num_speakers` 1–50 (auto), `highest_resolution` d true | Output field is `video` in both cases — for an audio-only job, demux the audio out of it rather than expecting an `audio` field. |
| `fal-ai/elevenlabs/sound-effects/v2` | `text`* (max 450 chars), `duration_seconds` **0.5–22** (omit = model chooses), `prompt_influence` 0–1 d0.3, `loop` d false, `output_format` | Raise `prompt_influence` to ~0.7 for a literal named sound; leave low for ambience. `loop: true` for anything running under a longer scene. |
| `sonilo/v1.1/text-to-sound-effects` | `prompt`*, `duration` int **1–180** d8, `audio_format` d **`aac`** | Override `audio_format` to match Delivery — `aac` is nobody's request. |
| `fal-ai/elevenlabs/music` | `prompt` (max 4100) and/or `composition_plan`, `music_length_ms` **3000–600000**, `force_instrumental` d false, `respect_sections_durations` d true, `output_format` | `music_length_ms` and `force_instrumental` apply only alongside `prompt`, not `composition_plan`. Set `force_instrumental: true` for a bed under narration — left false it can arrive with vocals. |
| `fal-ai/minimax-music/v2.6` | `prompt`* 10–2000, `lyrics` max 3500 with `[Verse]`/`[Chorus]` tags (required unless instrumental), `lyrics_optimizer` d false, `is_instrumental`, `audio_setting` | **No length field at all** — never promise a duration on this route. |
| `fal-ai/lyria3/pro` | `prompt`* (max 5000), `image_url` | `negative_prompt` exists but is deprecated and does nothing. No length control. |
| `fal-ai/elevenlabs/speech-to-text/scribe-v2` | `audio_url`*, `language_code` (**ISO 639-3**: `eng`, `spa`, `deu`), `diarize` d **true**, `tag_audio_events` d **true**, `keyterms` ≤100 (+30% price) | Both defaults are on and both pollute a clean transcript — set them false unless asked for speaker labels or `[laughter]`. Returns `words[]` of `{text, start, end, type, speaker_id}`; `type` is `word`, `spacing` or `audio_event`, so **filter to `type == "word"` before using timings**. Put names and jargon in `keyterms`. |
| `fal-ai/elevenlabs/speech-to-text` | as above, minus `keyterms` | Same `words[]` shape. Drop-in when scribe-v2 errors. |
| `wizper` | `audio_url`*, `task` transcribe/translate, `language` (639-1, d `en`, null to auto-detect), `max_segment_len` 10–29, `merge_chunks` | `chunk_level` is a **const `"segment"`** — wizper cannot return word timings whatever the name suggests. |
| `nvidia/nemotron-asr-multilingual/asr` | `audio_url`*, `language` d `auto`, `acceleration` none/regular/high/full | Returns one `output` string. No timings. |
| `cohere-transcribe` | `audio_url`*, `language` d `en`, `punctuation`, `max_new_tokens` 1–1014 d256 | Its `timings` field is **server performance metrics, not word timings.** Never parse it as alignment. |
| `fal-ai/elevenlabs/audio-isolation` | `audio_url` or `video_url` | No options. |

**Delivery mapping.** `MP3 128k` → `mp3_44100_128` / sonilo `mp3` / MiniMax
`{format: "mp3", bitrate: 128000}`. `MP3 192k` → `mp3_44100_192` / `mp3` /
`bitrate: 256000`. `WAV / PCM 44.1k` → `pcm_44100` / `wav` /
`{format: "pcm", sample_rate: 44100}`. The ElevenLabs TTS endpoints have no
format field and always return MP3 at 128 kbps — convert in the sandbox if WAV
was asked for. `MP3 192k` is **unachievable** on those routes: never re-encode
128 kbps upward to fake it (bits invented, quality lost — see the guardrails);
deliver the 128 kbps file and say so in the delivery line.

## Step 1 — Normalise the input

If a video was handed over and the job needs audio, demux and read the source
duration in one sandbox pass:

```
ffmpeg -i INPUT -vn -ac 1 -ar 44100 -c:a pcm_s16le source.wav
ffprobe -loglevel error -show_entries format=duration -of default=nk=1:nw=1 INPUT
```

**A sandbox file is not a URL.** Upload `source.wav` and pass the returned URL as
`audio_url`; a local path fails the request. Inputs that are not the clean case:

- **Noise or music under speech**, for Voice swap or Transcript: run
  `fal-ai/elevenlabs/audio-isolation` first and route the isolated audio onward.
- **More than one speaker, for Voice swap:** `voice-changer` collapses every
  speaker into the one target voice. Confirm that is wanted, or split on
  `speaker_id` boundaries from a `diarize: true` scribe-v2 pass and swap only the
  intended speaker's segments.
- **Music under speech, for Dub:** dubbing rebuilds the speech and the bed
  survives unevenly. Isolate, dub the voice, re-lay the original bed in the sandbox.
- **Silence or no audio stream:** stop and say so. Do not run on an empty file.

## Step 2 — Write the script to length

Voiceover with a Length target only. `No target` skips to Step 3.

Length comes from the word count and nothing else. One mechanism, deliberately:

1. Establish `RATE` in words per second for the chosen voice. Measured for
   `Brian` on `multilingual-v2` at `speed: 1.0` in English: **2.82 w/s**
   (56 words → 19.83 s). A starting estimate only — voice, language and
   `stability` all move it. Store each observed value as `rate_wps`.
2. Budget `WORDS = round(TARGET_SECONDS * RATE)`, minus ~4% headroom for the
   trailing breath ElevenLabs adds.
3. Write the script to that budget and count it before submitting.

Three things that are **not** the mechanism and are barred as substitutes:

- **Time-stretching.** `atempo`, `rubberband` and every post-hoc stretch damage a
  voice, and that damage is the first thing anyone notices.
- **`speed`.** A performance setting, not a fitting lever: it sits in the
  registry so every clip matches, and it does not exist on `eleven-v3`.
- **Trimming the tail.** A cut final consonant reads as a broken edit.

Padding runs one way only: if the finished audio is *shorter* than the window,
append digital silence. Never pad by slowing the read.

## Step 3 — Submit

For a multi-part voiceover on `multilingual-v2` or `turbo-v2.5`, send one request
per part with `previous_text` and `next_text` carrying the adjacent parts
verbatim so the prosody joins, then concatenate in the sandbox with a fixed
0.35 s of silence between parts. Assemble in a script with one variable per part,
so a re-run is provably identical.

**Unless the caller supplied a window per part — then return the parts and stop.**
A caller that gave you a start time or a target duration for each part is placing
the audio itself against something you cannot see, usually video it has already
cut. Concatenating with a fixed 0.35 s gap and padding a short part with trailing
silence both *destroy* that placement: the caller wanted gaps of its own size, in
its own positions. So when per-part windows arrive, hand back **one file per part,
unconcatenated and unpadded**, plus each part's measured duration, and let the
caller lay them out. Say in the hand-off that the parts are unjoined and that
placement is theirs. This is what `fal-video-production` stage 5 needs; getting a
single welded file back is how a thirty-second ad ended up with its speech pooled
in the first eighteen seconds.

## Step 4 — Verify

Run only the checks for the job that ran; a check belonging to another job is
`n/a`, not a failure.

1. **Every job:** `ffprobe` the delivered file — non-zero, decodes, not silent.
   A mean volume below about −60 dB from `ffmpeg -af volumedetect` is an empty
   render: re-run once, then report.
2. **Voiceover with a Length target: aim short, then pad to exact.**

   **Do not try to hit the target with words.** Measured on three renders at
   identical settings, the same endpoint produced 2.93, 3.19 and 3.04 words per
   second — a ±4% spread, about ±0.8 s on a 20 s read — and `multilingual-v2`
   exposes no `seed`, so that variance is not controllable. Chasing a ±2%
   window inside ±4% noise is a loop that pays repeatedly and lands by luck.

   Instead, budget for **95% of the target** — `WORDS = floor(0.95 × TARGET ×
   RATE)` — accept any take that comes in **at or under** the target, and append
   digital silence to reach it exactly. Silence is free, deterministic, and
   inaudible under a music bed or a hard cut. The result is exactly the target
   length with a read that finishes a beat early, which is what a real voiceover
   session delivers anyway.

   **Only rewrite when the take overruns**, since silence cannot fix long.
   Adjust by `(target − measured) × RATE` words — **target minus measured**, so a
   long take loses words and a short one gains them. Getting that subtraction the
   wrong way round makes every correction move away from the target; an earlier
   draft of this skill had it inverted. Update `rate_wps` with the newly observed
   rate and regenerate. **Two rewrites maximum.**

   Still overrunning after two: deliver the closest take **that does not exceed
   the target**, even if that means an earlier, shorter one, and say how much
   silence was added. An overrun truncates in a fixed slot; short does not. Never
   time-stretch, and never trim the tail mid-word.
3. **Voiceover, any:** if the script holds names, numbers or jargon, transcribe
   the output with `scribe-v2` and confirm those tokens survived. Misread numbers
   are the commonest defect and the easiest to skim past.
4. **Voice swap:** transcribe **both** source and result with `scribe-v2`, filter
   to `type == "word"`, normalise case and punctuation, compare the sequences.
   **They must match — the words are exactly what a voice swap must not change.**
   Below ~98% agreement the model re-spoke rather than converted: re-run once
   with `remove_background_noise: true`, then take the transcribe-and-re-speak
   fallback and say the timing has changed.
5. **Dub:** confirm the returned `target_lang` is what was asked for, transcribe
   the result and confirm the detected language agrees, and confirm the duration
   is within 2% of the source.
6. **Sound effect:** duration within 0.2 s of `duration_seconds`. With
   `loop: true`, confirm the first and last 100 ms match in level so the seam is
   inaudible.
7. **Music:** duration within 5% of `music_length_ms`. On `fal-ai/minimax-music/v2.6`
   this is `n/a` — that route has no length control, so report the duration you
   got rather than implying it was requested.
8. **Transcript:** confirm `words[]` is non-empty and `start` values rise
   monotonically. A route that returned text but no `words[]` when word timings
   were asked for has failed, not partly succeeded — take the fallback.

## Step 5 — Deliver

Hand back the audio, plus `.txt` and `.json` for a Transcript job. State in one
line: endpoint, voice, measured duration against target, language. Update
`audio/voices.json` before finishing.

## Cloning a voice from a supplied sample

Mechanics only. **Whose voice** (above) has already decided whether this
section may run at all — a sample does not open what that gate closed, and the
gate never needed a sample to close it.

| Route | Endpoint | Shape |
|---|---|---|
| Persistent clone | `fal-ai/minimax/voice-clone` → `fal-ai/minimax/speech-2.8-hd` | `audio_url` ≥10 s returns `custom_voice_id`, which goes in `voice_setting.voice_id`. **The ID is deleted if unused for 7 days.** |
| One-shot clone | `resemble-ai/chatterboxhd/text-to-speech` | `audio_url` on the TTS call itself; no stored ID, and it overrides `voice`. |
| Reference clone | `fal-ai/qwen-3-tts/clone-voice/1.7b` | `audio_url` up to 300 s plus `reference_text` of what the sample says, which improves the match. |

`fal-ai/minimax/speech-2.8-hd` defaults `output_format` to **`hex`**, returning
bytes instead of a link — send `output_format: "url"`. It also returns
`duration_ms`, so Step 4's length check needs no `ffprobe` there.

Record consent as `"consent": "owner"` or `"consent": "written permission from
<name>"` — the
two forms **Whose voice** admits, and nothing else. An empty
`consent` on a cloned voice blocks the run.

## Guardrails

- Never leave `voice` unset. The silent `Rachel` default is indistinguishable
  from a decision, and it is not one.
- Never invent a voice ID. If a user-supplied ID 422s, ask for a corrected ID —
  **unless the value named a real person**, in which case the 422 is the
  impersonation limit surfacing late, not a typo: apply **Whose voice**, and
  never answer that 422 by requesting a voice ID or an audio sample of the
  person.
- Never choose or tune a voice for resemblance to a real person — shopping the
  preset list for the closest match, steering `stability`/`style`, or writing
  v3 performance cues toward how someone in particular sounds are all the
  request **Whose voice** refuses, whatever the mechanism.
- Never fit speech by stretching, trimming or re-speeding. Rewrite the words.
- Never imply a duration parameter where none exists — `multilingual-v2`,
  `turbo-v2.5`, `eleven-v3`, `text-to-dialogue` and `fal-ai/minimax-music/v2.6` have no
  length field.
- Never estimate transcript timings from word count or duration. If no route
  returns `words[]`, report that word timings are unavailable.
- Never translate inside a Voiceover job. That is the Dub route, chosen
  explicitly by the user.
- Never resubmit a failed generation more than once before switching route.
- Send `diarize: false` and `tag_audio_events: false` on a transcript headed
  for captions (except `reels-creator`, whose own caption code filters the words). Both
  default to `true`, and the caption burn wants clean words.
- Do not re-encode a delivered file twice; each pass costs quality no later step
  recovers.
