# Common Workflow Patterns

Reusable patterns for building fal.ai workflows.

## Pattern 1: LLM Prompt → Image → Video

```
[Input] → [LLM: Image Prompt] → [Image Gen]
                ↓
          [LLM: Video Prompt] → [Video Gen] → [Output]
```

---

## Pattern 2: Parallel Processing (Fan-Out)

```
                → [Process A] →
[Hub Node] → [Process B] → [Merge] → [Output]
                → [Process C] →
```

All parallel nodes depend on hub, NOT on each other.

---

## Pattern 3: Video Extension with Extract Frame

```
[Video 1] → [Extract Last Frame] → [Video 2 with Start Frame] → [Merge] → [Output]
```

```json
"node-extract": {
  "depends": ["node-video-1"],
  "app": "fal-ai/ffmpeg-api/extract-frame",
  "input": {
    "video_url": "$node-video-1.video.url",
    "frame_type": "last"
  }
},
"node-video-2": {
  "depends": ["node-extract", "node-prompt-2"],
  "app": "fal-ai/kling-video/o1/image-to-video",
  "input": {
    "prompt": "$node-prompt-2.output",
    "image_url": "$node-extract.frame.url"
  }
}
```

---

## Pattern 4: First/Last Frame Video (Kling O1)

```
[Start Image] →
                → [Kling O1 Video] → [Output]
[End Image]   →
```

```json
"node-video": {
  "depends": ["node-start-frame", "node-end-frame", "node-prompt"],
  "app": "fal-ai/kling-video/o1/image-to-video",
  "input": {
    "prompt": "$node-prompt.output",
    "image_url": "$node-start-frame.images.0.url",
    "tail_image_url": "$node-end-frame.images.0.url"
  }
}
```

---

## Pattern 5: Video with Custom Music

```
[Video Gen] →                    → [Merge Audio/Video] → [Output]
[Music Gen] → [audio_file.url] →
```

```json
"node-music": {
  "depends": ["input"],
  "app": "fal-ai/elevenlabs/music",
  "input": {
    "prompt": "$input.music_style"
  }
},
"node-merge": {
  "depends": ["node-video", "node-music"],
  "app": "fal-ai/ffmpeg-api/merge-audio-video",
  "input": {
    "video_url": "$node-video.video.url",
    "audio_url": "$node-music.audio_file.url"
  }
}
```

---

## Pattern 6: Multi-Destination Campaign (Complex)

Pattern for multi-destination marketing videos:

```
[Input: dest_1] → [Vision LLM: Prompt] → [Edit Image] → [Upscale] →
                                                                    → [Vision LLM: Video Prompt] → [Video Gen]
                  [Edit: Remove Text] → [Upscale] →

[Input: dest_2] → [Same pattern...]
[Input: dest_3] → [Same pattern...]

All Videos → [Merge Videos] → [Output]
```
