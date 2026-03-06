#!/bin/bash
set -e

# edit-video.sh — Edit, remix, upscale, or remove background from a video

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VIDEO_URL=""
PROMPT=""
OPERATION=""
MODEL=""
POLL_INTERVAL=3
TIMEOUT=600

show_help() {
  echo "Usage: $0 --video-url URL --operation OP [--prompt TEXT] [options]"
  echo ""
  echo "Operations: remix, edit, upscale, remove-bg"
  echo ""
  echo "Options:"
  echo "  --video-url URL       Video URL (required)"
  echo "  --operation OP        Operation to perform (required)"
  echo "  --prompt, -p TEXT     Instructions/style description (for remix/edit)"
  echo "  --model, -m MODEL     Override model endpoint"
  echo "  --add-fal-key KEY     Store FAL_KEY in .env"
  echo "  --help, -h            Show this help"
  exit 0
}

[ -f "$SCRIPT_DIR/../.env" ] && source "$SCRIPT_DIR/../.env"
[ -f ".env" ] && source ".env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --video-url) VIDEO_URL="$2"; shift 2;;
    --prompt|-p) PROMPT="$2"; shift 2;;
    --operation) OPERATION="$2"; shift 2;;
    --model|-m) MODEL="$2"; shift 2;;
    --add-fal-key) echo "FAL_KEY=$2" > .env; echo "API key saved." >&2; exit 0;;
    --help|-h) show_help;;
    *) echo "Unknown: $1" >&2; exit 1;;
  esac
done

if [ -z "$FAL_KEY" ]; then echo "Error: FAL_KEY not set." >&2; exit 1; fi
if [ -z "$VIDEO_URL" ]; then echo "Error: --video-url required" >&2; exit 1; fi
if [ -z "$OPERATION" ]; then echo "Error: --operation required (remix/edit/upscale/remove-bg)" >&2; exit 1; fi

# Auto-select model based on operation
if [ -z "$MODEL" ]; then
  case "$OPERATION" in
    remix) MODEL="fal-ai/kling-video/o3/standard/video-to-video/reference";;
    edit) MODEL="fal-ai/kling-video/o3/standard/video-to-video/edit";;
    upscale) MODEL="fal-ai/topaz/upscale/video";;
    remove-bg) MODEL="bria/video/background-removal";;
    *) echo "Error: Unknown operation: $OPERATION" >&2; exit 1;;
  esac
fi

# Build payload based on operation
case "$OPERATION" in
  remix|edit)
    if [ -z "$PROMPT" ]; then echo "Error: --prompt required for $OPERATION" >&2; exit 1; fi
    PAYLOAD="{\"video_url\": \"$VIDEO_URL\", \"prompt\": \"$PROMPT\"}";;
  upscale|remove-bg)
    PAYLOAD="{\"video_url\": \"$VIDEO_URL\"}";;
esac

echo "Submitting $OPERATION to $MODEL..." >&2
SUBMIT=$(curl -s -X POST "https://queue.fal.run/$MODEL" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

REQUEST_ID=$(echo "$SUBMIT" | jq -r '.request_id // empty')
if [ -z "$REQUEST_ID" ]; then echo "Error: $SUBMIT" >&2; exit 1; fi

echo "Waiting (request: $REQUEST_ID)..." >&2
ELAPSED=0
while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
  STATUS=$(curl -s "https://queue.fal.run/$MODEL/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY")
  STATE=$(echo "$STATUS" | jq -r '.status')
  case "$STATE" in
    COMPLETED)
      echo "Completed!" >&2
      curl -s "https://queue.fal.run/$MODEL/requests/$REQUEST_ID" \
        -H "Authorization: Key $FAL_KEY" | jq .
      exit 0;;
    FAILED) echo "Failed: $STATUS" >&2; exit 1;;
    *) echo "  $STATE (${ELAPSED}s)" >&2;;
  esac
  sleep "$POLL_INTERVAL"
  ELAPSED=$((ELAPSED + POLL_INTERVAL))
done
echo "Timed out. Request ID: $REQUEST_ID" >&2; exit 1
