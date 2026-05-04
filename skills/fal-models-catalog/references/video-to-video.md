# Video-to-Video Endpoints

Curated picks across 5 use cases. **Kling O3** dominates content edit and style remix; **Wan family** specializes in animate/replace and motion control; **Topaz** is the upscale standard. Verify with `genmedia models --endpoint_id <id> --json` before running.

## Style remix / restyle

Restyle the entire video.

- `fal-ai/kling-video/o3/pro/video-to-video/reference`: Kling · O3 Pro Reference
- `fal-ai/kling-video/o3/standard/video-to-video/reference`: Kling · O3 Standard Reference
- `fal-ai/bytedance/video-stylize`: ByteDance · Video Stylize
- `bytedance/seedance-2.0/reference-to-video`: ByteDance · Seedance 2.0 Reference

## Content edit

Change a specific element while preserving motion.

- `fal-ai/kling-video/o3/pro/video-to-video/edit`: Kling · O3 Pro Edit
- `fal-ai/kling-video/o3/standard/video-to-video/edit`: Kling · O3 Standard Edit
- `alibaba/happy-horse/video-edit`: Alibaba · Happy Horse Video Edit
- `fal-ai/wan/v2.7/edit-video`: Alibaba · Wan 2.7 Edit
- `fal-ai/wan-vace-apps/video-edit`: Alibaba · Wan VACE Edit
- `xai/grok-imagine-video/edit-video`: xAI · Grok Imagine Edit
- `bytedance/seedance-2.0/reference-to-video`: ByteDance

## Animate / replace / motion control

Character animation, motion control, dreamactor.

- `fal-ai/wan/v2.2-14b/animate/move`: Alibaba · Wan-2.2 Animate Move
- `fal-ai/wan/v2.2-14b/animate/replace`: Alibaba · Wan-2.2 Animate Replace
- `fal-ai/bytedance/dreamactor/v2`: ByteDance · DreamActor v2
- `fal-ai/kling-video/v3/pro/motion-control`: Kling · V3 Pro Motion Control
- `fal-ai/kling-video/v3/standard/motion-control`: Kling · V3 Standard Motion Control
- `fal-ai/kling-video/v2.6/pro/motion-control`: Kling · V2.6 Pro Motion Control
- `fal-ai/kling-video/v2.6/standard/motion-control`: Kling · V2.6 Standard Motion Control
- `fal-ai/wan-fun-control`: Alibaba · Wan 2.2 Fun Control

## Upscale

Increase video resolution.

- `fal-ai/topaz/upscale/video`: Topaz Labs · Video Upscale
- `fal-ai/bytedance-upscaler/upscale/video`: ByteDance · Upscaler
- `fal-ai/wan-vision-enhancer`: Alibaba · Wan Vision Enhancer

## Background removal

Video background removal / matting.

- `fal-ai/birefnet/v2/video`: BiRefNet v2 Video
- `bria/video/background-removal`: Bria AI · Video BG Removal
- `veed/video-background-removal`: Veed · Video BG Removal
- `veed/video-background-removal/green-screen`: Veed · Green Screen

## VACE / specialized control

Wan VACE family covers inpaint / outpaint / reframe / depth / pose control through multiple endpoints. See [fal-workflow/references/utility-endpoints.md](../../fal-workflow/references/utility-endpoints.md) and discover via the genmedia CLI:

```bash
genmedia models "wan vace" --json
```

## Discovery

```bash
genmedia models --category video-to-video --limit 10 --json
genmedia docs "video editing" --json
```
