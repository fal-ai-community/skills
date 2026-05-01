# Audio-to-Text Endpoints

Curated picks for STT (speech-to-text) and audio cleanup. Verify with `genmedia models --endpoint_id <id> --json` before running.

## STT · General transcription

General-purpose speech → text.

- `fal-ai/wizper`: Whisper v3 (fal.ai edition)
- `fal-ai/speech-to-text`: fal.ai Speech-to-Text
- `fal-ai/speech-to-text/turbo`: fal.ai STT Turbo
- `fal-ai/speech-to-text/stream`: fal.ai STT Stream
- `fal-ai/speech-to-text/turbo/stream`: fal.ai STT Turbo Stream
- `fal-ai/elevenlabs/speech-to-text`: ElevenLabs · STT

## STT · Diarization (speaker labels)

Transcription with speaker separation.

- `fal-ai/elevenlabs/speech-to-text/scribe-v2`: ElevenLabs · Scribe v2

## Audio cleanup / separation

Audio cleanup, isolation, separation.

- `fal-ai/demucs`: Demucs (vocal/instrumental separation)
- `fal-ai/elevenlabs/audio-isolation`: ElevenLabs · Audio Isolation
- `fal-ai/sam-audio/separate`: Sam Audio · Separate
- `fal-ai/sam-audio/span-separate`: Sam Audio · Span Separate

## Common parameters

Inspect schema before running:

```bash
genmedia schema fal-ai/wizper --json
genmedia schema fal-ai/elevenlabs/speech-to-text/scribe-v2 --json
```

Frequently exposed:

- `audio_url`: URL of audio file
- `language`: explicit language hint (auto-detected if omitted)
- `task`: `transcribe` (default) or `translate` (Whisper translates to English)
- `chunk_level`: segment / word / sentence (when supported)
- `diarize`: boolean (Scribe v2)

## Discovery

```bash
genmedia models --category speech-to-text --json
genmedia models "audio isolation" --json
genmedia docs "speech to text" --json
```

## See also

- For TTS (the inverse), see [text-to-audio.md](text-to-audio.md)
- For video subtitle workflow, see [fal-recipes/references/video-with-audio.md](../../fal-recipes/references/video-with-audio.md)
