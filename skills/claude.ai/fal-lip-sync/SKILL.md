---
name: fal-lip-sync
description: Create talking head videos, lip sync audio to video, and animate portraits with expressions. Use when the user requests "Talking head", "Lip sync", "Make this person talk", "Animate portrait", "Live portrait", "Avatar video".
metadata:
  author: fal-ai
  version: "1.0.0"
---

# fal-lip-sync

Create talking head videos, sync lips to audio, and animate portraits using fal.ai models.

## Scripts

| Script | Purpose |
|--------|---------|
| `talking-head.sh` | Generate a talking head video from an image + audio/text |
| `lip-sync.sh` | Sync lips in an existing video to new audio |

## Usage

### Talking Head (Image + Audio → Video)
```bash
./scripts/talking-head.sh --image-url "https://example.com/portrait.jpg" --audio-url "https://example.com/speech.mp3" --model veed/fabric-1.0
```

### Talking Head (Image + Text → Video with auto TTS)
```bash
./scripts/talking-head.sh --image-url "https://example.com/portrait.jpg" --text "Hello, welcome to our presentation" --model fal-ai/creatify/aurora
```

### Lip Sync (Video + Audio → Synced Video)
```bash
./scripts/lip-sync.sh --video-url "https://example.com/video.mp4" --audio-url "https://example.com/new-speech.mp3"
```

## Arguments

### talking-head.sh
| Argument | Description | Required |
|----------|-------------|----------|
| `--image-url` | URL of portrait/face image | Yes |
| `--audio-url` | URL of audio to sync | Yes (or --text) |
| `--text` | Text to speak (auto TTS) | Yes (or --audio-url) |
| `--model` / `-m` | Model endpoint | No (default: veed/fabric-1.0) |
| `--tts-model` | TTS model for --text mode | No (default: fal-ai/minimax/speech-2.6-turbo) |
| `--wait` / `-w` | Wait for completion | No (default: true) |
| `--async` / `-a` | Return request ID immediately | No |

### lip-sync.sh
| Argument | Description | Required |
|----------|-------------|----------|
| `--video-url` | URL of video to lip sync | Yes |
| `--audio-url` | URL of audio to sync to | Yes |
| `--model` / `-m` | Model endpoint | No (default: fal-ai/sync-lipsync/v2) |

## Finding Models

To discover the best and latest lip sync and talking head models, use the search API:

```bash
# Search for talking head models
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "talking head"

# Search for lip sync models
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "lip sync"

# Search for live portrait / expression transfer
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "live portrait"
```

Or use the `search_models` MCP tool with relevant keywords like "lip sync", "talking head", "avatar".

## Output Format
```json
{
  "video": {
    "url": "https://fal.media/files/...",
    "content_type": "video/mp4"
  }
}
```

Present the video URL directly to the user.
