---
name: fal-generate
description: Generate images and videos using fal.ai AI models with queue support. Use when the user requests "Generate image", "Create video", "Make a picture of...", "Text to image", "Image to video", "Search models", or similar generation tasks.
metadata:
  author: fal-ai
  version: "3.0.0"
---

# fal.ai Generate

Generate images and videos using state-of-the-art AI models on fal.ai.

## Scripts

| Script | Purpose |
|--------|---------|
| `generate.sh` | Generate images/videos (queue-based) |
| `upload.sh` | Upload local files to fal CDN |
| `search-models.sh` | Search and discover models |
| `get-schema.sh` | Get OpenAPI schema for any model |

## Queue System (Default)

All requests use the queue system by default for reliability:

```
User Request → Queue Submit → Poll Status → Get Result
                   ↓
              request_id
```

**Benefits:**
- Long-running tasks (video) won't timeout
- Can check status anytime
- Can cancel queued requests
- Results retrievable even if connection drops

## Generate Content

```bash
bash /mnt/skills/user/fal-generate/scripts/generate.sh [options]
```

### Basic Usage (Queue Mode)

```bash
# Image - submits to queue, waits for completion
bash generate.sh --prompt "A serene mountain landscape" --model "fal-ai/nano-banana-pro"

# Video - same, but takes longer
bash generate.sh --prompt "Ocean waves crashing" --model "fal-ai/veo3.1"

# Image-to-Video
bash generate.sh \
  --prompt "Camera slowly zooms in" \
  --model "fal-ai/kling-video/v2.6/pro/image-to-video" \
  --image-url "https://example.com/image.jpg"
```

### Async Mode (Return Immediately)

For long video jobs, use `--async` to get request_id immediately:

```bash
# Submit and return immediately
bash generate.sh --prompt "Epic battle scene" --model "fal-ai/veo3.1" --async

# Output:
# Request ID: abc123-def456
# Request submitted. Use these commands to check:
#   Status: ./generate.sh --status "abc123-def456" --model "fal-ai/veo3.1"
#   Result: ./generate.sh --result "abc123-def456" --model "fal-ai/veo3.1"
```

### Queue Operations

```bash
# Check status
bash generate.sh --status "request_id" --model "fal-ai/veo3.1"
# → IN_QUEUE (position: 3) | IN_PROGRESS | COMPLETED

# Get result (when COMPLETED)
bash generate.sh --result "request_id" --model "fal-ai/veo3.1"

# Cancel (only if still queued)
bash generate.sh --cancel "request_id" --model "fal-ai/veo3.1"
```

### Show Logs During Generation

```bash
bash generate.sh --prompt "A sunset" --model "fal-ai/nano-banana-pro" --logs
# Status: IN_QUEUE (position: 2)
# Status: IN_PROGRESS
#   > Loading model...
#   > Generating image...
# Status: COMPLETED
```

## File Upload

### Option 1: Auto-upload with --file

```bash
# Local file is automatically uploaded to fal CDN
bash generate.sh \
  --file "/path/to/photo.jpg" \
  --model "fal-ai/kling-video/v2.6/pro/image-to-video" \
  --prompt "Camera zooms in slowly"
```

### Option 2: Manual upload with upload.sh

```bash
# Upload first
URL=$(bash upload.sh --file "/path/to/photo.jpg")
# → https://v3.fal.media/files/xxx/photo.jpg

# Then generate
bash generate.sh --image-url "$URL" --model "..." --prompt "..."
```

### Option 3: Use existing URL

```bash
# Any public URL works
bash generate.sh --image-url "https://example.com/image.jpg" ...
```

**Supported file types:**
- Images: jpg, jpeg, png, gif, webp
- Videos: mp4, mov, webm
- Audio: mp3, wav, flac

**Upload flow (two-step):**
```
1. POST rest.alpha.fal.ai/storage/auth/token?storage_type=fal-cdn-v3
   → {"token": "...", "base_url": "https://v3b.fal.media"}

2. POST {base_url}/files/upload
   Authorization: Bearer {token}
   → {"access_url": "https://v3b.fal.media/files/..."}
```

**Max file size:** 100MB (simple upload)

