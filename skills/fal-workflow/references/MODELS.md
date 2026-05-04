# Model Reference

Detailed configuration and usage for all supported models in fal.ai workflows.

## Image Generation

### Nano Banana Pro (DEFAULT)
```json
{
  "app": "fal-ai/nano-banana-pro",
  "input": {
    "prompt": "$node-prompt.output",
    "aspect_ratio": "16:9",
    "num_images": 1
  }
}
```
**Output:** `$node.images.0.url`

### Nano Banana Pro Edit (DEFAULT for editing)
```json
{
  "app": "fal-ai/nano-banana-pro/edit",
  "input": {
    "prompt": "$node-prompt.output",
    "image_urls": ["$input.source_image"],
    "aspect_ratio": "16:9",
    "resolution": "4K"
  }
}
```
**Output:** `$node.images.0.url`

### Other Image Models

| Model | App ID |
|-------|--------|
| FLUX.1 Dev | `fal-ai/flux/dev` |
| FLUX.1 Schnell | `fal-ai/flux/schnell` |
| FLUX.1 Pro | `fal-ai/flux-pro` |
| Ideogram v3 | `fal-ai/ideogram/v3` |
| Recraft v3 | `fal-ai/recraft-v3` |

---

## Video Generation

### Seedance 1.5 Pro (DEFAULT)
```json
{
  "app": "fal-ai/bytedance/seedance/v1.5/pro/image-to-video",
  "input": {
    "prompt": "$node-video-prompt.output",
    "image_url": "$node-image.images.0.url",
    "aspect_ratio": "16:9",
    "resolution": "720p",
    "duration": "5",
    "generate_audio": true
  }
}
```
**Output:** `$node.video.url`

### Kling Video O1 (Image-to-Video with First/Last Frame)
```json
{
  "app": "fal-ai/kling-video/o1/image-to-video",
  "input": {
    "prompt": "$node-prompt.output",
    "image_url": "$node-start-frame.images.0.url",
    "tail_image_url": "$node-end-frame.images.0.url",
    "duration": "5",
    "aspect_ratio": "16:9"
  }
}
```
**Output:** `$node.video.url`

### Kling Video 2.6 Pro (Best I2V)
```json
{
  "app": "fal-ai/kling-video/v2.6/pro/image-to-video",
  "input": {
    "prompt": "$node-prompt.output",
    "start_image_url": "$node-image.images.0.url",
    "duration": "5",
    "negative_prompt": "blur, distort, and low quality",
    "generate_audio": true
  }
}
```
**Output:** `$node.video.url`

**Parameters:**
- `prompt` - Video description (can include speech for lip-sync)
- `start_image_url` - Starting frame image URL
- `duration` - Video length: `"5"` or `"10"` seconds
- `negative_prompt` - What to avoid in generation
- `generate_audio` - Enable audio generation from prompt

**Best for:** High quality image-to-video with optional audio generation and lip-sync support.

### Other Video Models

| Model | App ID | Notes |
|-------|--------|-------|
| Veo 3.1 Fast | `fal-ai/veo3.1/fast/image-to-video` | High quality |
| Kling 2.6 Pro | `fal-ai/kling-video/v2.6/pro/image-to-video` | **Best I2V** |


---

## LLM Models

### Text LLM (DEFAULT - No images)
```json
{
  "app": "openrouter/router",
  "input": {
    "prompt": "$input.user_input",
    "system_prompt": "Your instructions here...",
    "model": "google/gemini-2.5-flash",
    "temperature": 0.7
  }
}
```
**Output:** `$node.output`

### Vision LLM (When image analysis needed)
```json
{
  "app": "openrouter/router/vision",
  "input": {
    "prompt": "$input.user_request",
    "system_prompt": "Analyze the image and...",
    "image_urls": ["$node-image.images.0.url"],
    "model": "google/gemini-3-pro-preview",
    "reasoning": true
  }
}
```
**Output:** `$node.output`

**Available LLM Models:**
- `google/gemini-2.5-flash` - Fast, good quality
- `google/gemini-3-pro-preview` - Best reasoning
- `anthropic/claude-sonnet-4.5` - Best for complex tasks

---

## Audio/Music Generation

### ElevenLabs Music
```json
{
  "app": "fal-ai/elevenlabs/music",
  "input": {
    "prompt": "Mysterious soundtrack, jungle themes, tribal percussion",
    "respect_sections_durations": true,
    "output_format": "mp3_44100_128"
  }
}
```
**Output:** `$node.audio_file.url`

