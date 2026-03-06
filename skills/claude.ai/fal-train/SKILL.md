---
name: fal-train
description: Train custom AI models (LoRA) on fal.ai — personalize image generation for specific people, styles, objects, or video generation. Use when the user requests "Train model", "Train LoRA", "Fine-tune", "Custom model", "Train on my images", "Portrait training".
metadata:
  author: fal-ai
  version: "1.0.0"
---

# fal-train

Train custom LoRA models on fal.ai for personalized AI generation.

## Scripts

| Script | Purpose |
|--------|---------|
| `train.sh` | Submit a LoRA training job |

## Usage

### Train Image LoRA (Style/Subject/Person)
```bash
./scripts/train.sh --images-url "https://example.com/training-images.zip" --trigger-word "sks style" --model fal-ai/flux-lora-fast-training
```

### Train Portrait LoRA
```bash
./scripts/train.sh --images-url "https://example.com/face-photos.zip" --trigger-word "ohwx person" --model fal-ai/flux-lora-portrait-trainer
```

### Check Training Status
```bash
./scripts/train.sh --status --endpoint fal-ai/flux-lora-fast-training --request-id "abc123"
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--images-url` | URL to zip of training images | Yes |
| `--trigger-word` | Word to activate the LoRA in prompts | Yes |
| `--model` / `-m` | Training model endpoint | No (default: fal-ai/flux-lora-fast-training) |
| `--steps` | Training steps | No (default: 1000) |
| `--status` | Check training job status | No |
| `--endpoint` | Endpoint for status check | With --status |
| `--request-id` | Request ID for status check | With --status |
| `--param` | Extra param as key=value (repeatable) | No |

## Finding Models

To discover the best and latest training/LoRA models, use the search API:

```bash
# Search for LoRA training models
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "lora training"
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "trainer"
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "fine-tune"
```

Or use the `search_models` MCP tool with keywords like "lora", "training", "trainer", "fine-tune".

## Training Data Tips

- **People**: 10-20 photos, varied angles/lighting/expressions, consistent person
- **Styles**: 10-15 images exemplifying the style, diverse subjects
- **Objects**: 5-15 photos from different angles on various backgrounds
- Images should be high quality, at least 512x512
- Zip all images into a single .zip file and host at a URL

## Output Format
```json
{
  "diffusers_lora_file": {
    "url": "https://fal.media/files/.../lora.safetensors",
    "content_type": "application/octet-stream",
    "file_name": "lora.safetensors",
    "file_size": 12345678
  },
  "config_file": {
    "url": "https://fal.media/files/.../config.json"
  }
}
```

Use the `diffusers_lora_file.url` as the `lora_url` parameter when generating images with FLUX models.
