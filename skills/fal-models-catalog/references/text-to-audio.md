# Text-to-Audio Endpoints

Curated picks across 6 use cases. TTS Premium / Fast / Multilingual / Voice clone, Music Vocal+lyrics, Music Instrumental+SFX. Verify with `genmedia models --endpoint_id <id> --json` before running.

## TTS · Premium expressive

High-quality, expressive TTS.

- `fal-ai/elevenlabs/tts/eleven-v3`: ElevenLabs · Eleven v3
- `fal-ai/elevenlabs/text-to-dialogue/eleven-v3`: ElevenLabs · Text-to-Dialogue (multi-speaker scene)
- `fal-ai/minimax/speech-2.8-hd`: Minimax · Speech 2.8 HD

## TTS · Fast / cheap

Low-latency, economical TTS.

- `fal-ai/minimax/speech-2.8-turbo`: Minimax · 2.8 Turbo
- `fal-ai/minimax/speech-2.6-turbo`: Minimax · 2.6 Turbo
- `fal-ai/minimax/speech-02-turbo`: Minimax · 02 Turbo
- `fal-ai/minimax/preview/speech-2.5-turbo`: Minimax · 2.5 Turbo Preview
- `fal-ai/kokoro/american-english`: Kokoro (American English)
- `fal-ai/kokoro/british-english`: Kokoro (British English)

## TTS · Multilingual

Multi-language TTS.

- `fal-ai/elevenlabs/tts/multilingual-v2`: ElevenLabs · Multilingual v2
- `fal-ai/chatterbox/text-to-speech/multilingual`: Resemble · Chatterbox Multilingual
- `fal-ai/qwen-3-tts/text-to-speech/0.6b`: Alibaba · Qwen 3 TTS 0.6B
- `fal-ai/qwen-3-tts/text-to-speech/1.7b`: Alibaba · Qwen 3 TTS 1.7B
- `fal-ai/kokoro/brazilian-portuguese`: Kokoro PT-BR
- `fal-ai/kokoro/french`: Kokoro FR
- `fal-ai/kokoro/hindi`: Kokoro HI
- `fal-ai/kokoro/italian`: Kokoro IT
- `fal-ai/kokoro/japanese`: Kokoro JA
- `fal-ai/kokoro/mandarin-chinese`: Kokoro ZH
- `fal-ai/kokoro/spanish`: Kokoro ES

## TTS · Voice clone / design

Voice cloning and custom voice design.

- `fal-ai/minimax/voice-clone`: Minimax · Voice Cloning
- `fal-ai/minimax/voice-design`: Minimax · Voice Design
- `fal-ai/qwen-3-tts/clone-voice/0.6b`: Alibaba · Qwen 3 Clone (0.6B)
- `fal-ai/qwen-3-tts/clone-voice/1.7b`: Alibaba · Qwen 3 Clone (1.7B)
- `fal-ai/qwen-3-tts/voice-design/1.7b`: Alibaba · Qwen 3 Voice Design

## Music · Vocal + lyrics

Vocal music generation with lyrics.

- `fal-ai/elevenlabs/music`: ElevenLabs · Music
- `fal-ai/minimax-music/v2.6`: Minimax · Music 2.6
- `fal-ai/lyria2`: Lyria 2

## Music · Instrumental / SFX

Instrumental music and sound effects.

- `fal-ai/elevenlabs/sound-effects/v2`: ElevenLabs · Sound Effects v2
- `cassetteai/music-generator`: Cassette AI · Music Generator
- `fal-ai/stable-audio-25/text-to-audio`: Stability AI · Stable Audio 2.5

## Discovery

```bash
genmedia models --category text-to-speech --limit 10 --json
genmedia models --category text-to-audio --limit 10 --json
genmedia models "music generation" --json
genmedia models "sound effect" --json
```

## See also

- For TTS chained into talking-head video: [fal-recipes/references/character-lipsync.md](../../fal-recipes/references/character-lipsync.md)
- For TTS chained into video narration: [fal-recipes/references/video-with-audio.md](../../fal-recipes/references/video-with-audio.md)
- For STT (audio → text), see [audio-to-text.md](audio-to-text.md)
