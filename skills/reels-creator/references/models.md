# Models: endpoints, inputs, prices

These are the recommended models, as verified in **October 2026** from each endpoint's public OpenAPI schema and fal's model pages. They are a starting point, not a cage. When a shot needs something else, search the live catalogue and say why you chose it.

## 0. Check on the day

**Check current prices and account access.** Historical figures below are examples,
not a quote. Use the current model page, genmedia pricing or the connected MCP
pricing tools. An unavailable or zero rate is not evidence of a free job; report
uncertainty and resolve it before spending.

**Inputs change too:**
- Read the schema before the first call of a session. It's public, no key needed:
  `curl -s 'https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=<id>'`
- Watch the enums: H3 Max wants `"1080P"`, FLUX 3 Max wants `"1080p"`.

**Search the live catalogue** for alternatives (more than 1,500 endpoints). Lead with current models, never last year's.

## 1. Voice: ElevenLabs v4 TTS

`fal-ai/elevenlabs/tts/eleven-v4` (also `elevenlabs/tts/eleven-v4`). **$0.08 per 1,000 characters.**

**Inputs:**
- `text`: required. It supports audio tags like `[curious]` and IPA between slashes, e.g. `/ˈnaɪki/`.
- `voice`: the ElevenLabs voice id given for the video.
- `stability`: 0–1. Use 0.5.
- `similarity_boost`: 0–1, schema default 0.75. **Use 0.95.**
- `seed`.
- `language_code`: ISO 639-1.
- `timestamps`: true gives character timings.
- `apply_text_normalization`: auto / on / off.
- `output_format`: use `mp3_44100_192`.

**Settings:**
- 3 seeds per line, so the user picks.
- Never `[softly]` or any whisper tag: it sounds affected.

## 2. The host on camera: H3 Max Lip Sync

`minimax/h3-max/lip-sync/image-to-video`: fal's H3 Max animates one image so that its face says the given audio. The clip carries the voice take exactly, at up to 2K and 24 fps, the master's rate.

**Inputs** (schema read October 2026):
- `image_url`: required. The presenter still; aspect ratio 0.4–2.5.
- `audio_url`: required, at least 5 s and up to 15 min. The output lasts exactly as long as the audio, so a short take is padded with silence (`host_lipsync.py prep`).
- `resolution`: 480P, 768P, 1080P or 2K. **The default is 768P**, so set `"1080P"`. The output takes the supported aspect ratio nearest the image: 1080×1920 for a 9:16 still.
- `enable_transcription`: default false. Pass true: the model transcribes the audio to guide the lips.
- `seed`, and `enable_safety_checker` (default true).
- There is no prompt.

**Output:** `video` at 24 fps carrying the audio resampled to 32 kHz (the mix uses the original take), plus `seed` and `duration`.

**Price** (model page, October 2026; the pricing API can show 0 in early access, and 0 is never quoted): **$0.16/s at 1080P**; $0.05/s at 480P, $0.08/s at 768P, $0.32/s at 2K. Past 15 s each second costs 1.2×. It is billed on the audio's length, so a host line padded to 5 s costs about $0.80 at 1080P.

## 3. Real-life b-roll: FLUX 3 Max

FLUX 3 Max is fal Research's video model, built on Black Forest Labs' FLUX 3 and post-trained with them (model page, October 2026). Use it when the shot must look filmed: people, places, products, everyday scenes.

**Routes:**
- `blackforestlabs/flux-3-max/text-to-video`: `prompt`;
- `blackforestlabs/flux-3-max/image-to-video`: `prompt` and `image_url`, plus an optional `end_image_url`;
- `blackforestlabs/flux-3-max/keyframes-to-video`: `prompt` and `keyframes` (≤ 10 `{image_url, frame_index}`, frames at 24 fps).

**Inputs (all routes):**
- `duration`: integer 5–20, default 5.
- `resolution`: 720p or 1080p. **The default is 720p**, so set 1080p.
- `aspect_ratio`: auto, 21:9, 2:1, 16:9, 4:3, 1:1, 3:4 or 9:16. auto is 16:9 for text and follows the image otherwise.
- `reasoning_level`: low or high, default high.
- `generate_audio`: default true. The clip's own sound becomes the ambience under the voice.
- `seed`.

