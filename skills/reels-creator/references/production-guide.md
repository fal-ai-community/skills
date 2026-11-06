# Reels creator

A finished video with a presenter on camera:
- their face and voice open it and close it, and come back in between only when the story needs a face;
- animations drawn in code explain the ideas, each word landing as it is spoken;
- generated footage shows the real world;
- an end card closes it while the music resolves;
- one mix holds it together.

The presenter is the person the user names, who must have agreed to appear. The voice is the ElevenLabs voice id the user gives for the video: ask for it when the brief has none, and never pick one yourself.

Reply in the user's language, briefly, results first. Show stills, sheets and clips, not scores.

## Local runtime

- **Models:** use genmedia or the connected public fal MCP tools. Verify current
  schemas, account access and prices; stay within the user's authorized budget.
  If a price is unavailable, report that uncertainty instead of using a hidden
  price assumption or treating the job as free.
- **Dependencies:** check Python, Pillow, numpy, ffmpeg, Node and a supported
  Chromium/Playwright installation. Follow the public package documentation for
  missing dependencies. Save intermediate files in a persistent project folder.
- **Helper code** is in this skill's `references/code/`. Copy the required files into the local project tools folder before use:
  - `host_lipsync.py`: the H3 Max Lip Sync inputs (`prep`) and each clip's `take_at` (`measure`);
  - `host_reel.py`: host clips played 1:1 with the take back on, captions, mix, MP4;
  - `host_check.py`: the finished video's host segments, picture against the clip and voice against the lips;
  - `wordtimes.py`;
  - `scene.html` (a seek(t) page; GSAP optional), `textkit.js` and `render.mjs` (page → MP4 through Playwright and ffmpeg): scenes;
  - `check.mjs` + `check.py`: stills, glyphs, centring;
  - `preview_mux.py`, `review_sheet.py`, `mix_check.py`, `sheet.py`.
- **Animation scenes** are seek(t) HTML pages in plain JS, with GSAP when it helps, rendered frame by frame by `render.mjs`. This skill decides the look (design.md) and the exactness (animation-craft.md).
- **The final video** is assembled by `host_reel.py`, because it puts the real voice on the presenter's lips and draws word-timed captions.
- **Project:** keep the script, sources and decisions in local project files.

## Router ()

| You need | Read |
|---|---|
| What the animations should look like | design.md, **always, before the first frame** |
| Building, checking and rendering scenes in the local workspace | animation-craft.md |
| A model, its inputs, its price | models.md (re-read prices on the day) |
| Script, voice takes, pronunciation, the presenter on camera, non-English videos | voice-and-host.md |
| Music, SFX, the mix | sound.md |
| Local workspace layout, the edit file, the final render, delivery | assembly.md |
| Something looks or sounds wrong | pitfalls.md |

## Non-negotiables

**Money and permission**
- **Cost before every paid step.** Generate nothing paid until the user asked for that work, and show each paid step's cost before running it. The gates below say when.
- **Presenter lines:** show them before rendering the presenter's mouth saying them. The language is fixed before the first host clip.
- **Picks:** the user picks takes, looks and directions. Show options, briefly.
- **Publishing:** post nothing anywhere unless the user asks for that exact post.

**Content**
- **Facts:** every claim at its source's strength (web search, dated), and every number on screen with a dated source line. Current models only.
- **Scripts:** plain declaratives built on facts. No teaser openers, negation runs or fragment triads (voice-and-host.md §1).
- **People:** no public figures. Another person's face, or a voice cloned from a real person, needs that person's consent.
- **Generated footage:** no logos and no text.

**Shape**
- **Host time:** the presenter opens and closes the video. In between, the face comes back only when the story needs one. Host clips take about 15 % of the runtime or less (voice-and-host.md §1).
- **The ending:** after the last line comes a 3–4 s end card in the video's own look, while the music resolves on a final chord. A video never ends on its last spoken word.

**The presenter's face**
- **Never retimed.** Host clips play 1:1 at their own frame rate: no speed-up, slow-down, frame skip, frame blend or warp to fit the voice. The lips follow the take because the clip was made from it (voice-and-host.md §4).
- **Ask first** before any change that alters how the presenter looks or sounds: a new route, a new default, a fallback.

**Craft**
- **The look is free and the slop is not.** No palette, font or motion style is prescribed: each video finds its own (design.md). What's fixed:
  - little text;
  - no border-left or border-top accent bars;
  - no grey card grids;
  - no uppercase tracked labels;
  - no fade-and-rise as the only motion;
  - no template transitions.
- **The object explains:** every scene has one thing whose movement makes the point.
- **Frame rate:** a 24 fps master, with the animation scenes rendered at 24 fps. H3 Max, Seedance and FLUX clips are 24 fps, and a 30 fps cut repeats every 5th frame of them.
- **One shot is one unbroken take:** no slow-motion stretch, restart, freeze or self-dissolve to fill time.
- **Exact text:**
  - glyphs covered;
  - labels centred within ±2 px (`check.py` must end in ALL OK);
  - counters show one value per frame.
