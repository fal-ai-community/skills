# fal redesign

**Turn any coded website into award-tier editorial design, in one command.**

`fal-redesign` is a Claude Code / Codex skill that takes a site you've already coded (or a freeform brief) and ships back a real redesign: a reference image plus a precise Markdown build-spec your agent can implement.

No more "make it look nicer" feedback loops. The model *shows* you the new design, then *tells* your agent how to build it.

---

## What it actually does

```
your index.html → screenshot (1920×1200)
screenshot + brand → opus-4.7 writes a redesign prompt
screenshot + prompt → fal-ai/gpt-image-2/edit → after.png
after.png → opus-4.7 writes Markdown build-spec + tokens.json
 → returned to Claude Code / Codex
```

Your agent reads `changes.md` + `tokens.json`, you review `after.png`, the agent edits your HTML. Next cycle, same skill, the redesign keeps getting sharper.

---

## Why it works

Most "AI design" tools ask a language model to *write* beautiful CSS. LLMs are bad at that, they default to Inter, rounded corners, blue CTAs, infinite boilerplate.

`fal-redesign` flips the job:

- **Image model does the design.** `gpt-image-2/edit` is trained on real design and renders legible in-image typography. Given a screenshot + an art-director prompt, it produces a mockup that looks like it came out of Figma, not a prompt.
- **Vision LLM does the spec.** `opus-4.7` reads the new mockup and writes a concrete change-list, palette hexes, font stacks, tracking, grid shifts, component details, plus a `Hard constraints` section the implementer must follow verbatim.
- **Your agent does the code.** Claude Code / Codex then applies the spec to your real HTML, because that's what coding agents are good at.

Each model plays to its strength. The result is a redesign your engineer-agent can actually *execute*, not a vibes-based critique.

---

## Install

Copy this folder into your skills directory, or reference it via a Claude Code plugin / symlink:

```bash
ln -s /path/to/skills/claude.ai/fal-redesign ~/.claude/skills/fal-redesign
export FAL_KEY=... # https://fal.ai/dashboard/keys
```

First run: the skill auto-installs its Node runtime (`puppeteer`, `@fal-ai/client`, `sharp`). ~1 minute, once.

---

## Use

Ask Claude Code / Codex anything that sounds like a design request and point at a file or URL:

> "upgrade the design of `./index.html`, it's a landing page for a fishing-guide startup"

> "make `http://localhost:3000` look world-class"

> "design pass on `public/index.html`"

The agent invokes the skill, runs the pipeline (60–180s), and surfaces:

- `after.png`: the new approved design (opened in chat).
- `changes.md`: the Markdown build-spec with a leading `Hard constraints` section.
- `tokens.json`: design tokens for exact values.
- An offer to apply the spec to your HTML.

You say "yes" and your HTML updates. Optionally run `iterate` for a residual pixel-fix pass.

---

## Modes

### `upgrade`, you already coded something
```bash
bash scripts/upgrade.sh --target ./index.html --context "your brand in one line"
```
Outputs: `before.png`, `after.png`, `edit-prompt.txt`, `changes.md`, `tokens.json`.

### `describe`, re-run the spec on an existing `after.png`
Useful when the first spec was noisy or you want to iterate on the spec without regenerating the image.
```bash
bash scripts/describe.sh --after .fal-site-upgrade/after.png
```

### `iterate`, residual pixel-fix pass after implementation
```bash
bash scripts/iterate.sh --target ./index.html --reference .fal-site-upgrade/after.png
```
Outputs `current.png` + `delta.md` (only the remaining fixes).

### `generate`, greenfield
```bash
bash scripts/generate.sh --context "a volunteer bouldering gym in a Lyon church" --variants 4
```
Outputs N standalone single-file HTML variations (Tailwind CDN + inline base64 hero), each in a different design direction.

---

## Models

| Stage | Model | Why |
| --- | --- | --- |
| Brief extraction | `anthropic/claude-opus-4.7` via `openrouter/router` | Structures freeform context into a tight JSON brief. |
| Redesign prompt | `anthropic/claude-opus-4.7` via `openrouter/router/vision` | Strong multi-image reasoning; writes art-director prompts gpt-image-2 understands. |
| Redesign image | `fal-ai/gpt-image-2/edit` | Edits a screenshot while preserving readable brand copy in-image. |
| Build-spec | `anthropic/claude-opus-4.7` via `openrouter/router/vision` | Produces precise, actionable Markdown specs + tokens. |

Override the vision model with `FAL_SITE_MODEL=<provider>/<model>`. Use `anthropic/claude-sonnet-4.6` for ~3× cheaper runs with near-parity for this task.

---

## Roadmap

- `upgrade --variants N`: render N directions in parallel, pick a favorite before the build-spec.
- Swap `puppeteer` for a hosted screenshot API so the skill can ship pure bash + curl.
- Fold into the official `fal` CLI as `fal design upgrade <path>` once it ships.
- Optional `--implement` flag to let the skill write the HTML changes directly (bypassing the agent), for headless pipelines.
- Auto-iterate: loop `upgrade → implement → iterate` until the residual delta is below a threshold.

---

## License

MIT.
