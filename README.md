# fal.ai Skills

Agent skills for [fal.ai](https://fal.ai). The default execution path is the
[genmedia CLI](https://github.com/fal-ai-community/genmedia-cli): discover an
endpoint, inspect its schema, run it, poll status when needed, and download
outputs. Most skills in this repo are knowledge layers that tell an agent which
endpoint to use, how to prompt it, and how to chain calls.

Compatible with [Claude.ai Projects](https://claude.ai), [Claude Code](https://claude.ai/claude-code), and other agent platforms supporting the community skills format.

## Current system

- Skills live directly under `skills/<name>/`.
- Each skill has a required `SKILL.md` with `name` and `description`
  frontmatter.
- Larger skills may add `references/` files for prompt patterns, endpoint
  notes, examples, or workflows.
- `skills/index.json` is the generated registry for the current skill folders.
- User-facing model execution should go through `genmedia` unless a skill
  explicitly documents another workflow in its own folder.

## Skills

### Core

| Skill | Purpose |
|-------|---------|
| **[genmedia](skills/genmedia)** | The CLI surface. `models`, `schema`, `run`, `status`, `upload`, `pricing`, `docs`. Every other skill calls genmedia for execution. |
| **[model-routing](skills/model-routing)** | Endpoint-first model defaults for production skills. |

### Umbrellas, knowledge organized by modality, family, or use case

| Skill | Purpose |
|-------|---------|
| **[fal-models-catalog](skills/fal-models-catalog)** | Curated endpoint picks across 10 modalities (text-to-image, image-to-image, text-to-video, image-to-video, video-to-video, text-to-3d, image-to-3d, text-to-audio, audio-to-text, image-to-text). |
| **[fal-prompting](skills/fal-prompting)** | Family-specific prompt craft (Kling, GPT Image 2, Happy Horse). |
| **[fal-recipes](skills/fal-recipes)** | Use-case pipelines (cinematography, character design, commercial, storytelling, lipsync, restoration, virtual try-on, video with audio, product shot). |

### Production skills

| Skill | Purpose |
|-------|---------|
| **[character-design](skills/character-design)** | Original characters, identity anchors, reference consistency, and character-driven media. |
| **[cinematography](skills/cinematography)** | Cinematic stills and video direction: shot language, lighting, lens, color, and camera movement. |
| **[commercial](skills/commercial)** | Product photography, ads, e-commerce batches, product reveal videos, and brand-safe product prompts. |
| **[marketing](skills/marketing)** | Campaign matrices, launch kits, paid social variants, landing-page visuals, banners, and channel-specific marketing assets. |
| **[storytelling](skills/storytelling)** | Multi-shot narratives, storyboards, brand films, social stories, and sequence continuity. |
| **[ugc](skills/ugc)** | Creator ads, talking-head clips, testimonials, demos, unboxing, reaction, faceless voiceover, and short vertical social videos. |

### Workflow and vertical skills

| Skill | Purpose |
|-------|---------|
| **[fal-workflow](skills/fal-workflow)** | Multi-step pipelines. Mode A authors fal.ai workflow JSON; Mode B drives genmedia CLI orchestration. |
| **[fan-cam](skills/fan-cam)** | Personalized live sports broadcast fan-cam videos from a user photo with GPT Image 2 and Kling v3. |
| **[fal-gamedev](skills/fal-gamedev)** | 2D pixel-art game assets: characters, sprite sheets, parallax and isometric backgrounds. |
| **[fal-redesign](skills/fal-redesign)** | Website redesign: screenshot review, vision-driven reference image, build spec, and implementation guidance. |
| **[fal-regenerate-3d](skills/fal-regenerate-3d)** | Interactive 3D character-selector experience with Three.js, Meshy, and Seedance. |
| **[genmedia-workflow](skills/genmedia-workflow)** | Genmedia-oriented workflow planning, node rules, pipeline patterns, and reusable recipes. |

## Install

Use the [one-command installation guide](docs/install.md) for Codex, Claude Code
and Cursor. It also documents hybrid MCP packages for Codex, Cursor and supported
Grok hosts: the fal router, five outcome workflows and live guidance on demand.
The complete 36-skill library remains available for project installation and full
package builds. Claude MCP packages retain a full bundle by default.

Install the published Gemini CLI extension:

```sh
gemini extensions install https://github.com/fal-ai-community/fal-gemini-extension
```

The [v0.1.0 release](https://github.com/fal-ai-community/skills/releases/tag/v0.1.0)
provides complete Claude, CLI, Gemini and OpenClaw archives with checksums.
The [Grok/Cursor v0.2.0 release](https://github.com/fal-ai-community/fal-grok-plugin/releases/tag/v0.2.0)
provides the compact plugin; marketplace synchronization or review remains pending.

The official Registry entry, [`io.github.fal-ai-community/mcp`](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.fal-ai-community%2Fmcp/versions/latest),
is active at version `0.1.0`. Gemini gallery indexing remains pending.
The [Cline submission](https://github.com/cline/mcp-marketplace/issues/3593)
awaits marketplace review. ClawHub publication awaits publisher sign-in and
ownership confirmation; no ClawHub package is published yet.

See the [distribution guide](docs/distribution.md) for installation, publication
status and local bundle builds. The [Cline guide](docs/cline.md) covers its remote
connection. Builders only export files; publication uses separate manual steps.

## Complete creative outcomes

| Skill | Deliverable |
| --- | --- |
| [product-ad-campaign](skills/product-ad-campaign) | Hero art, channel variants, motion ads and campaign manifest |
| [game-asset-production](skills/game-asset-production) | Transparent frames, atlas, animation preview and engine import metadata |
| [storyboard-to-short-film](skills/storyboard-to-short-film) | Rendered film, clean cut, shot table and audio stems |
| [ecommerce-product-photography](skills/ecommerce-product-photography) | Consistent hero, detail and lifestyle images by SKU |
| [localize-and-repurpose](skills/localize-and-repurpose) | Localized speech, timed captions and channel cuts |

Each includes a stage plan for the shared resumable runner in `genmedia/scripts/`.
Production guidance imported from the fal agent lives with its version-pinned
references. See the [source and compatibility inventory](docs/consolidation.md).
The [generated registry](skills/index.json) is the full skill list.

## Development checks

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/build-skills-index.py --check
.venv/bin/python -m unittest discover -s tests -v
```

Validation CI checks metadata, hashes, packaging, isolated installation, candidate
schema fixtures and submission recovery. It publishes no release and runs no paid
jobs. Registry publication uses a separate manual workflow.

## Skill format

```text
skills/
└── skill-name/
 ├── SKILL.md # YAML frontmatter (name, description) + body
 └── references/ # optional, for umbrellas
 └── *.md
```

## License

MIT
