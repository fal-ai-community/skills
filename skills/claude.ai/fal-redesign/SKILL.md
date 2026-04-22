---
name: fal-redesign
description: Upgrade a coded website to award-tier, editorially-crafted design using fal.ai. Takes a local HTML file or a dev-server URL, screenshots it, has an opus-4.7 vision model write a gpt-image-2 edit prompt, uses fal-ai/gpt-image-2/edit to produce the redesigned reference image, then opus-4.7 vision writes a Markdown build-spec with a "Hard constraints" section + a tokens.json. Also supports iterate (screenshot implemented site → delta-spec vs reference) and greenfield generate (brief → mockup → single-file HTML). Invoke when the user says "improve the design", "make it world-class", "redesign this landing page", "upgrade this site", "design pass", or points at a local HTML / dev server for a visual review.
metadata:
  author: fal-ai-community
  version: "0.1.0"
---

# fal-redesign

`fal-redesign` turns "I coded a site — make it look amazing" into a concrete, implementable design pass.

```
your index.html          →  screenshot (1920×1200)
screenshot + brand       →  opus-4.7 writes a redesign prompt
screenshot + prompt      →  fal-ai/gpt-image-2/edit → after.png
after.png                →  opus-4.7 writes Markdown build-spec + tokens.json
                         →  returned to Claude Code / Codex
```

The agent reads `after.png` + `changes.md` + `tokens.json`, applies the spec to the real HTML, refreshes, optionally runs `iterate` for a residual pixel-fix pass.

## When to invoke

- User has a local `index.html` or a running dev server and asks to improve the design, make it world-class, redesign, polish, or run a design review.
- User describes a brand/product in freeform text and asks for a fresh site (greenfield mode → `generate`).

Do NOT invoke for:
- Copy-only edits (the skill is visual-design focused).
- Backend, build config, or infra tasks.

## Scripts

### `scripts/upgrade.sh` — redesign a coded site
```bash
bash scripts/upgrade.sh --target <path-or-url> [--context "..."] [--variants N] [--out <dir>]
```

Pass `--variants N` (2–8) to fan out into N distinct design directions in parallel. You get `after-01-<slug>.png`, `after-02-<slug>.png`, … plus a `gallery.html` to compare them side-by-side. Pick one, then run `scripts/describe.sh` on the chosen PNG to produce its build-spec.
Outputs in `<out>/`:
- `before.png` — current-site screenshot.
- `after.png` — redesigned reference image.
- `edit-prompt.txt` — transformation prompt fed to gpt-image-2.
- `changes.md` — Markdown build-spec with a leading "Hard constraints" section (also echoed to stdout).
- `tokens.json` — design tokens (colors, typography clamps, grid, buttons).

### `scripts/describe.sh` — re-run the build-spec on an existing `after.png`
Useful if the first spec was noisy or if you want to iterate on the spec without regenerating the image.
```bash
bash scripts/describe.sh --after <path/to/after.png> [--out <dir>]
```

### `scripts/iterate.sh` — residual pixel-fix pass
After the agent has implemented the spec, screenshot the live site and emit a delta-spec vs the reference.
```bash
bash scripts/iterate.sh --target <path-or-url> --reference <path/to/after.png> [--out <dir>]
```
Outputs `current.png` + `delta.md`.

### `scripts/generate.sh` — greenfield (brief → site)
```bash
bash scripts/generate.sh --context "<freeform context>" [--variants 4] [--out <dir>]
```

## Required environment

```bash
export FAL_KEY=...   # https://fal.ai/dashboard/keys
```

Models used:
- `anthropic/claude-opus-4.7` — via `openrouter/router` and `openrouter/router/vision` (overridable with `FAL_SITE_MODEL`).
- `fal-ai/gpt-image-2` — greenfield hero + mockup renders.
- `fal-ai/gpt-image-2/edit` — screenshot-to-redesign transformation.

## Usage pattern for agents

1. **Check `FAL_KEY`.** If unset, ask the user to export it and stop.
2. **Pick the mode.**
   - If the user references a file path that exists or a URL (`http://localhost:...`) → `scripts/upgrade.sh`.
   - Otherwise → `scripts/generate.sh`.
3. **Run the script.** Each `upgrade` pass takes 60–180s (1 screenshot + 2 vision calls + 1 image-edit). Emit a brief status to the user before calling.
4. **Surface the result.**
   - Open `after.png` (Read tool) so the user sees the new design.
   - Paste `changes.md` in the chat (or the highlights).
   - Ask: "Want me to implement these changes in `<file>` now?"
5. **If yes, implement.** Read the current file. Apply the spec section by section, obeying the `Hard constraints` verbatim and pulling exact values from `tokens.json`. For imagery in the result grid, look at `after.png` directly and either use `<img>` placeholders at the matching aspect ratio or source stock that matches the mood.
6. **Optional iterate.** After implementation, offer `scripts/iterate.sh --target <file> --reference <after.png>` for a residual delta-spec. Apply deltas, refresh.

## Model notes

- Opus 4.7 handles multi-image reasoning and produces precise design specs. For 3× cheaper runs with near-parity on this task, set `FAL_SITE_MODEL=anthropic/claude-sonnet-4.6`.
- `gpt-image-2/edit` is the right primitive because it edits an existing screenshot while preserving legible in-image text — avoid substituting other image models here.

## Runtime

The skill ships a small Node 18+ runtime under `runtime/` (`puppeteer`, `@fal-ai/client`, `sharp`). Scripts `npm install` on first run. Override the runtime path with `FAL_SITE_RUNTIME=/abs/path`.