### MMAudio (Video to Audio)
```json
{
  "app": "fal-ai/mmaudio-v2",
  "input": {
    "video_url": "$node-video.video.url",
    "prompt": "Ambient nature sounds"
  }
}
```

### Stable Audio
```json
{
  "app": "fal-ai/stable-audio",
  "input": {
    "prompt": "Cinematic orchestral music"
  }
}
```

### Other Music Models

| Model | App ID |
|-------|--------|
| MiniMax Music v2 | `fal-ai/minimax-music/v2` |

---

## Text-to-Speech

### ElevenLabs TTS v3
```json
{
  "app": "fal-ai/elevenlabs/tts/eleven-v3",
  "input": {
    "text": "$node-llm.output",
    "voice": "Aria",
    "stability": 0.5,
    "similarity_boost": 0.75,
    "speed": 1
  }
}
```
**Output:** `$node.audio.url`

**Parameters:**
- `text` - Text to convert to speech
- `voice` - Voice name (e.g., "Aria", "Roger", "Sarah")
- `stability` - Voice stability (0-1)
- `similarity_boost` - Voice clarity (0-1)
- `speed` - Speech speed multiplier

### MiniMax Speech 2.6 HD (Best Quality)
```json
{
  "app": "fal-ai/minimax/speech-2.6-hd",
  "input": {
    "prompt": "$node-llm.output",
    "voice_setting": {
      "voice_id": "Wise_Woman",
      "speed": 1,
      "vol": 1,
      "pitch": 0
    },
    "output_format": "mp3"
  }
}
```
**Output:** `$node.audio.url`

**Parameters:**
- `prompt` - Text to convert to speech
- `voice_setting.voice_id` - Voice ID (e.g., "Wise_Woman", "Young_Man")
- `voice_setting.speed` - Speech speed (0.5-2)
- `voice_setting.vol` - Volume (0-1)
- `voice_setting.pitch` - Pitch adjustment (-12 to 12)
- `output_format` - Output format: `"mp3"`, `"wav"`, `"hex"`

### MiniMax Voice Clone
Clone a voice from audio sample, then use the cloned voice ID in MiniMax Speech.

```json
{
  "app": "fal-ai/minimax/voice-clone",
  "input": {
    "audio_url": "$input.voice_sample",
    "text": "Preview text for the cloned voice",
    "model": "speech-02-hd"
  }
}
```
**Output:** `$node.audio.url`, `$node.voice_id`

**Use cloned voice in Speech 2.6 HD:**
```json
{
  "app": "fal-ai/minimax/speech-2.6-hd",
  "input": {
    "prompt": "$node-llm.output",
    "voice_setting": {
      "voice_id": "$node-voice-clone.voice_id"
    }
  }
}
```

### Other TTS Models

| Model | App ID | Notes |
|-------|--------|-------|
| MiniMax Speech 2.6 Turbo | `fal-ai/minimax/speech-2.6-turbo` | Fast |
| Chatterbox | `fal-ai/chatterbox/text-to-speech/multilingual` | Multi-language |

---

## Text Utilities (CRITICAL for combining values)

**⚠️ These are the ONLY ways to combine text values - string interpolation is NOT supported!**

### Text Concat (2 texts)
Concatenates exactly TWO text values. `text1` can be static text!

```json
{
  "app": "fal-ai/text-concat",
  "input": {
    "text1": "Brand expert response:",
    "text2": "$node-llm.output"
  }
}
```
**Output:** `$node.results`

**Use Cases:**
- Add a label/prefix to a variable: `"text1": "Scene 1:", "text2": "$node.output"`
- Combine static instruction with dynamic content

### Merge Text (Multiple texts)
Merges an ARRAY of text values with a separator.

```json
{
  "app": "fal-ai/workflow-utilities/merge-text",
  "input": {
    "texts": [
      "$node-a.results",
      "$node-b.results",
      "$node-c.results"
    ],
    "separator": "------"
  }
}
```
**Output:** `$node.text`

**Use Cases:**
- Combine 3+ LLM outputs before passing to next node
- Merge multiple expert responses into single context

### Pattern: Label + Merge
Common pattern for combining multiple labeled outputs:

