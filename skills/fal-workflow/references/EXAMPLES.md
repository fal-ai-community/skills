# Real-World Workflow Examples

Complete workflow examples for reference.

## Multi-Destination Marketing Campaign Workflow

This workflow creates personalized video content for multiple locations:

1. Takes multiple destinations as input
2. Uses Vision LLM to analyze template and generate edit prompts
3. Creates destination-specific images
4. Removes backgrounds
5. Upscales all images
6. Generates videos with 360° camera tours
7. Merges all videos into final output

### Key Pattern: Edit → Remove Text → Upscale → Video

```json
// Step 1: Vision LLM analyzes template, generates edit prompt
"vision-prompt-dest2": {
  "id": "vision-prompt-dest2",
  "type": "run",
  "depends": ["input"],
  "app": "openrouter/router/vision",
  "input": {
    "image_urls": ["https://example.com/template.jpg"],
    "prompt": "$input.destination_2",
    "system_prompt": "Generate prompt to change background to destination, keep layout...",
    "model": "google/gemini-3-pro-preview",
    "reasoning": true
  }
},

// Step 2: Edit image with new destination
"edit-dest2": {
  "id": "edit-dest2",
  "type": "run",
  "depends": ["vision-prompt-dest2"],
  "app": "fal-ai/nano-banana-pro/edit",
  "input": {
    "image_urls": ["https://example.com/template.jpg"],
    "prompt": "$vision-prompt-dest2.output",
    "aspect_ratio": "16:9"
  }
},

// Step 3: Create text-free version for video background
"edit-notext-dest2": {
  "id": "edit-notext-dest2",
  "type": "run",
  "depends": ["edit-dest2"],
  "app": "fal-ai/nano-banana-pro/edit",
  "input": {
    "image_urls": ["$edit-dest2.images.0.url"],
    "prompt": "Remove all text and logo, leave only background scene"
  }
},

// Step 4: Upscale both versions
"upscale-dest2": {
  "id": "upscale-dest2",
  "type": "run",
  "depends": ["edit-dest2"],
  "app": "fal-ai/seedvr/upscale/image",
  "input": {
    "image_url": "$edit-dest2.images.0.url"
  }
},

// Step 5: Vision LLM creates video prompt from both images
"video-prompt-dest2": {
  "id": "video-prompt-dest2",
  "type": "run",
  "depends": ["upscale-notext-dest2", "upscale-dest2", "input"],
  "app": "openrouter/router/vision",
  "input": {
    "image_urls": [
      "$upscale-notext-dest2.image.url",
      "$upscale-dest2.image.url"
    ],
    "prompt": "$input.destination_2",
    "system_prompt": "Create video prompt: camera tours 360° then transitions to tail image..."
  }
},

// Step 6: Generate video with first/last frame
"video-dest2": {
  "id": "video-dest2",
  "type": "run",
  "depends": ["video-prompt-dest2", "upscale-notext-dest2", "upscale-dest2"],
  "app": "fal-ai/kling-video/o1/image-to-video",
  "input": {
    "prompt": "$video-prompt-dest2.output",
    "image_url": "$upscale-notext-dest2.image.url",
    "tail_image_url": "$upscale-dest2.image.url"
  }
},

// Step 7: Merge all destination videos
"merge-all-videos": {
  "id": "merge-all-videos",
  "type": "run",
  "depends": ["video-dest1", "video-dest2", "video-dest3"],
  "app": "fal-ai/ffmpeg-api/merge-videos",
  "input": {
    "video_urls": [
      "$video-dest1.video.url",
      "$video-dest2.video.url",
      "$video-dest3.video.url"
    ]
  }
}
```

### Input Schema for This Workflow

```json
"schema": {
  "input": {
    "destination_1": {
      "name": "destination_1",
      "label": "Destination 1",
      "type": "string",
      "description": "First destination name (e.g., Paris, Tokyo)",
      "required": true,
      "modelId": "vision-prompt-dest1"
    },
    "destination_2": {
      "name": "destination_2",
      "label": "Destination 2",
      "type": "string",
      "required": true,
      "modelId": "vision-prompt-dest2"
    },
    "destination_3": {
      "name": "destination_3",
      "label": "Destination 3",
      "type": "string",
      "required": true,
      "modelId": "vision-prompt-dest3"
    }
  }
}
```
