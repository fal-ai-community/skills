# fal.ai Skills

Agent skills for [fal.ai](https://fal.ai). Most skills are knowledge layers:
which endpoint to use, how to prompt it, and how to chain calls through the
[genmedia CLI](https://github.com/fal-ai-community/genmedia-cli). Skills with
additional setup document that in their own folder.

Compatible with [Claude.ai Projects](https://claude.ai), [Claude Code](https://claude.ai/claude-code), and other agent platforms supporting the community skills format.

## Skills

### Foundational

| Skill | Purpose |
|-------|---------|
| **[genmedia](skills/genmedia)** | The CLI surface. `models`, `schema`, `run`, `status`, `upload`, `pricing`, `docs`. Every other skill calls genmedia for execution. |

### Umbrellas, knowledge organized by modality, family, or use case

| Skill | Purpose |
|-------|---------|
| **[fal-models-catalog](skills/fal-models-catalog)** | Curated endpoint picks across 10 modalities (text-to-image, image-to-image, text-to-video, image-to-video, video-to-video, text-to-3d, image-to-3d, text-to-audio, audio-to-text, image-to-text). |
| **[fal-prompting](skills/fal-prompting)** | Family-specific prompt craft (Kling, GPT Image 2, Happy Horse). |
| **[fal-recipes](skills/fal-recipes)** | Use-case pipelines (cinematography, character design, commercial, storytelling, lipsync, restoration, virtual try-on, video with audio, product shot). |
| **[model-routing](skills/model-routing)** | Endpoint-first model defaults for production skills. |

### Production skills

| Skill | Purpose |
|-------|---------|
| **[commercial](skills/commercial)** | Product photography, ads, e-commerce batches, product reveal videos, and brand-safe product prompts. |
| **[marketing](skills/marketing)** | Campaign matrices, launch kits, paid social variants, landing-page visuals, banners, and channel-specific marketing assets. |
| **[ugc](skills/ugc)** | Creator ads, talking-head clips, testimonials, demos, unboxing, reaction, faceless voiceover, and short vertical social videos. |
| **[character-design](skills/character-design)** | Original characters, identity anchors, reference consistency, and character-driven media. |
| **[cinematography](skills/cinematography)** | Cinematic stills and video direction: shot language, lighting, lens, color, and camera movement. |
| **[storytelling](skills/storytelling)** | Multi-shot narratives, storyboards, brand films, social stories, and sequence continuity. |

### Verticals, closed pipelines

| Skill | Purpose |
|-------|---------|
| **[fal-workflow](skills/fal-workflow)** | Multi-step pipelines. Mode A authors fal.ai workflow JSON; Mode B drives genmedia CLI orchestration. |
| **[fal-redesign](skills/fal-redesign)** | Website redesign: screenshot review, vision-driven reference image, build spec, and implementation guidance. |
| **[fal-regenerate-3d](skills/fal-regenerate-3d)** | Interactive 3D character-selector experience (Three.js + Meshy + Seedance). Powers [fal-roster.vercel.app](https://fal-roster.vercel.app). |
| **[fal-gamedev](skills/fal-gamedev)** | 2D pixel-art game assets: characters, sprite sheets, parallax and isometric backgrounds. |

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

```
skills/
└── skill-name/
 ├── SKILL.md # YAML frontmatter (name, description) + body
 └── references/ # optional, for umbrellas
 └── *.md
```

## License

MIT
