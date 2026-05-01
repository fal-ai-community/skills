# fal.ai Skills

Agent skills for [fal.ai](https://fal.ai). All execution runs through the [genmedia CLI](https://github.com/fal-ai-community/genmedia-cli). These skills are knowledge layers (which endpoint to use, how to prompt it, how to chain calls). They are not API wrappers and ship no `.sh` scripts.

Compatible with [Claude.ai Projects](https://claude.ai), [Claude Code](https://claude.ai/claude-code), and other agent platforms supporting the community skills format.

## Skills

### Foundational

| Skill | Purpose |
|-------|---------|
| **[genmedia](skills/claude.ai/genmedia)** | The CLI surface. `models`, `schema`, `run`, `status`, `upload`, `pricing`, `docs`. Every other skill calls genmedia for execution. |

### Umbrellas, knowledge organized by modality, family, or use case

| Skill | Purpose |
|-------|---------|
| **[fal-models-catalog](skills/claude.ai/fal-models-catalog)** | Curated endpoint picks across 10 modalities (text-to-image, image-to-image, text-to-video, image-to-video, video-to-video, text-to-3d, image-to-3d, text-to-audio, audio-to-text, image-to-text). |
| **[fal-prompting](skills/claude.ai/fal-prompting)** | Family-specific prompt craft (Kling, GPT Image 2, Happy Horse). |
| **[fal-recipes](skills/claude.ai/fal-recipes)** | Use-case pipelines (cinematography, character design, commercial, storytelling, lipsync, restoration, virtual try-on, video with audio, product shot). |

### Verticals, closed pipelines

| Skill | Purpose |
|-------|---------|
| **[fal-workflow](skills/claude.ai/fal-workflow)** | Multi-step pipelines. Mode A authors workflow JSON for the fal.ai cloud runtime; Mode B drives genmedia CLI orchestration. |
| **[fal-redesign](skills/claude.ai/fal-redesign)** | Website redesign with its own Node runtime (puppeteer screenshot, multi-vision pipeline, file orchestration). Powers screenshot → vision-driven build-spec → HTML implementation. |
| **[fal-regenerate-3d](skills/claude.ai/fal-regenerate-3d)** | Interactive 3D character-selector experience (Three.js + Meshy + Seedance). Powers [fal-roster.vercel.app](https://fal-roster.vercel.app). |
| **[fal-gamedev](skills/claude.ai/fal-gamedev)** | 2D pixel-art game assets: characters, sprite sheets, parallax and isometric backgrounds. |

## Setup

### 1. Get an API key

[fal.ai/dashboard/keys](https://fal.ai/dashboard/keys)

### 2. Install genmedia

```bash
curl https://genmedia.sh/install -fsS | bash # macOS / Linux
genmedia setup
```

### 3. Install skills

**Claude.ai:** upload skill `.zip` files to your project from `skills/claude.ai/`.

**Any project with `genmedia` installed:**

```bash
genmedia init
```

Installs the default skill bundle into `.agents/skills/` or `.claude/skills/`.

## Skill format

```
skills/claude.ai/
└── skill-name/
 ├── SKILL.md # YAML frontmatter (name, description) + body
 └── references/ # optional, for umbrellas
 └── *.md
```

## License

MIT
