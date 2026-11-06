# Design: free, never slop

Every video gets its own look. This page doesn't hand you a palette, a font or a motion style. It lists what reads as cheap, what makes a scene "cool", and a method that finds a look the user will pick.

## 1. Freedom

- **Derive the look from the subject and the audience**, not from the last video. A science explainer, a cooking reel and a news recap should not share a palette or a font.
- **Mixing looks in one video is welcome when the reason is clear:** for example, light pastel scenes with stroke boxes for structure, and black cinematic scenes with real footage for proof.
- **Brands use their own system:** their real fonts, colours and marks, verified on the brand's own site (licensed faces only with files the user supplies). Never draw a logo by hand: use its official paths (`textkit.mark()`).
- **Any technique in §5 is available; none is required.** Don't tie a video to a single animation style or design.

## 2. The text budget

The words on screen are the voice's shadow, not a second script. Too much text is the first thing that makes a scene look cheap.

- **One idea per scene.** The headline, if there is one, is a single line of at most six words.
- **Labels name things** (≤ 3 words each) and appear on the word that says them (word times from `wordtimes.py`). A label the voice never says is a candidate to cut.
- **No sentences on screen**, except a quoted claim with its source.
- **Visible words at any moment:**
  - 16:9: aim for ≤ 12, hard ceiling 20;
  - 9:16: aim for ≤ 8, ceiling 12;
  - captions and the one-line source footnote don't count.
- **Numbers may be big.** A number the voice says can fill a third of the frame. That is often the best scene.
- **Every number gets a dated source line** (`who.int · Oct 2026`), small, in one corner, set once per scene.
- **Text over a host clip never touches the face or the hair.** On a 9:16 talking head, the plain area below the captions (often the shirt) is the clean ground.

## 3. Tells: the AI-slop look

Never ship:
- coloured accent bars on a card's left or top edge (border-left / border-top), or "callout" boxes;
- a grid of white or grey cards with hairline borders on a grey ground, the dashboard look. A card is fine when it is a real object (a widget, a phone, a ticket, a window on footage), not a container for bullet text;
- uppercase, letter-spaced mono "eyebrow" labels over headings;
- bento grids that exist to fill space, and three-icon feature rows;
- gradient blobs, decorative glows, and glass with no light source;
- text that fades and rises in, line after line, as the scene's only motion;
- emoji or stock icons with mismatched strokes;
- rolling odometer strips on every number (half digits show in paused frames);
- floating corner badges, "NEW" stickers, pulsing dots;
- template transitions: zoom blur, glitch, page curl, cube spin, a swipe wipe between every scene;
- drop shadows on everything, and three different corner radii in one frame;
- a centred title over three cards (a slide, not a scene);
- labels off-centre in their boxes (the bar is ±2 px, measured by `check.py`);
- flat clip-art drawings in two saturated colours, and full-bleed split colour blocks.

## 4. Cooler = the object explains

A scene is cool when the thing itself moves to make the point, so the voice needs no help. Ask of every scene: **what is the one thing that moves, and what does its movement say?**

Moves that work:
- **Footage that proves the number.** A score on a chart flies into a window that opens on the footage it scored: this score *is* this video. The footage then docks into a card while the next fact arrives, so the result keeps its place.
- **A duration you watch.** A stopwatch counts while a clip plays: a speed claim becomes a length of time, not a number you read.
- **The layout is the argument.** A box spans only the columns it covers, so its width says what it does.
- **No half-empty frame.** A box holds the middle alone, then slides aside when its partner draws on.
- **Handovers.** Consecutive animation scenes hand over by a circle reveal of the next ground from the point of interest. After a host shot or b-roll, the scene just cuts in.
  - The reveal lives inside the incoming scene: its first frame shows the previous scene's last ground, and its own ground opens as a circle.
  - host_reel only hard-cuts, and the cut is invisible because the two frames match.

More directions that fit this rule:
- a bar that *is* the thing it counts (stacked clips, coins, GPUs);
- a map region lighting up as it's named;
- a timeline that becomes the next scene's ground;
- a price that physically shrinks next to the one it beats;
- a UI the viewer knows (a terminal, a phone, a player) doing the real thing.

## 5. Techniques catalogue (techniques, not a style)

Borrow freely and adapt to the look:
- **Studio motion techniques:** squircle morphs, colour reveals, flip faces, word-pop line launches, slanted band masks, velocity-matched zoom cuts, card tilt-and-rise, radial gauges, counters with centred bars, rack focus, and a physical object for one moment.
- **The measured house curve:** arrivals leave at full speed and land softly (cubic-bezier 0.085, 0.648, 0, 1, 0.55–0.85 s); exits into a cut accelerate to the last frame.
- **Premium rhythm:** one loud thing on a quiet ground, one idea per shot, a pace that breathes.
- **Words that perform their meaning** ("cut" cuts, "slide" slides), used once, not on every word.
- **Real footage inside the design:** frame sequences in rounded windows (`textkit.seq`), docked cards, masks that follow an object.
- **Generated plates:** an H3 Max abstract plate or a FLUX 3 Max real-world shot as a scene's ground, with the design drawn on top.

## 6. Method

1. **Scene list first.** Per scene: its line, its one idea, its one moving object, its ground. This is cheap, so show it with the script.
2. **Directions.** Make 2–3 directions as stills on the same two scenes, picking the hardest ones, on one sheet with short labels (A, B, C, one line each).
   - The directions differ in look, not just colour.
   - Never re-propose a rejected direction.
3. **The user picks or mixes.** Then make a short motion test of the same two scenes with the real voice (`preview_mux.py`) before building the rest.
4. **Build every scene.** Send stills of each scene's key moments (`check.mjs`) before the full render.
5. **After any rejection, stills come first again.** Never go straight to a full render.

## 7. Type

- **Faces:** brand fonts first. Otherwise one display face with character and one text face, plus one mono only when it carries data.
  - Check licences: OFL faces (Geist, Inter, Space Grotesk…) are safe to load in the local workspace; licensed brand faces only with the user's files and OK.
  - Load fonts with `@font-face` in the page's `fonts.css`, verify them with `assertFonts`, and check glyph coverage with `check.py`.
- **Sizes:** judge them on the final frame, at phone size.
  - At 1920 × 1080: body ≥ 34 px, labels ≥ 24 px, the source line ≥ 20 px.
  - At 1080 × 1920: body ≥ 44 px, labels ≥ 30 px.
- **Figures:** tabular for anything that counts. Use the real minus, real quotes and real apostrophes when the face has them; `check.py` tells you when it doesn't.
- **Brand names keep their own case:** avoid label styles that force uppercase.