**Price:**
- List: **$0.29/s at 1080p, $0.17/s at 720p**.
- Promos come and go: check the model page.
- The pricing API shows 0 (EAP).

**Prompts:** describe the shot plainly: subject, action, place, light, camera. No logos, no text, no public figures.

## 4. Everything else: H3 Max

H3 Max is fal's post-trained variant of MiniMax H3 (model page, October 2026). Use it for stylised, abstract, illustrated or designed footage: plates, textures, metaphors, motion behind type.

**Routes:**
- `minimax/h3-max/text-to-video`;
- `minimax/h3-max/image-to-video`: `image_url` and/or `end_image_url`.

**Inputs:**
- `prompt`: required.
- `prompt_expansion_mode`: **required**; disabled, balanced or quality. Use `"disabled"`, so the prompt you showed is the prompt that ran.
- `duration`: 0.92–15 s, default 5. The output can run about 0.7 s longer.
- `resolution`: 480P, 768P or 1080P. **The default is 768P.** 1080P is a latent refinement of a 768P source.
- `aspect_ratio`: 21:9, 16:9, 4:3, 1:1, 3:4 or 9:16.
- `target_audio_url`: ≥ 2 s, ≤ 15 MB, pins a sound to the soundtrack.
- `seed`.

**Price:** list **$0.16/s at 1080P** (model page; the pricing API shows 0 in EAP).

**Other routes** exist (reference-to-video, turbo, styles, extend, relight; lip-sync/image-to-video is the host route, §2). Read their schemas when needed.

## 5. SFX: Mirelo SFX 2.0

**$0.015 per second per sample. `num_samples` defaults to 2 and each sample is billed, so pass 1** unless the user wants options.

| Route | Inputs | Notes |
|---|---|---|
| `mirelo-ai/sfx2.0/video-to-audio` | `video_url` (required), `text_prompt`, `negative_prompt`, `preserve_speech` (default true), `return_speech`, `duration` 1–600 | `duration` defaults to **10 s**, clamped to the video's length: set it to the clip's length. Over 10 s it generates in 10 s windows |
| `mirelo-ai/sfx2.0/video-to-video` | same inputs | returns the video with its new sound mixed in |
| `mirelo-ai/sfx2.0/text-to-audio` | **`prompt`** (required; not `text_prompt`), `negative_prompt`, `duration` 0.1–600 (default **30**) | one-shot sounds for animation scenes |

All three routes also take `num_samples` (1–4), `seed`, `upload_audio_format` (wav, mp3, aac or flac) and `upload_audio_bitrate_kbps`.

## 6. Word timings: Scribe v2

`fal-ai/elevenlabs/speech-to-text/scribe-v2`. **$0.008 per minute.**

**Inputs:**
- `audio_url`.
- `language_code`.
- `diarize`: default true. Pass false.
- `tag_audio_events`.
- `keyterms`: up to 100. It adds a 30 % premium; use it for brand names Scribe misspells.

## 7. Music: ElevenLabs Music v2.5

`elevenlabs/music/v2.5`. **$0.60 per minute.**

**Inputs:**
- `composition_plan` (chunks with `text`, `duration_ms`, `positive_styles` and `negative_styles`), or `prompt` with `music_length_ms` (3,000–600,000).
- `force_instrumental`.
- `seed`: only with a plan.
- `output_format`: default `mp3_48000_192`.

## 8. Keyframes and start frames: Nano Banana Pro

`fal-ai/nano-banana-pro`. **$0.15 per image** (as listed; the 4K price may differ: check).

**Inputs:**
- `prompt`.
- `resolution`: 1K, 2K or 4K.
- `aspect_ratio`.
- `num_images`: 1–4.
- `context`: reference images.
- `seed`.

Use it for the start frame of an i2v shot, or as a cheaper presenter still for H3 Max Lip Sync (check the likeness against the photos; voice-and-host.md §3).

## 9. Fallbacks and other routes

