# Assembly in the local workspace

`host_reel.py` (in `references/code/`) turns an edit JSON into the finished MP4. It:
- plans the timeline;
- plays the host clips 1:1 and puts the real take back on where their lips say it;
- places the scenes and b-roll on their words, and the end card after the last line;
- draws word-by-word captions;
- ducks the clips' sound, the music and the SFX under the voice;
- mixes to −14 LUFS and encodes H.264/AAC with BT.709 tags, at 16:9 or 9:16 and 24 fps.

## 0. Local workspace layout

```
./project-work/tools    the helper code from references/code/
./project-work/vo       takes (.mp3) + their .scribe.json
./project-work/refs     photos, presenter stills
./project-work/clips    host clips (+ the lip-sync wav and frame each was made from), b-roll clips
./project-work/scenes   scene compositions and their rendered MP4s
./project-work/audio    the music bed      ./project-work/sfx  sound effects      ./project-work/fonts  the caption font
./project-work/out      the final video, its plan, its sheet
```

**Getting files in.** Download every input by its generation URL (`curl -L` or `requests`).

**Persistent files.** Keep the input/output manifest and intermediate files in the local project folder. Back up only to a user-authorized destination.

**The caption font.** Use a TTF/OTF of an OFL face (for example Geist or Inter, downloaded by URL). A `.woff2` works only when the local workspace's FreeType reads it.

## 1. The edit

```json
{"fps": 24, "w": 1920, "h": 1080, "x264_preset": "veryfast",
 "font": "fonts/Geist-SemiBold.ttf", "caption_size": 54, "caption_y": 945,
 "caption_pill": [242, 242, 244], "caption_active_text": [10, 10, 11], "caption_words": 5, "caption_chars": 30,
 "ambience_db": -14, "duck_db": -24,
 "music": {"file": "audio/bed.mp3", "from": 0, "db": -20, "duck_db": -25, "fade_in": 0.4, "fade_out": 1.0},
 "sfx": [{"file": "sfx/tick.wav", "seg": 3, "at": 4.62, "db": -20}],
 "lines": {"H1": {"take": "vo/H1_s202.mp3", "scribe": "vo/H1_s202.scribe.json", "text": "…"}, …},
 "segments": [
  {"kind": "host", "line": "H1", "clip": "clips/H1.mp4", "take_at": 0.24, "lead": 0.12, "tail": 0.25, "push": 0.03},
  {"kind": "broll", "clip": "scenes/map.mp4", "in": 0.0, "line": "V1", "words": [0, 50], "captions": false},
  {"kind": "broll", "clip": "clips/B_studio.mp4", "in": 0.0, "line": "V2", "words": [0, 10]},
  {"kind": "host", "line": "H4", "clip": "clips/H4.mp4", "take_at": 0.21, "lead": 0.12, "tail": 0.5, "push": 0.03},
  {"kind": "card", "clip": "scenes/end.mp4", "dur": 3.5, "music_db": -14}]}
```

Paths are relative to `./project-work`; run `host_reel.py` from there.

**Frame rate: `"fps": 24`.** H3 Max (host clips and b-roll), Seedance and FLUX all deliver 24 fps, so a 24 fps master plays every clip frame-exact. A 30 fps master repeats every 5th frame of them, and that reads as stutter, most of all on a face. Render the animation scenes at 24 fps too (animation-craft.md §4).

**Segment kinds:**
- **Host segment:** an H3 Max Lip Sync clip and its `take_at` (voice-and-host.md §4–5). The clip plays 1:1, the voice is the take put back on at `take_at`, and the clip's own sound is never mixed.
- **B-roll segment:** speaks words [a, b) of its line, its first word 0.16 s after the cut. It lasts span + 0.44 s, or `min`.
  - One line can run across several clips.
  - `in` picks a moment with motion.
- **Animation scene:** a b-roll segment whose clip is the rendered scene, with `"captions": false`.
  - Render it at exactly its `wordtimes.py` length; a shorter MP4 holds its last frame, and that is a freeze.
- **Card segment** (`"kind": "card"`): no line, no voice, no captions, and the clip's own sound is left out; the music carries it. It plays its clip from `in` (default 0) for `dur` seconds; `music_db` lifts the bed to that level over its first 0.5 s (−14 over a bed at −20). The end card is one (voice-and-host.md §1): a rendered scene at exactly `dur`, never a still image, which would be a freeze.

