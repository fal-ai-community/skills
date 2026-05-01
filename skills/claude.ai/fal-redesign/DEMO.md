# fal-redesign, launch-day demo cheat-sheet

Copy-paste blocks in order. Designed for a 60–90s screen recording.

## 0. Setup (off-camera)

```bash
export FAL_KEY=... # https://fal.ai/dashboard/keys

# Demo subject, a deliberately plain starter HTML:
cd ~/mon-projet-web # contains index.html (PixelFind)
open index.html # show the "before" in the browser

# Open a second terminal for the skill commands
cd ~/mon-projet-web
```

## 1. Single redesign (the core money shot)

```bash
node ~/.claude/skills/fal-redesign/runtime/bin/fal-site.mjs upgrade \
 --target ./index.html \
 --context "PixelFind, a royalty-free image search and in-browser editor"
```

Artifacts land in `./.fal-site-upgrade/`:
- `before.png` current screenshot
- `after.png` redesign
- `changes.md` build-spec (Hard constraints section first)
- `tokens.json` design tokens
- `edit-prompt.txt`

Open `after.png` at the 20–35s mark of the video for the reveal.

```bash
open ./.fal-site-upgrade/after.png
cat ./.fal-site-upgrade/changes.md | head -40
```

## 2. Hand off to Claude Code for implementation

In a separate Claude Code session:

> Réimplémente `./index.html` en suivant strictement `.fal-site-upgrade/changes.md`. La section "Hard constraints" est non-négociable. Utilise les valeurs exactes de `.fal-site-upgrade/tokens.json`. Regarde `.fal-site-upgrade/after.png` directement pour l'imagerie du grid.

Refresh the browser. Split-screen the old vs. new. That's the delivery.

## 3. Residual pixel-fix pass (optional)

```bash
node ~/.claude/skills/fal-redesign/runtime/bin/fal-site.mjs iterate \
 --target ./index.html \
 --reference ./.fal-site-upgrade/after.png
```

Produces `current.png` + `delta.md`. Hand `delta.md` back to Claude Code; refresh.

## 4. Multi-direction teaser (outro shot)

```bash
node ~/.claude/skills/fal-redesign/runtime/bin/fal-site.mjs upgrade \
 --target ./index.html \
 --context "PixelFind, a royalty-free image search and in-browser editor" \
 --variants 4 \
 --out ./.fal-redesign-variants
```

Then open the gallery:

```bash
open ./.fal-redesign-variants/gallery.html
```

4 redesigns side-by-side in 4 distinct directions. Use this as the closing shot of the video: "one command, four futures, pick one."

## 5. Greenfield (bonus for a future video)

```bash
node ~/.claude/skills/fal-redesign/runtime/bin/fal-site.mjs generate \
 --context "a volunteer-run bouldering gym inside a deconsecrated 19th-century church in Lyon, key-fob 24/7, weekly route-voting assemblies, Sunday brioche breakfast in the old sacristy" \
 --variants 3 \
 --out ./.fal-redesign-greenfield
```

Produces N standalone single-file HTML pages in different directions.

---

## Timing per step (approximate)

| Step | Typical duration |
| ------------------- | ---------------- |
| `upgrade` single | 60–150s |
| `upgrade` 4-variant | 90–180s (parallel)|
| `describe` | 20–40s |
| `iterate` | 40–70s |
| `generate` 3-var | 180–300s |

## One-liner you can pin to your Raycast / Alfred

```bash
node ~/.claude/skills/fal-redesign/runtime/bin/fal-site.mjs upgrade --target ./index.html --context "<brand>"
```
