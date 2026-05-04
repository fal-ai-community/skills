# Image-to-Video Endpoints

Curated picks across 6 use cases. **Seedance 2.0** dominates for general I2V; **Kling O3 / V3** specializes in reference-to-video and 4K; **Sora 2** is included for I2V. Avatar/lipsync has its own large bucket. Verify with `genmedia models --endpoint_id <id> --json` before running.

## Premium realism

Final-quality image-to-video.

- `bytedance/seedance-2.0/image-to-video`: ByteDance · Seedance 2.0
- `bytedance/seedance-2.0/reference-to-video`: ByteDance · Seedance 2.0 Reference
- `fal-ai/bytedance/seedance/v1.5/pro/image-to-video`: ByteDance · Seedance 1.5 Pro
- `fal-ai/veo3.1/image-to-video`: Google · Veo 3.1
- `fal-ai/kling-video/v3/pro/image-to-video`: Kling · V3 Pro
- `fal-ai/kling-video/o3/pro/image-to-video`: Kling · O3 Pro
- `fal-ai/kling-video/o3/pro/reference-to-video`: Kling · O3 Pro Reference
- `fal-ai/sora-2/image-to-video`: OpenAI · Sora 2
- `fal-ai/minimax/hailuo-2.3/pro/image-to-video`: Minimax · Hailuo 2.3 Pro

## Fast / cheap

Economical / fast I2V.

- `bytedance/seedance-2.0/fast/image-to-video`: ByteDance
- `bytedance/seedance-2.0/fast/reference-to-video`: ByteDance
- `fal-ai/bytedance/seedance/v1/pro/fast/image-to-video`: ByteDance
- `xai/grok-imagine-video/image-to-video`: xAI · Grok Imagine
- `xai/grok-imagine-video/reference-to-video`: xAI
- `fal-ai/veo3.1/lite/image-to-video`: Google · Veo 3.1 Lite
- `fal-ai/kling-video/v3/standard/image-to-video`: Kling · V3 Standard
- `fal-ai/minimax/hailuo-2.3/standard/image-to-video`: Minimax

## First/last frame interpolation

Controlled transition between start and end frames.

- `fal-ai/kling-video/o1/image-to-video`: Kling · O1 First-Last (Pro)
- `fal-ai/kling-video/o1/standard/image-to-video`: Kling · O1 First-Last (Standard)
- `fal-ai/veo3.1/first-last-frame-to-video`: Google · Veo 3.1
- `fal-ai/veo3.1/fast/first-last-frame-to-video`: Google · Veo 3.1 Fast
- `fal-ai/veo3.1/lite/first-last-frame-to-video`: Google · Veo 3.1 Lite
- `fal-ai/wan-flf2v`: Alibaba · Wan 2.1 First-Last
- `fal-ai/vidu/q1/start-end-to-video`: Vidu
- `fal-ai/vidu/start-end-to-video`: Vidu
- `fal-ai/pixverse/c1/image-to-video`: PixVerse C1

## Reference-to-video

Multiple reference images (person / style / element) → video.

- `bytedance/seedance-2.0/reference-to-video`: ByteDance · Seedance 2.0
- `bytedance/seedance-2.0/fast/reference-to-video`: ByteDance · Fast
- `fal-ai/bytedance/seedance/v1/lite/reference-to-video`: ByteDance · Lite
- `fal-ai/kling-video/o3/pro/reference-to-video`: Kling · O3 Pro
- `fal-ai/kling-video/o3/standard/reference-to-video`: Kling · O3 Standard
- `fal-ai/kling-video/o3/4k/reference-to-video`: Kling · O3 4K
- `alibaba/happy-horse/reference-to-video`: Alibaba · Happy Horse
- `xai/grok-imagine-video/reference-to-video`: xAI · Grok Imagine
- `fal-ai/veo3.1/reference-to-video`: Google · Veo 3.1
- `fal-ai/wan/v2.7/reference-to-video`: Alibaba · Wan 2.7
- `fal-ai/pixverse/c1/reference-to-video`: PixVerse C1

## 4K capable

Endpoints with native 4K output.

- `fal-ai/kling-video/v3/4k/image-to-video`: Kling · V3 4K
- `fal-ai/kling-video/o3/4k/image-to-video`: Kling · O3 4K
- `fal-ai/kling-video/o3/4k/reference-to-video`: Kling · O3 4K Reference

## Avatar / talking head / lipsync

Talking head, avatar, lip-sync video. The widest bucket in this modality, models differ meaningfully in input requirements, motion style, and language support.

- `veed/fabric-1.0`: Veed · Fabric 1.0 (image + audio)
- `fal-ai/creatify/aurora`: Creatify · Aurora
- `fal-ai/bytedance/omnihuman`: ByteDance · OmniHuman
- `fal-ai/bytedance/omnihuman/v1.5`: ByteDance · OmniHuman v1.5
- `bytedance/lynx`: ByteDance · Lynx
- `fal-ai/kling-video/v1/standard/ai-avatar`: Kling · AI Avatar (Standard)
- `fal-ai/kling-video/v1/pro/ai-avatar`: Kling · AI Avatar (Pro)
- `fal-ai/kling-video/ai-avatar/v2/pro`: Kling · AI Avatar v2 Pro
- `fal-ai/kling-video/ai-avatar/v2/standard`: Kling · AI Avatar v2 Standard
- `fal-ai/hunyuan-avatar`: Tencent · Hunyuan Avatar
- `fal-ai/hunyuan-portrait`: Tencent · Hunyuan Portrait
- `fal-ai/hunyuan-custom`: Tencent · Hunyuan Custom
- `fal-ai/kling-video/lipsync/audio-to-video`: Kling · Lipsync Audio-to-Video
- `fal-ai/kling-video/lipsync/text-to-video`: Kling · Lipsync Text-to-Video
- `fal-ai/flashtalk`: Flashtalk

For the multi-step TTS → lipsync recipe, see [fal-recipes/references/character-lipsync.md](../../fal-recipes/references/character-lipsync.md).

## Family-specific prompting

- Kling → [fal-prompting/references/kling.md](../../fal-prompting/references/kling.md)
- Happy Horse → [fal-prompting/references/happy-horse.md](../../fal-prompting/references/happy-horse.md)

## Discovery

```bash
genmedia models --category image-to-video --limit 10 --json
genmedia docs "image to video" --json
```
