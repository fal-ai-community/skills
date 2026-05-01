# Image-to-Text Endpoints

Curated picks for OCR, captioning/VQA, and detection/segmentation. **Moondream 3** is the dominant pick across all three; **Florence-2** and **SAM-3** complete the toolset. Verify with `genmedia models --endpoint_id <id> --json` before running.

## OCR, extract text from image

- `fal-ai/got-ocr/v2`: GOT OCR 2.0
- `fal-ai/florence-2-large/ocr`: Florence-2 Large (OCR head)
- `fal-ai/moondream3-preview/segment`: Moondream 3 Preview (segment also reads text regions)
- `fal-ai/moondream3-preview/query`: Moondream 3 Preview (query for text content)

## Caption / VQA

Image description and visual question-answering.

- `fal-ai/moondream3-preview/caption`: Moondream 3 · Caption
- `fal-ai/moondream3-preview/query`: Moondream 3 · Query (VQA)
- `fal-ai/florence-2-large/caption`: Florence-2 Large
- `fal-ai/florence-2-large/detailed-caption`: Florence-2 Large · Detailed
- `fal-ai/florence-2-large/more-detailed-caption`: Florence-2 Large · More Detailed
- `fal-ai/video-understanding`: Video Understanding
- `fal-ai/auto-caption`: Auto-Captioner
- `perceptron/isaac-01`: Perceptron · Isaac 0.1
- `perceptron/isaac-01/openai/v1/chat/completions`: Perceptron · Isaac 0.1 (OpenAI-compatible)

## Detection / Segmentation

Nesne tespit ve maskeleme.

- `fal-ai/moondream3-preview/detect`: Moondream 3 · Detect (open-vocabulary detection)
- `fal-ai/moondream3-preview/point`: Moondream 3 · Point
- `fal-ai/moondream2/object-detection`: Moondream 2 · Object Detection
- `fal-ai/moondream2/point-object-detection`: Moondream 2 · Point Object Detection
- `fal-ai/sam-3/image/embed`: SAM 3 · Image Embed (segmentation backbone)
- `fal-ai/florence-2-large/region-to-category`: Florence-2 · Region-to-Category
- `fal-ai/florence-2-large/region-to-description`: Florence-2 · Region-to-Description
- `perceptron/isaac-01`: Perceptron · Isaac 0.1
- `perceptron/isaac-01/openai/v1/chat/completions`: Perceptron · Isaac 0.1 (OpenAI-compatible)

## Common parameters

```bash
genmedia schema fal-ai/moondream3-preview/query --json
genmedia schema fal-ai/got-ocr/v2 --json
genmedia schema fal-ai/sam-3/image/embed --json
```

Frequently exposed:

- `image_url`: source image
- `prompt` / `query` / `question`, for VQA or guided segmentation
- `threshold`: confidence cutoff (detection)
- `output_format`: for masks: `png` alpha, `binary`, `coco-rle`, etc.

## Discovery

```bash
genmedia models --category vision --limit 10 --json
genmedia models "ocr" --json
genmedia models "image segmentation" --json
genmedia docs "vision" --json
```

## See also

- For mask manipulation utilities, see [fal-workflow/references/utility-endpoints.md](../../fal-workflow/references/utility-endpoints.md)
- For document scan cleanup before OCR, see [fal-recipes/references/image-restoration.md](../../fal-recipes/references/image-restoration.md)
