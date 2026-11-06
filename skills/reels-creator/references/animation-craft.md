# Animation craft in the local workspace

Scenes are seek(t) HTML pages: plain JS, with GSAP when it helps. `render.mjs` opens a page in Playwright, seeks every frame and pipes the screenshots into ffmpeg, so the MP4 holds exactly what the page draws at each t. Render scenes this way rather than through another compositing tool: host_reel.py and the word timings expect these MP4s. This page adds what makes every frame exact and every word land on its spoken time.

## 1. One page per scene

**Files.** Start from `references/code/scene.html`. Write it to `./project-work/scenes/<scene>/index.html`, next to `textkit.js` and a `fonts/` folder.
- Fonts: OFL faces downloaded by URL (Geist, Inter, Space Grotesk…), or the user's licensed files with their OK.
- The page sets `W`, `H` (the frame) and `LOOP` (the scene length from `wordtimes.py`), exposes `window.seek`, `W`, `H` and `LOOP`, and sets `window.__ready = true` last.

**The scene is `seek(t)`**, a function of t alone. Build and measure everything once; seek(t) only sets values. Nothing may depend on what was drawn before (`check.mjs --order` catches it).

**GSAP** is welcome for curves and choreography: build one paused timeline once and call `tl.seek(t, true)` inside seek(t). Values are set on every seek and callbacks are suppressed, so never draw in `onUpdate` or `call()`, and never let a tween run on the clock.

**Real footage inside a scene:** decode the clip to frames (`ffmpeg -i clip.mp4 -vf fps=24 frames/f%03d.jpg`) and show it with `textkit.seq()`, whose `at(t, t0)` resolves only once that frame is decoded. Make seek async and await it; `render.mjs` and `check.mjs` await every seek. A `<video>` seeked through `currentTime` also works when seek awaits its `seeked` event.

**Times come from the voice.** `python3 ./project-work/tools/wordtimes.py ./project-work/vo/<take> [a] [b]` prints each word's time in the scene and the scene length. Its rule is the one `host_reel.py` uses: the first word at 0.16 s, length = span + 0.44 s. Put labels on their words, and start a move 0.1–0.2 s before its word.

## 2. textkit.js in one screen

```js
const T = TextKit({ W: 1080, H: 1920, stroke: 3, radius: 8, tracking: -0.02 });   // every value is a per-video choice
const F = { head: T.font(500, 88, "Face"), chip: T.font(400, 40, "Face") };
await T.K.assertFonts(Object.values(F));
```

| Piece | What it guarantees |
|---|---|
| `text`, `word`, `line` | DOM-measured baseline; widths without tracking's trailing space |
| `reveal`, `rline` | each word rises whole out of its own mask on its time: paused frames show whole glyphs |
| `chip`, `tab` | a box that hugs its label, with the caps centred `(h + cap) / 2`; cut on/off with `.at(t, t0)` |
| `frame` | a stroke box that draws on from its top-left corner |
| `media`, `seq` | a picture, or a clip's frames, in a rounded window |
| `timer` | tabular stopwatch, right edge fixed, one value per 60 fps frame |
| `mark` | an official SVG mark from its path data |
| `bar`, `field`, `layer`, `circle` | fills and strokes, grounds, groups that move together, circle-reveal clip paths |
| `house`, `prog`, `rise` | the arrival curve (house bezier 0.085, 0.648, 0, 1), progress, a rise offset |

textkit needs no other library. Every string and every chip is registered for the checks.

## 3. Lessons: symptom → fix

| Symptom | Cause | Fix |
|---|---|---|
| Counter shows two values blended | value evaluated between frames | `timer()` quantises to the frame |
| The same moment differs with what came before | state kept between seeks (a `+=`, a leftover src, a tween on the clock) | derive everything from t; `check.mjs --order` must report nothing |
| A label sits high or low in its pill | centred on the line box, not the caps | `chip()`; `check.py` measures the ink (baseline ±1.5 px, caps dy ±2, dx ±2) |
| A character renders in another font | the face lacks the glyph (≈, ±, U+202F and the thin space are common gaps) | `check.py`'s glyph check; rewrite ("about", a plain space, "-") |
| Half the frame stays empty for seconds | the second object arrives late | centre the first object alone, then slide it aside when the second arrives |
| Two consecutive animation scenes jump | two unrelated grounds | the incoming scene starts on the previous scene's last ground and opens its own as a circle (0.45 s, `T.circle()`); the hard cut is then invisible |
| A 5 s clip must fill a 9 s window | — | never slow it, restart it, freeze it or dissolve it into itself; dock it into a card, morph it, or cut to another clip |
| The voice's caption lands on a UI scene | a phrase's tail spills past its segment | `"captions": false` on the scene's segment |
| Motion feels cheap | linear or symmetric ease-in-out | front-loaded arrivals (house curve, or GSAP `expo.out`, 0.55–0.85 s), chips cut on, springs for settling; never linear |
| A render hits the command limit | a long scene, or PNG frames | one scene per command; JPEG frames (the default); split a long scene in two pages |

## 4. Set up once per local workspace

```
pip install fonttools brotli
mkdir -p ./project-work/scenes && cd ./project-work/scenes && npm i playwright && npx playwright install chromium
```

Check for a working Chromium installation first. Use Playwright's public installer if needed and authorized. Set `CHROME` only to a browser installed in this environment.

## 5. Check before showing anything

1. **Per scene:**
   ```
   cd ./project-work/scenes/<scene> && node ./project-work/tools/check.mjs --order index.html:4.4,6.2,9.0 | python3 ./project-work/tools/check.py --faces faces.json
   ```
   - The viewport comes from the page's `W`/`H`. `faces.json` maps `{"Family|100-900": "fonts/Face.woff2"}`; `--css fonts.css` works when the faces are in a stylesheet.
   - The run must end in `ALL OK`.
   - Choose the times at the key moments: each new chip, the "everything visible" moment, and the last frame. The stills land in `out/`: send them to the user as images.
2. **Look at the stills yourself:**
   - Is the text inside its box?
   - Is anything overlapping?
   - Is the dated source line there?

## 6. Render

- **Command:** `cd ./project-work/scenes/<scene> && node ./project-work/tools/render.mjs index.html ./project-work/scenes/<scene>.mp4 --fps 24`. The size comes from the page's `W`/`H` and the length from `LOOP` (or `--dur`). One scene per command; a 5 s 1080×1920 scene renders in about 12 s.
- **Frame rate:** 24, the edit's fps (assembly.md §1). A 30 fps scene in a 24 fps edit loses every 5th frame, and a 60 fps one loses frames in a 2:3 pattern.
- **Verify:** `ffprobe` the duration against `LOOP`, and make a frame grid with `python3 ./project-work/tools/sheet.py <scene>.mp4 <scene>_sheet.jpg --fps=2`.