## Arguments Reference

| Argument | Description | Default |
|----------|-------------|---------|
| `--prompt`, `-p` | Text description | (required) |
| `--model`, `-m` | Model ID | `fal-ai/nano-banana-pro` |
| `--image-url` | Input image URL for I2V | - |
| `--file`, `--image` | Local file (auto-uploads) | - |
| `--size` | `square`, `portrait`, `landscape` | `landscape_4_3` |
| `--num-images` | Number of images | 1 |

**Mode Options:**
| Argument | Description |
|----------|-------------|
| (default) | Queue mode - submit and poll until complete |
| `--async` | Submit to queue, return request_id immediately |
| `--sync` | Synchronous (not recommended for video) |
| `--logs` | Show generation logs while polling |

**Queue Operations:**
| Argument | Description |
|----------|-------------|
| `--status ID` | Check status of a queued request |
| `--result ID` | Get result of a completed request |
| `--cancel ID` | Cancel a queued request |

**Advanced:**
| Argument | Description | Default |
|----------|-------------|---------|
| `--poll-interval` | Seconds between status checks | 2 |
| `--timeout` | Max seconds to wait | 600 |
| `--lifecycle N` | Object expiration in seconds | - |
| `--schema [MODEL]` | Get OpenAPI schema | - |

## Finding Models

To discover the best and latest models, use the search API:

```bash
# Search by category
bash search-models.sh --category "text-to-image"
bash search-models.sh --category "text-to-video"
bash search-models.sh --category "image-to-video"

# Search by keyword
bash search-models.sh --query "flux"
bash search-models.sh --query "kling video"
```

Or use the `search_models` MCP tool with relevant keywords.

**Categories:** `text-to-image`, `image-to-image`, `text-to-video`, `image-to-video`, `text-to-speech`, `speech-to-text`

## Get Model Schema (OpenAPI)

**IMPORTANT:** Fetch schema to see exact parameters for any model.

```bash
# Get schema
bash get-schema.sh --model "fal-ai/nano-banana-pro"

# Show only input parameters
bash get-schema.sh --model "fal-ai/kling-video/v2.6/pro/image-to-video" --input

# Quick schema via generate.sh
bash generate.sh --schema "fal-ai/veo3.1"
```

**API Endpoint:**
```
https://fal.ai/api/openapi/queue/openapi.json?endpoint_id={model-id}
```

## Output

**Queue Submit Response:**
```json
{
  "request_id": "abc123-def456",
  "status": "IN_QUEUE",
  "response_url": "https://queue.fal.run/.../requests/abc123-def456",
  "status_url": "https://queue.fal.run/.../requests/abc123-def456/status",
  "cancel_url": "https://queue.fal.run/.../requests/abc123-def456/cancel"
}
```

**Final Result:**
```json
{
  "images": [{ "url": "https://v3.fal.media/files/...", "width": 1024, "height": 768 }]
}
```

## Present Results to User

**Images:**
```
![Generated Image](https://v3.fal.media/files/...)
• 1024×768 | Generated in 2.2s
```

**Videos:**
```
[Click to view video](https://v3.fal.media/files/.../video.mp4)
• Duration: 5s | Generated in 45s
```

**Async Submission:**
```
Request submitted to queue.
• Request ID: abc123-def456
• Model: fal-ai/veo3
• Check status: --status "abc123-def456"
```

## Object Lifecycle (Optional)

Control how long generated files remain accessible:

```bash
# Files expire after 1 hour (3600 seconds)
bash generate.sh --prompt "..." --lifecycle 3600

# Files expire after 24 hours
bash generate.sh --prompt "..." --lifecycle 86400
```

## Troubleshooting

### Timeout Error
```
Error: Timeout after 600s
Request ID: abc123-def456
```
**Solution:** Use `--status` and `--result` to check manually, or increase `--timeout`.

### API Key Error
```
Error: FAL_KEY not set
```
**Solution:** Run `./generate.sh --add-fal-key` or `export FAL_KEY=your_key`.

### Network Error (claude.ai)
Go to `claude.ai/settings/capabilities` and add `*.fal.ai` to allowed domains.
