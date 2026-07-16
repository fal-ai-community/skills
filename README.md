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

## Setup

### 1. Get an API key

[fal.ai/dashboard/keys](https://fal.ai/dashboard/keys)

### 2. Install genmedia

Install genmedia from [fal-ai-community/genmedia-cli](https://github.com/fal-ai-community/genmedia-cli), then run `genmedia setup`.

### 3. Install skills

**Claude.ai:** upload skill `.zip` files to your project from `skills/`.

**Any project with `genmedia` installed:**

```text
genmedia init
```

Installs the default skill bundle into `.agents/skills/` or `.claude/skills/`.

## Skill format

```text
skills/
└── skill-name/
 ├── SKILL.md # YAML frontmatter (name, description) + body
 └── references/ # optional, for umbrellas
 └── *.md
```

## Built on genmedia

Third-party skills that use the genmedia CLI as their execution layer:

| Skill | Purpose |
|-------|---------|
| **[HyperShots](https://github.com/hypersocialinc/hypershots)** | App Store screenshots: agent-authored HTML rendered at exact store dimensions with a spec validator; genmedia powers its sticker art (GPT Image 2 + BiRefNet cutouts) and spec-preserving style passes. |

## License

MIT
