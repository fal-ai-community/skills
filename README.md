# fal.ai Skills

Agent skills for [fal.ai](https://fal.ai) — ready-to-use bash scripts that let AI agents generate images, videos, audio, 3D models, and more.

Compatible with [Claude.ai Projects](https://claude.ai), [Claude Code](https://claude.ai/claude-code), and any agent platform that supports the community skills format.

## Skills

### Core

| Skill | Description | Scripts |
|-------|-------------|---------|
| **[fal-generate](skills/claude.ai/fal-generate)** | Generate images and videos with queue support | `generate.sh`, `upload.sh`, `search-models.sh`, `get-schema.sh` |
| **[fal-image-edit](skills/claude.ai/fal-image-edit)** | Edit images — style transfer, object removal, background change, inpainting | `edit-image.sh` |
| **[fal-audio](skills/claude.ai/fal-audio)** | Text-to-speech and speech-to-text | `text-to-speech.sh`, `speech-to-text.sh` |
| **[fal-upscale](skills/claude.ai/fal-upscale)** | Upscale and enhance image resolution | `upscale.sh` |

### Specialized Models

| Skill | Description | Scripts |
|-------|-------------|---------|
| **[fal-kling-o3](skills/claude.ai/fal-kling-o3)** | Kling O3 — highest quality photorealistic images and video editing | `kling-generate.sh`, `kling-video.sh` |
| **[fal-realtime](skills/claude.ai/fal-realtime)** | Real-time/streaming generation (~0.3s per image) | `realtime.sh` |

### Video & Animation

| Skill | Description | Scripts |
|-------|-------------|---------|
| **[fal-video-edit](skills/claude.ai/fal-video-edit)** | Edit videos — remix, upscale, remove background, add audio | `edit-video.sh`, `video-audio.sh` |
| **[fal-lip-sync](skills/claude.ai/fal-lip-sync)** | Talking head, lip sync, live portrait | `talking-head.sh`, `lip-sync.sh` |

### Creative & Production

| Skill | Description | Scripts |
|-------|-------------|---------|
| **[fal-3d](skills/claude.ai/fal-3d)** | Text/image to 3D model generation | `generate-3d.sh` |
| **[fal-vision](skills/claude.ai/fal-vision)** | Image analysis — segment, detect, OCR, describe | `analyze.sh` |
| **[fal-restore](skills/claude.ai/fal-restore)** | Restore image quality — deblur, denoise, fix faces | `restore.sh` |
| **[fal-tryon](skills/claude.ai/fal-tryon)** | Virtual clothing try-on | `tryon.sh` |
| **[fal-train](skills/claude.ai/fal-train)** | Train custom LoRA models | `train.sh` |

### Platform & Utilities

| Skill | Description | Scripts |
|-------|-------------|---------|
| **[fal-platform](skills/claude.ai/fal-platform)** | Pricing, usage tracking, cost estimation, API key setup | `pricing.sh`, `usage.sh`, `estimate-cost.sh`, `setup.sh`, `requests.sh` |
| **[fal-workflow](skills/claude.ai/fal-workflow)** | Create multi-step model pipelines | `create-workflow.sh` |

## Setup

### 1. Get your API key

Sign up at [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys).

### 2. Set the key

```bash
export FAL_KEY=your_key_here
```

Or use the built-in setup:

```bash
bash scripts/generate.sh --add-fal-key
```

### 3. Use with Claude.ai

Upload skills to a Claude.ai Project:
1. Go to your project settings
2. Add skills from the `claude.ai/` directory
3. Make sure `*.fal.ai` is in your allowed domains under `claude.ai/settings/capabilities`

### 4. Use with any agent

Every skill is a standalone bash script. Call them directly:

```bash
# Generate an image
bash skills/claude.ai/fal-generate/scripts/generate.sh \
  --prompt "A serene mountain landscape" \
  --model "fal-ai/nano-banana-pro"

# Generate a video
bash skills/claude.ai/fal-generate/scripts/generate.sh \
  --prompt "Ocean waves crashing on rocks" \
  --model "fal-ai/veo3.1" \
  --async

# Edit an image
bash skills/claude.ai/fal-image-edit/scripts/edit-image.sh \
  --image-url "https://example.com/photo.jpg" \
  --prompt "Convert to anime style" \
  --operation style

# Text to speech
bash skills/claude.ai/fal-audio/scripts/text-to-speech.sh \
  --text "Hello world"

# Search for models
bash skills/claude.ai/fal-generate/scripts/search-models.sh \
  --query "text to video"
```

## Skill Format

Each skill follows the community skills standard:

```
claude.ai/
└── skill-name/
    ├── SKILL.md          # Metadata + documentation (YAML frontmatter)
    └── scripts/
        └── script.sh     # Executable bash script
```

The `SKILL.md` contains a YAML frontmatter with `name`, `description`, and `metadata`, followed by usage documentation that the agent reads to understand how to use the skill.

## License

MIT