**Seedance 2.5 US reference-to-video**, `bytedance/seedance-2.5/us/reference-to-video`, makes the presenter stills: frame 0 of a short clip from the presenter's photos (voice-and-host.md §3). It is not a talking-host route for a separate voice take: given the take as `@Audio1`, it re-performs the line at its own tempo and with its own pauses, so its lips never match the real take without retiming one of them.
- Price: billed per token, about **$1.16/s at 1080p, $0.47/s at 720p, $0.22/s at 480p** (October 2026).
- Inputs: `image_urls` (the presenter's photos), `prompt`, `duration` as a string (`"auto"` or `"4"`–`"30"`), `resolution` (default 720p), `generate_audio` (default true), and `audio_urls` (1.8–30.2 s, `@Audio1`) when it should speak.

**sync-lipsync v3**, `fal-ai/sync-lipsync/v3`, re-syncs the lips of an existing clip to a take.
- Inputs: `video_url` and `audio_url`; `sync_mode` is one of cut_off, loop, bounce, silence or remap.
- **$8 per minute:** the expensive last resort. It changes only the mouth of an existing clip, so the clip's own motion stays.

**Other lip-sync routes:** `fal-ai/kling-video/lipsync/audio-to-video` (a clip's lips to an audio file), `fal-ai/kling-video/ai-avatar/v2/pro` (an image and an audio file to a talking video) and `veed/fabric-1.0` (the same, 720p at most). Read each one's schema and price on the day, and check one line's frame rate and size before using it: the master is 24 fps (voice-and-host.md §4).

### Kling v4 reference-to-video (a presenter only when the user asks)

`kling/v4/reference-to-video`. **$0.157 per second at 720p, $0.235 at 1080p** (October 2026).

The presenter route is H3 Max Lip Sync (§2). With Kling's own voice the lips don't follow a separate take, and its create-voice step can return an empty result.

**Inputs:**
- `prompt`: ≤ 26,000 characters. It references the inputs as `@Element1`, `@Image1`, `@Video1` and `@Voice1`. Either `prompt` or `multi_prompt` is required.
- `multi_prompt`: shots as `[{prompt, duration}]`. The video's length is the sum of the shot durations.
- `elements`: up to 7 characters or objects.
  - Each element has `frontal_image_url`, `reference_image_urls` (1–3 other angles), `voice_id`, or `video_url`.
  - `video_url` is 3–8.05 s, ≥ 700 × 700 px, 24–60 fps, used instead of the images.
  - Up to 3 elements may carry a voice and up to 3 may be video elements.
- `image_urls`: up to 10.
- `video_urls`: up to 5, each 3–30 s, 30 s combined with the element videos.
- `voice_ids`: up to 3, counting voices bound to elements.
- Frames: `start_image_url`, `middle_image_urls` (≤ 8) and `end_image_url`.
- `duration`: integer 3–30, default 5.
- `resolution`: 720p or 1080p, default 1080p.
- `aspect_ratio`: auto, 16:9, 9:16, 1:1 or 21:9, default 16:9.

**No audio file goes in.** The voice enters as a `voice_id` made by **`fal-ai/kling-video/create-voice`**:
- input `voice_url`: an mp3, wav, mp4 or mov of 5–30 s of one clean voice;
- output `voice_id`;
- price not always readable. Read it before the first call on the model page (fal.ai/models/fal-ai/kling-video/create-voice). If it isn't shown, tell the user the price is unknown (it is a one-off per voice) and ask.

create-voice can come back empty with no error: check that a `voice_id` came back before building on it.

**Same family:** `kling/v4/image-to-video` ($0.157/s; `start_image_url` required, plus `end_image_url`, `middle_image_urls` and `multi_prompt`), and Kling v4 text-to-video and edit routes. Check their prices on the day.

## 10. What a 2-minute reel costs (list prices, October 2026)

| Item | Estimate |
|---|---|
| Voice takes: ~1,500 characters × 3 seeds × $0.08/1k | $0.36 |
| Presenter still: one Seedance clip, 4 s at 1080p (once per set) | $4.66 |
| Host clips: 4 lines × 5 s × $0.16/s (H3 Max Lip Sync, 1080P) | $3.20 |
| B-roll: 5 FLUX 3 Max clips × 5 s × $0.29/s (1080p) | $7.25 |
| Music: 2.5 min × $0.60/min | $1.50 |
| SFX: 10 sounds × 2 s × $0.015/s, one sample each | $0.30 |
| Scribe: every take | cents |
| **Total** | **about $17** (about $13 when the set's still already exists) |

Animation scenes are drawn in code and cost nothing. Promos lower the b-roll line.
