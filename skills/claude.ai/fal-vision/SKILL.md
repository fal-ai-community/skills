---
name: fal-vision
description: Analyze images using AI — segment objects, detect objects, extract text (OCR), describe images, ask questions about images. Use when the user requests "Segment image", "Detect objects", "OCR", "Extract text from image", "Describe image", "What's in this image", "Image analysis".
metadata:
  author: fal-ai
  version: "1.0.0"
---

# fal-vision

Analyze and understand images using fal.ai vision models — segmentation, detection, OCR, captioning, and visual QA.

## Scripts

| Script | Purpose |
|--------|---------|
| `analyze.sh` | Analyze an image (segment, detect, OCR, describe, QA) |

## Usage

### Segment Objects
```bash
./scripts/analyze.sh --image-url "https://example.com/photo.jpg" --operation segment --query "the red car"
```

### Detect Objects
```bash
./scripts/analyze.sh --image-url "https://example.com/photo.jpg" --operation detect
```

### Extract Text (OCR)
```bash
./scripts/analyze.sh --image-url "https://example.com/document.jpg" --operation ocr
```

### Describe Image
```bash
./scripts/analyze.sh --image-url "https://example.com/photo.jpg" --operation describe
```

### Visual QA
```bash
./scripts/analyze.sh --image-url "https://example.com/photo.jpg" --operation qa --query "How many people are in this image?"
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--image-url` | URL of image to analyze | Yes |
| `--operation` | segment, detect, ocr, describe, qa | Yes |
| `--query` / `-q` | Text prompt for segment/qa operations | For segment/qa |
| `--model` / `-m` | Override model endpoint | No |

## Finding Models

To discover the best and latest vision/analysis models, use the search API:

```bash
# Search for segmentation models
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "segmentation"

# Search for object detection models
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "object detection"

# Search for OCR models
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "ocr"

# Search for image captioning / visual QA models
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "caption"
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "visual question"
```

Or use the `search_models` MCP tool with keywords like "segmentation", "detection", "ocr", "caption", "vision".
