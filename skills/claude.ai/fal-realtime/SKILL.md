---
name: fal-realtime
description: Real-time and streaming AI image generation — instant results for interactive use. Use when the user requests "Real-time generation", "Fast generation", "Streaming image", "Instant image", "Live generation", "Realtime".
metadata:
  author: fal-ai
  version: "1.0.0"
---

# fal-realtime

Real-time and streaming image generation using fal.ai's fastest models. Results in under 1 second — ideal for interactive applications, live previews, and rapid iteration.

## Scripts

| Script | Purpose |
|--------|---------|
| `realtime.sh` | Generate images in real-time (sub-second) |

## Usage

### Quick Real-Time Generation
```bash
./scripts/realtime.sh --prompt "A cute cat wearing a top hat"
```

### With LoRA
```bash
./scripts/realtime.sh --prompt "A portrait in sks style" --lora-url "https://example.com/lora.safetensors"
```

### Multiple Rapid Iterations
```bash
./scripts/realtime.sh --prompt "Abstract art with flowing colors, version 1"
./scripts/realtime.sh --prompt "Abstract art with flowing colors, version 2, more vibrant"
./scripts/realtime.sh --prompt "Abstract art with flowing colors, version 3, darker tones"
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--prompt` / `-p` | Image description | Yes |
| `--model` / `-m` | Model endpoint | No (default: fal-ai/flux-2/klein/realtime) |
| `--size` | square, landscape, portrait | No (default: square) |
| `--seed` | Random seed for reproducibility | No |
| `--lora-url` | URL to LoRA weights | No |
| `--lora-scale` | LoRA influence (0.0-1.0, default: 1.0) | No |
| `--num-images` | Number of images (default: 1) | No |

## Finding Models

To discover the best and latest real-time generation models, use the search API:

```bash
# Search for real-time / fast image generation models
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "realtime"
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "fast image"
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --category "text-to-image"
```

Or use the `search_models` MCP tool with keywords like "realtime", "fast", "schnell", "turbo".

## When to Use Real-Time vs Standard Generation

| Use Case | Use Real-Time | Use Standard |
|----------|--------------|--------------|
| Rapid prototyping / iteration | Yes | |
| Interactive apps / live preview | Yes | |
| Final high-quality output | | Yes (FLUX Dev, Nano Banana Pro) |
| Professional / commercial work | | Yes (FLUX Pro Ultra) |
| Exploring prompt ideas quickly | Yes | |
| Batch generation with variations | Yes | |

## Output Format
```json
{
  "images": [
    {
      "url": "https://fal.media/files/...",
      "content_type": "image/jpeg",
      "width": 1024,
      "height": 1024
    }
  ],
  "seed": 12345,
  "has_nsfw_concepts": [false]
}
```

## Tips

- Real-time models use fewer inference steps — prompts should be clear and concise
- Use `--seed` to lock in a good composition, then iterate on the prompt
- LoRA support works with FLUX Klein Realtime — great for style-locked fast iteration
- These models use the synchronous API (no queue), so results are instant
