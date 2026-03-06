#!/bin/bash
set -e

# talking-head.sh — Generate a talking head video from portrait + audio/text

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL="veed/fabric-1.0"
TTS_MODEL="fal-ai/minimax/speech-2.6-turbo"
IMAGE_URL=""
AUDIO_URL=""
TEXT=""
ASYNC=false
POLL_INTERVAL=3
TIMEOUT=600

show_help() {
  echo "Usage: $0 --image-url URL [--audio-url URL | --text TEXT] [options]"
  echo ""
  echo "Options:"
  echo "  --image-url URL    Portrait/face image URL (required)"
  echo "  --audio-url URL    Audio URL to sync (required, or use --text)"
  echo "  --text TEXT         Text to speak (auto TTS, alternative to --audio-url)"
  echo "  --model, -m MODEL  Model endpoint (default: $MODEL)"
  echo "  --tts-model MODEL  TTS model for --text mode (default: $TTS_MODEL)"
  echo "  --async, -a        Return request ID immediately"
  echo "  --poll-interval N  Seconds between polls (default: $POLL_INTERVAL)"
  echo "  --timeout N        Max wait seconds (default: $TIMEOUT)"
  echo "  --add-fal-key KEY  Store FAL_KEY in .env"
  echo "  --help, -h         Show this help"
  exit 0
}

# Load env
[ -f "$SCRIPT_DIR/../.env" ] && source "$SCRIPT_DIR/../.env"
[ -f ".env" ] && source ".env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --image-url) IMAGE_URL="$2"; shift 2;;
    --audio-url) AUDIO_URL="$2"; shift 2;;
    --text) TEXT="$2"; shift 2;;
    --model|-m) MODEL="$2"; shift 2;;
    --tts-model) TTS_MODEL="$2"; shift 2;;
    --async|-a) ASYNC=true; shift;;
    --poll-interval) POLL_INTERVAL="$2"; shift 2;;
    --timeout) TIMEOUT="$2"; shift 2;;
    --add-fal-key) echo "FAL_KEY=$2" > .env; echo "API key saved." >&2; exit 0;;
    --help|-h) show_help;;
    *) echo "Unknown: $1" >&2; exit 1;;
  esac
done

if [ -z "$FAL_KEY" ]; then echo "Error: FAL_KEY not set. Use --add-fal-key or set FAL_KEY env var." >&2; exit 1; fi
if [ -z "$IMAGE_URL" ]; then echo "Error: --image-url is required" >&2; exit 1; fi
if [ -z "$AUDIO_URL" ] && [ -z "$TEXT" ]; then echo "Error: --audio-url or --text is required" >&2; exit 1; fi

# If text mode, generate TTS first
if [ -n "$TEXT" ] && [ -z "$AUDIO_URL" ]; then
  echo "Generating TTS audio..." >&2
  TTS_PAYLOAD=$(cat <<EOF
{"text": "$TEXT"}
EOF
)
  TTS_RESULT=$(curl -s -X POST "https://fal.run/$TTS_MODEL" \
    -H "Authorization: Key $FAL_KEY" \
    -H "Content-Type: application/json" \
    -d "$TTS_PAYLOAD")

  AUDIO_URL=$(echo "$TTS_RESULT" | jq -r '.audio.url // .audio_url.url // .url // empty')
  if [ -z "$AUDIO_URL" ]; then
    echo "Error: TTS failed: $TTS_RESULT" >&2; exit 1
  fi
  echo "TTS audio: $AUDIO_URL" >&2
fi

# Build payload
PAYLOAD=$(cat <<EOF
{"image_url": "$IMAGE_URL", "audio_url": "$AUDIO_URL"}
EOF
)

# Submit to queue
echo "Submitting to $MODEL..." >&2
SUBMIT=$(curl -s -X POST "https://queue.fal.run/$MODEL" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

REQUEST_ID=$(echo "$SUBMIT" | jq -r '.request_id // empty')
if [ -z "$REQUEST_ID" ]; then
  echo "Error: Submit failed: $SUBMIT" >&2; exit 1
fi

if [ "$ASYNC" = true ]; then
  echo "$REQUEST_ID"
  exit 0
fi

# Poll for completion
echo "Waiting for completion (request: $REQUEST_ID)..." >&2
ELAPSED=0
while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
  STATUS=$(curl -s "https://queue.fal.run/$MODEL/requests/$REQUEST_ID/status?logs=1" \
    -H "Authorization: Key $FAL_KEY")

  STATE=$(echo "$STATUS" | jq -r '.status')
  case "$STATE" in
    COMPLETED)
      echo "Completed!" >&2
      curl -s "https://queue.fal.run/$MODEL/requests/$REQUEST_ID" \
        -H "Authorization: Key $FAL_KEY" | jq .
      exit 0;;
    FAILED)
      echo "Failed!" >&2; echo "$STATUS" | jq . >&2; exit 1;;
    IN_QUEUE)
      POS=$(echo "$STATUS" | jq -r '.queue_position // "?"')
      echo "  Queue position: $POS (${ELAPSED}s elapsed)" >&2;;
    IN_PROGRESS)
      echo "  Processing... (${ELAPSED}s elapsed)" >&2;;
  esac
  sleep "$POLL_INTERVAL"
  ELAPSED=$((ELAPSED + POLL_INTERVAL))
done

echo "Error: Timed out after ${TIMEOUT}s. Request ID: $REQUEST_ID" >&2
exit 1