```json
// Step 1: Add labels with text-concat
"label-brand": {
  "app": "fal-ai/text-concat",
  "input": {
    "text1": "Brand expert:",
    "text2": "$brand-llm.output"
  }
},
"label-visual": {
  "app": "fal-ai/text-concat",
  "input": {
    "text1": "Visual director:",
    "text2": "$visual-llm.output"
  }
},

// Step 2: Merge labeled outputs
"merged-context": {
  "depends": ["label-brand", "label-visual"],
  "app": "fal-ai/workflow-utilities/merge-text",
  "input": {
    "texts": ["$label-brand.results", "$label-visual.results"],
    "separator": "\n\n---\n\n"
  }
},

// Step 3: Use merged context
"final-llm": {
  "depends": ["merged-context"],
  "input": {
    "prompt": "$merged-context.text"
  }
}
```

---

## FFmpeg Utilities (CRITICAL)

### Extract Frame from Video
```json
{
  "app": "fal-ai/ffmpeg-api/extract-frame",
  "input": {
    "video_url": "$node-video.video.url",
    "frame_type": "first"
  }
}
```
**Output:** `$node.frame.url`

**frame_type options:** `"first"` or `"last"`

**Use Cases:**
- Get last frame for video extension
- Get first frame for transitions
- Extract frame for first/last frame video generation

### Merge Multiple Videos
```json
{
  "app": "fal-ai/ffmpeg-api/merge-videos",
  "input": {
    "video_urls": [
      "$node-video-1.video.url",
      "$node-video-2.video.url",
      "$node-video-3.video.url"
    ]
  }
}
```
**Output:** `$node.video.url`

### Merge Audio and Video
```json
{
  "app": "fal-ai/ffmpeg-api/merge-audio-video",
  "input": {
    "video_url": "$node-video.video.url",
    "audio_url": "$node-music.audio_file.url"
  }
}
```
**Output:** `$node.video.url`

---

## Image Utilities

### Crop Image
Crops a portion of an image using percentage-based coordinates.

```json
{
  "app": "fal-ai/workflow-utilities/crop-image",
  "input": {
    "image_url": "$node-image.images.0.url",
    "x_percent": 0,
    "y_percent": 0,
    "width_percent": 33.333333,
    "height_percent": 33.333333
  }
}
```
**Output:** `$node.image.url`

**Parameters:**
- `x_percent`: Starting X position (0-100)
- `y_percent`: Starting Y position (0-100)
- `width_percent`: Width of crop area (0-100)
- `height_percent`: Height of crop area (0-100)

**Use Cases:**
- Split image into grid tiles (3x3, 2x2, etc.)
- Extract specific region from generated image
- Create multiple crops for parallel processing

**Example: 3x3 Grid Split**
```json
// Top-left tile
"crop-1": { "input": { "x_percent": 0, "y_percent": 0, "width_percent": 33.33, "height_percent": 33.33 } }
// Top-center tile
"crop-2": { "input": { "x_percent": 33.33, "y_percent": 0, "width_percent": 33.33, "height_percent": 33.33 } }
// Top-right tile
"crop-3": { "input": { "x_percent": 66.67, "y_percent": 0, "width_percent": 33.33, "height_percent": 33.33 } }
// ... and so on for all 9 tiles
```

---

## Image Processing

### Upscale Image
```json
{
  "app": "fal-ai/seedvr/upscale/image",
  "input": {
    "image_url": "$node-image.images.0.url"
  }
}
```
**Output:** `$node.image.url`

### Remove Background
```json
{
  "app": "fal-ai/bria/background/remove",
  "input": {
    "image_url": "$node-image.images.0.url"
  }
}
```
**Output:** `$node.image.url`

---

## 3D Generation (Image to 3D)

### Hunyuan3D v3 (Recommended)
```json
{
  "app": "fal-ai/hunyuan3d-v3/image-to-3d",
  "input": {
    "input_image_url": "$node-image.images.0.url",
    "face_count": 500000,
    "generate_type": "Normal",
    "polygon_type": "triangle"
  }
}
```
**Output:** `$node.model_mesh.url`

**Parameters:**
- `input_image_url` - Source image URL
- `face_count` - Mesh detail level (default: 500000)
- `generate_type` - Generation mode: `"Normal"`, `"Fast"`
- `polygon_type` - Mesh type: `"triangle"`, `"quad"`

### Rodin v2 (Multi-view)
```json
{
  "app": "fal-ai/hyper3d/rodin/v2",
  "input": {
    "input_image_urls": [
      "$node-front.images.0.url",
      "$node-left.images.0.url",
      "$node-right.images.0.url",
      "$node-back.images.0.url"
    ],
    "quality_mesh_option": "500K Triangle",
    "material": "All"
  }
}
```
**Output:** `$node.model_mesh.url`

**Best for:** Multi-view 3D generation (provide multiple angles for better results)

