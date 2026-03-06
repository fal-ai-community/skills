---
name: fal-audio
description: Text-to-speech and speech-to-text using fal.ai audio models. Use when the user requests "Convert text to speech", "Transcribe audio", "Generate voice", "Speech to text", "TTS", "STT", or similar audio tasks.
metadata:
  author: fal-ai
  version: "1.0.0"
---

# fal.ai Audio

Text-to-speech and speech-to-text using state-of-the-art audio models on fal.ai.

## How It Works

1. User provides text (for TTS) or audio URL (for STT)
2. Script selects appropriate model
3. Sends request to fal.ai API
4. Returns audio URL (TTS) or transcription text (STT)

## Finding Models

To discover the best and latest audio models, use the search API:

```bash
# Search for text-to-speech models
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --category "text-to-speech"

# Search for speech-to-text models
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --category "speech-to-text"

# Search for music generation models
bash /mnt/skills/user/fal-generate/scripts/search-models.sh --query "music generation"
```

Or use the `search_models` MCP tool with relevant keywords like "tts", "speech", "music".

## Usage

### Text-to-Speech

```bash
bash /mnt/skills/user/fal-audio/scripts/text-to-speech.sh [options]
```

**Arguments:**
- `--text` - Text to convert to speech (required)
- `--model` - TTS model (defaults to `fal-ai/minimax/speech-2.8-turbo`)
- `--voice` - Voice ID or name (model-specific)

**Examples:**

```bash
# Basic TTS (fast, good quality)
bash /mnt/skills/user/fal-audio/scripts/text-to-speech.sh \
  --text "Hello, welcome to the future of AI."

# High quality with MiniMax HD
bash /mnt/skills/user/fal-audio/scripts/text-to-speech.sh \
  --text "This is premium quality speech." \
  --model "fal-ai/minimax/speech-2.8-hd"

# Natural voices with ElevenLabs
bash /mnt/skills/user/fal-audio/scripts/text-to-speech.sh \
  --text "Natural sounding voice generation" \
  --model "fal-ai/elevenlabs/tts/eleven-v3"

# Multi-language TTS
bash /mnt/skills/user/fal-audio/scripts/text-to-speech.sh \
  --text "Bonjour, bienvenue dans le futur." \
  --model "fal-ai/chatterbox/text-to-speech/multilingual"
```

### Speech-to-Text

```bash
bash /mnt/skills/user/fal-audio/scripts/speech-to-text.sh [options]
```

**Arguments:**
- `--audio-url` - URL of audio file to transcribe (required)
- `--model` - STT model (defaults to `fal-ai/whisper`)
- `--language` - Language code (optional, auto-detected)

**Examples:**

```bash
# Transcribe with Whisper
bash /mnt/skills/user/fal-audio/scripts/speech-to-text.sh \
  --audio-url "https://example.com/audio.mp3"

# Transcribe with speaker diarization
bash /mnt/skills/user/fal-audio/scripts/speech-to-text.sh \
  --audio-url "https://example.com/meeting.mp3" \
  --model "fal-ai/elevenlabs/speech-to-text/scribe-v2"

# Transcribe specific language
bash /mnt/skills/user/fal-audio/scripts/speech-to-text.sh \
  --audio-url "https://example.com/spanish.mp3" \
  --language "es"
```

## MCP Tool Alternative

Use `search_models` MCP tool or `search-models.sh` to find the best current model, then call `mcp__fal-ai__generate` with the discovered `modelId`.

## Output

### Text-to-Speech Output
```
Generating speech...
Model: fal-ai/minimax/speech-2.8-turbo

Speech generated!

Audio URL: https://v3.fal.media/files/abc123/speech.mp3
Duration: 5.2s
```

### Speech-to-Text Output
```
Transcribing audio...
Model: fal-ai/whisper

Transcription complete!

Text: "Hello, this is the transcribed text from the audio file."
Duration: 12.5s
Language: en
```

## Present Results to User

### For TTS:
```
Here's the generated speech:

[Download audio](https://v3.fal.media/files/.../speech.mp3)

• Duration: 5.2s | Model: Maya TTS
```

### For STT:
```
Here's the transcription:

"Hello, this is the transcribed text from the audio file."

• Duration: 12.5s | Language: English
```

## Model Selection Tips

- **Text-to-Speech**: Search for `text-to-speech` category. Consider quality vs speed tradeoffs.
- **Text-to-Music**: Search for `music generation`. Some models specialize in vocals, others in instrumental.
- **Speech-to-Text**: Search for `speech-to-text` category. Consider whether you need speaker diarization or multi-language support.

## Troubleshooting

### Empty Audio
```
Error: Generated audio is empty

Check that your text is not empty and contains valid content.
```

### Unsupported Audio Format
```
Error: Audio format not supported

Supported formats: MP3, WAV, M4A, FLAC, OGG
Convert your audio to a supported format.
```

### Language Detection Failed
```
Warning: Could not detect language, defaulting to English

Specify the language explicitly with --language option.
```
