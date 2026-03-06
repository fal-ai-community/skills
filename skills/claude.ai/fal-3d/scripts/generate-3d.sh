#!/bin/bash
set -e

# generate-3d.sh — Generate a 3D model from text or image

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL="fal-ai/hunyuan3d-v3/image-to-3d"
IMAGE_URL=""
PROMPT=""
EXTRA_PARAMS=""
POLL_INTERVAL=5
TIMEOUT=600

show_help() {
  echo "Usage: $0 [--image-url URL | --prompt TEXT] [options]"
  echo ""
  echo "Options:"
  echo "  --image-url URL    Image to convert to 3D"
  echo "  --prompt, -p TEXT  Text description for text-to-3D"
  echo "  --model, -m MODEL  Model (default: $MODEL)"
  echo "  --param KEY=VALUE  Extra parameter (repeatable)"
  echo "  --add-fal-key KEY  Store FAL_KEY in .env"
  echo "  --help, -h         Show this help"
  exit 0
}

[ -f "$SCRIPT_DIR/../.env" ] && source "$SCRIPT_DIR/../.env"
[ -f ".env" ] && source ".env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --image-url) IMAGE_URL="$2"; shift 2;;
    --prompt|-p) PROMPT="$2"; shift 2;;
    --model|-m) MODEL="$2"; shift 2;;
    --param) EXTRA_PARAMS="$EXTRA_PARAMS, \"$(echo "$2" | cut -d= -f1)\": \"$(echo "$2" | cut -d= -f2)\""; shift 2;;
    --add-fal-key) echo "FAL_KEY=$2" > .env; echo "API key saved." >&2; exit 0;;
    --help|-h) show_help;;
    *) echo "Unknown: $1" >&2; exit 1;;
  esac
done

if [ -z "$FAL_KEY" ]; then echo "Error: FAL_KEY not set." >&2; exit 1; fi
if [ -z "$IMAGE_URL" ] && [ -z "$PROMPT" ]; then echo "Error: --image-url or --prompt required" >&2; exit 1; fi

# Build payload
if [ -n "$IMAGE_URL" ]; then
  PAYLOAD="{\"image_url\": \"$IMAGE_URL\"$EXTRA_PARAMS}"
else
  PAYLOAD="{\"prompt\": \"$PROMPT\"$EXTRA_PARAMS}"
fi

echo "Submitting 3D generation to $MODEL..." >&2
SUBMIT=$(curl -s -X POST "https://queue.fal.run/$MODEL" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

REQUEST_ID=$(echo "$SUBMIT" | jq -r '.request_id // empty')
if [ -z "$REQUEST_ID" ]; then echo "Error: $SUBMIT" >&2; exit 1; fi

echo "Waiting (request: $REQUEST_ID) — 3D generation takes 1-5 min..." >&2
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
    FAILED) echo "Failed: $STATUS" >&2; exit 1;;
    *) echo "  $STATE (${ELAPSED}s)" >&2;;
  esac
  sleep "$POLL_INTERVAL"
  ELAPSED=$((ELAPSED + POLL_INTERVAL))
done
echo "Timed out. Request ID: $REQUEST_ID" >&2; exit 1