- **The mix:** −14 LUFS, true peak ≤ −1 dBFS, voice 15–25 dB over the bed. No whooshes, risers or shrill sounds.

## Models (recommended; exact endpoint ids, inputs and prices in models.md)

| Job | Model | Notes |
|---|---|---|
| Voice | ElevenLabs v4 TTS | the voice id given for this video, stability 0.5, similarity 0.95, 3 seeds per line |
| Presenter on camera | H3 Max Lip Sync (image to video) | the presenter still + the picked take padded to ≥ 5 s (`host_lipsync.py prep`); `resolution: "1080P"`, `enable_transcription: true`; ≈ $0.16/s; the clip is as long as the audio, 24 fps, and plays 1:1 (voice-and-host.md §4) |
| Presenter still, once per set | Seedance 2.5 US reference-to-video | frame 0 of a short clip from the presenter's photos (≈ $1.16/s at 1080p); the user confirms the likeness first (voice-and-host.md §3) |
| Real-life b-roll | FLUX 3 Max (text, image or keyframes to video) | `resolution: "1080p"` (the default is 720p); its own sound becomes the ambience |
| Everything else | H3 Max (text or image to video) | `prompt_expansion_mode: "disabled"` (required); `resolution: "1080P"` (the default is 768P) |
| SFX | Mirelo SFX 2.0 (video-to-audio, text-to-audio, video-to-video) | `num_samples: 1`; video-to-audio makes 10 s unless `duration` is set; text-to-audio takes `prompt` |
| Word times | ElevenLabs Scribe v2 | every take; save the JSON in the local workspace |
| Music | ElevenLabs Music v2.5 | a composition plan, one section per part of the edit |
| Start frames | Nano Banana Pro | i2v starts |

These are where to start, not a cage. Pick another model when a shot needs it, and say why.

## Workflow (every gate waits for the user)

0. **Setup.**
   - Create a persistent local folder with a source manifest and notes.
   - The presenter, who must have agreed: their character in Assets if there is one; otherwise ask for three photos: front, a second front, three-quarter.
   - The voice: the ElevenLabs voice id the user gives for this video. Ask for it when the brief has none; never fall back to a voice on your own.
1. **Brief.** Ask only for what's missing: topic, audience, format (9:16 or 16:9), length, language, the presenter and the voice id.
2. **Research.** Web search, a dated source for every claim, and models and prices checked on the day.
3. **Script, scene list and a whole-video cost estimate.**
   - Host hook, voice-over sections, host close, end card. A host line in the middle only where the story needs a face (voice-and-host.md §1).
   - Per line: what the screen shows, and its one moving object. The end card's short line is on the list too.
   - `tts` holds the spoken spelling; `text` holds the screen form.
   - Save approved lines as a local JSON file so later steps can read them.
   - **Gate 1:** the user approves the lines. That yes also covers the voice takes, which are cheap; say their cost. Then write the approved lines and the scene plan to `./project-work/script.json`, save it as an output, and read it from there in later turns.
4. **Voice.**
   - Make the takes (3 seeds). Run Scribe on each and save its JSON next to the take in `./project-work/vo/`.
   - Send them. **Gate 2:** the user picks.
5. **Look.** 2–3 directions as stills (`check.mjs`) on the same two scenes (design.md §6).
   - **Gate 3:** the user picks or mixes.
   - Then a short motion test of those two scenes with their takes (`preview_mux.py`).
6. **Host clips.** The presenter still first (once per set; show it, and the user confirms the likeness), then one H3 Max Lip Sync clip per host line from that still and the line's picked take (`host_lipsync.py prep`, voice-and-host.md §3–4). They go into the footage plan of step 7; afterwards `host_lipsync.py measure` gives each clip's `take_at` for the edit.
7. **Footage.** One plan covering the host clips and the b-roll, with costs. **Gate 4:** go.
8. **Scenes.**
   - `wordtimes.py` gives each scene's word times and length.
   - The end card is one more scene, 3–4 s long, with no words to time.
   - Build one seek(t) page per scene from `scene.html`, with textkit for type and chips and GSAP where it helps.
   - Take stills with `check.mjs`, run `check.py`, and look at them. Render each scene with `render.mjs --fps 24`, one scene per command.
9. **Sound.**
   - Run `host_reel.py --plan` with the end card in the edit, and take the music's sections from it: the last section resolves over the card (sound.md §1).
   - List each scene's few SFX: an object that lands, docks or settles gets its sound. They are part of the video; never skip them to save time.
   - Price them. **Gate 5:** go. Then put the bed and the SFX into the edit.
10. **Render once.** Keep the inputs in the local project and run `host_reel.py` at the edit frame rate. Split large renders into scene segments if the local execution limit requires it. Then run `host_check.py` (every host segment 1:1 with its clip, the voice within ±20 ms of the lips), `review_sheet.py` and `mix_check.py`, and watch it, through the end card.
11. **Deliver.** Give:
    - the inspected MP4 through the client's normal file interface;
    - the sheet;
    - what's real and what's generated;
    - the sources;
    - the money spent;
    - the deviations from the plan.

    Save the decisions to the local project notes.
