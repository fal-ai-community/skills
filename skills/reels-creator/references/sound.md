# Sound: voice first, then the bed, then a few effects

**The voice carries the video.** Everything else sits under it and never competes.

**Targets for the finished mix** (`host_reel.py` mixes to them; `mix_check.py` measures them):

| | Target |
|---|---|
| Integrated loudness | −14 LUFS |
| True peak | ≤ −1 dBFS (loudnorm at −1.5) |
| Voice over the bed | 15–25 dB (RMS while speaking vs in the pauses) |

## 1. Music bed

**Score it to the cut, not the other way round.**
1. Run `host_reel.py --plan` first, with the end card already in the edit. The segment starts become the sections: intro, each scene, each host appearance, the close, the end card.
2. Write `music.json` with one section per part, each with a mood that fits its picture.
3. Call `elevenlabs/music/v2.5` with a composition plan of one chunk per section:
   - `{text: "[name]", duration_ms, positive_styles, negative_styles, context_adherence: "high"}`;
   - the first chunk carries the global styles plus its mood;
   - later chunks carry their mood, "flows continuously from the previous section with no pause and no hard stop", and the same instruments, key and tempo;
   - the last chunk is the end card's: its positive styles add "resolves to the home chord" and "ends on a final held chord that rings out", and it bans an abrupt ending and a fade-out; the others ban endings, final chords and fades;
   - `output_format` is `mp3_48000_192`.
   It costs $0.60 a minute: say the cost first (Gate 5).

**Instruments:**
- **Use** warm acoustic or soft electric: felt piano, upright or soft electric bass, brushed kit, strings, pizzicato, soft pads that breathe.
- **Never use** synth leads, hi-hat rolls, risers, whooshes, cymbal swells, or bright ringing tones. They read as shrill and digital, above all on phone speakers.
- Put the bans in `global_neg`.

**Behaviour:**
- The music never cuts to silence mid-scene. It flows across sections: every later chunk says "flows continuously" and repeats the anchor.
- **It ends on a resolution, with the video.** The last section is the end card's: a short cadence to the home chord, then a final held chord that rings out to the end of the video. Only that chunk may end; the ones before it ban endings and fades (step 3 above).
- The bed comes back up by itself once the voice stops, and the card's `"music_db"` lifts it further (−14 over a bed at −20), so the ending is heard. Never fade the music out under the last word: the video then has no close.

**In the edit:** `"music": {"file": "audio/bed.mp3", "from": 0, "db": -20, "duck_db": -25, "fade_in": 0.4, "fade_out": 1.0}`. The bed ducks under the voice by itself. `fade_out` only softens the last second of the ring-out.

## 2. Clip sound

- **FLUX 3 Max clips** come with their own sound (`generate_audio` defaults to true). host_reel keeps it as ambience: `ambience_db` −14 and `duck_db` −24 for 16:9, −12 and −22 for 9:16.
- **Host clips' audio is discarded.** An H3 Max Lip Sync clip carries the take resampled to 32 kHz; the mix uses the take itself (voice-and-host.md §4).
- **H3 Max clips:** their own audio track is seldom what a scene needs. Prefer Mirelo for their sound.
- **A b-roll clip with no or wrong sound:** use Mirelo `video-to-audio`.
  - Set `duration` to the clip's length (the default is 10 s), `num_samples: 1`, a `text_prompt` naming off-screen sounds, and a `negative_prompt` such as "music, whoosh, riser, swell, bright ring".
  - Or use `video-to-video` to get the clip back with its sound mixed in.

## 3. SFX for animation scenes

**Few and soft.** A scene can carry one or two sounds that belong to its objects:
- a soft tick as a chip lands;
- a paper slide as a card docks;
- a low thud as a big number settles.

No sound on every label, and none on the circle reveals.

**Make them:**
- Mirelo `text-to-audio` with `prompt` (not `text_prompt`), a short `duration`, `num_samples: 1` (or 2 when the user wants a choice), and the same negative prompt.
- Or Mirelo `video-to-audio` on the rendered scene MP4, with a `text_prompt` naming the actions. It finds the motion by itself.

**Screen them** by ear and by spectrum (ffmpeg `showspectrumpic` in the local workspace). Reject sweeps (a rising or falling band) and bright, ringing highs.

**Place them** in the edit's `sfx` list, at segment-relative times taken from the scene's own timeline (`wordtimes.py` and the scene's seek times):
```json
"sfx": [{"file": "sfx/chip_tick.wav", "seg": 3, "at": 4.62, "db": -20}, {"file": "sfx/dock.wav", "seg": 5, "at": 13.40, "db": -18, "duck": true}]
```

## 4. Checks

```bash
python3 ./project-work/tools/mix_check.py ./project-work/out/Video.mp4 ./project-work/out/Video_plan.json          # voice vs pauses, LUFS, true peak
python3 ./project-work/tools/review_sheet.py ./project-work/out/Video.mp4 ./project-work/out/Video_plan.json ./project-work/out/Video_sheet.jpg
```

Then listen to the whole video once, from start to end:
- the first word of each host appearance;
- the music under the first scene after a cut;
- every SFX in context;
- the ending: the card plays out and the music resolves on it, with no fade under the last word and no hard stop.

Numbers don't catch a shrill sound; ears do.
