---
name: fal-restore
description: Restore and fix image quality — deblur, denoise, dehaze, fix faces, restore documents. Use when the user requests "Fix blurry image", "Remove noise", "Fix face", "Restore photo", "Enhance document", "Deblur", "Denoise".
metadata:
  author: fal-ai
  version: "1.0.0"
---

# fal-restore

Restore and enhance image quality using AI — fix blur, noise, haze, faces, and documents.

## Scripts

| Script | Purpose |
|--------|---------|
| `restore.sh` | Restore an image (deblur, denoise, dehaze, fix-face, document) |

## Usage

### Deblur
```bash
./scripts/restore.sh --image-url "https://example.com/blurry.jpg" --operation deblur
```

### Denoise
```bash
./scripts/restore.sh --image-url "https://example.com/noisy.jpg" --operation denoise
```

### Fix Face
```bash
./scripts/restore.sh --image-url "https://example.com/bad-face.jpg" --operation fix-face
```

### Restore Document
```bash
./scripts/restore.sh --image-url "https://example.com/scan.jpg" --operation document
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--image-url` | URL of image to restore | Yes |
| `--operation` | deblur, denoise, dehaze, fix-face, document | Yes |
| `--model` / `-m` | Override model endpoint | No |
| `--fidelity` | For fix-face: 0.0-1.0 (0=max quality, 1=most faithful) | No |

## Finding Models

To discover the best and latest image restoration models, use the search API:

```bash
# Search for restoration models
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "restore"
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "deblur"
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "denoise"
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "face restoration"
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "document"
```

Or use the `search_models` MCP tool with keywords like "restore", "deblur", "denoise", "face fix", "document".