**Captions:**
- **Set every caption key** to the video's look. Unset keys fall back to an amber pill.
- **Other languages:** `caption_func_words` lists the words a phrase must not end on. A video in another language passes that language's own function words (its words for and, with, a, this…).
- **Glyphs:** check that the font has every letter the captions use.

**Host keys.** `take_at` comes from `host_lipsync.py measure`; `lead`/`tail` are the seconds kept before the take's first sound and after its last; `push` is a slow, sub-pixel zoom. Leave `sync` at its default, `"clip"`: the clip plays 1:1 and nothing is retimed (voice-and-host.md §5).

## 2. Run

```
cd ./project-work && python3 tools/host_reel.py edit.json out/Video --plan     # timeline, voice pieces, cut check, total length
cd ./project-work && python3 tools/host_reel.py edit.json out/Video            # → out/Video.mp4, out/Video_plan.json
```

**Read the plan first:**
- the cut check: no `CUT` line (voice-and-host.md §5);
- each segment's length against its scene's rendered length;
- the total, with the end card as the last segment.

**The command limit (600 s).** A command stopped at 600 s loses the whole render, so plan for it before the first run:
- `"x264_preset": "veryfast"` makes the encode several times faster than the default `slow`. A 35 s 9:16 edit renders well inside the limit with it.
- A video over 60 s: split the edit up front at segment boundaries, into parts of about 45 s (an estimate: time the first part and adjust). Each later part's music takes `"from"` = the total of the parts before it, so the bed continues. Only the last part keeps `fade_out` (and the end card); earlier parts set `"fade_out": 0` and later parts `"fade_in": 0`, so the bed runs through the joins (the plan prints a `MUSIC` line when a part breaks this). Join the parts with `python3 tools/host_reel.py --join out/Video out/Video_p1 out/Video_p2 …`: it copies the pictures, joins the parts' raw mixes (`<part>_mix_raw.wav`) sample-exact, and normalises and encodes the sound once. Never concat the parts' AAC tracks: each part's encoder priming adds up, and the voice lands 21–50 ms off the lips after a few joins. Check the joined video with `host_check.py` and the whole edit's plan (`--plan` on the unsplit edit). Anything that moves timing (a new host_reel.py, a retake) changes the parts' lengths: re-run `--plan` on every part and recompute each `"from"`.
- Stay at 24 fps: it is already the lightest rate that keeps the footage frame-exact, and 30 fps would repeat frames of every 24 fps clip.

## 3. Check

- `python3 tools/host_check.py out/Video.mp4 out/Video_plan.json`: each host segment's picture against its clip (r ≈ 0.99 and no frame off: nothing repeated, skipped or retimed) and its voice against the clip's own sound (within ±20 ms). Fix every `CHECK` line before anyone sees the video. A video rendered in parts is checked whole, with the full plan.
- `python3 tools/review_sheet.py out/Video.mp4 out/Video_plan.json out/Video_sheet.jpg`: two frames per segment and the loudness. Look at the order, the cuts and the captions; there must be none on UI scenes.
- `python3 tools/mix_check.py out/Video.mp4 out/Video_plan.json`: voice against bed, LUFS and true peak.
- Watch and listen to every host segment: lips against voice, identity, and every word of the take heard whole (no clipped first sound, no gap inside a phrase). Watch every cut into and out of a scene (no freeze, no caption tail).
- Watch the ending: the card plays out while the music resolves, and nothing stops on the last word.
- After any retake, check that the edit points at the new file (compare its sha256 with the new generation), and look at that shot on the sheet: a regenerated clip that never reached the edit is an easy miss.

## 4. Deliver

- **The files:** the final MP4 and the sheet land in the chat as generations.
- **Say, briefly:**
  - what is in the video, one line per part;
  - what is real and what is generated (models and dates), and the sources of the claims;
  - the cost spent;
  - every deviation from the approved plan.
- **Record:** save the decisions, the picks and the user's feedback to the project memory. The next video starts there.
- **Posting:** post or share nothing unless the user asks for that exact post.
