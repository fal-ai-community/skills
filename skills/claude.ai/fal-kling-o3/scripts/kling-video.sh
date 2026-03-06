#!/bin/bash
set -e

# kling-video.sh — Generate or edit videos with Kling O3

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPT=""
MODE=""
IMAGE_URL=""
VIDEO_URL=""
TIER="pro"
EXTRA_PARAMS=""
POLL_INTERVAL=5
TIMEOUT=600

show_help() {
  echo "Usage: $0 --mode MODE --prompt TEXT [options]"
  echo ""
  echo "Modes: text-to-video, image-to-video, edit, remix"
  echo ""
  echo "Options:"
  echo "  --prompt, -p TEXT     Description or edit instructions (required)"
  echo "  --mode MODE           Generation mode (required)"
  echo "  --image-url URL       Image for image-to-video"
  echo "  --video-url URL       Video for edit/remix"
  echo "  --tier TIER           standard or pro (default: pro)"
  echo "  --param KEY=VALUE     Extra parameter (repeatable)"
  echo "  --add-fal-key KEY     Store FAL_KEY in .env"
  echo "  --help, -h            Show this help"
  exit 0
}

[ -f "$SCRIPT_DIR/../.env" ] && source "$SCRIPT_DIR/../.env"
[ -f ".env" ] && source ".env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt|-p) PROMPT="$2"; shift 2;;
    --mode) MODE="$2"; shift 2;;
    --image-url) IMAGE_URL="$2"; shift 2;;
    --video-url) VIDEO_URL="$2"; shift 2;;
    --tier) TIER="$2"; shift 2;;
    --param) EXTRA_PARAMS="$EXTRA_PARAMS, \"$(echo "$2" | cut -d= -f1)\": \"$(echo "$2" | cut -d= -f2)\""; shift 2;;
    --add-fal-key) echo "FAL_KEY=$2" > .env; echo "API key saved." >&2; exit 0;;
    --help|-h) show_help;;
    *) echo "Unknown: $1" >&2; exit 1;;
  esac
done

if [ -z "$FAL_KEY" ]; then echo "Error: FAL_KEY not set." >&2; exit 1; fi
if [ -z "$MODE" ]; then echo "Error: --mode required (text-to-video/image-to-video/edit/remix)" >&2; exit 1; fi
if [ -z "$PROMPT" ]; then echo "Error: --prompt required" >&2; exit 1; fi

# Select endpoint based on mode and tier
case "$MODE" in
  text-to-video)
    MODEL="fal-ai/kling-video/o3/$TIER/text-to-video"
    PAYLOAD="{\"prompt\": \"$PROMPT\"$EXTRA_PARAMS}";;
  image-to-video)
    if [ -z "$IMAGE_URL" ]; then echo "Error: --image-url required for image-to-video" >&2; exit 1; fi
    MODEL="fal-ai/kling-video/o3/$TIER/image-to-video"
    PAYLOAD="{\"prompt\": \"$PROMPT\", \"image_url\": \"$IMAGE_URL\"$EXTRA_PARAMS}";;
  edit)
    if [ -z "$VIDEO_URL" ]; then echo "Error: --video-url required for edit" >&2; exit 1; fi
    MODEL="fal-ai/kling-video/o3/$TIER/video-to-video/edit"
    PAYLOAD="{\"prompt\": \"$PROMPT\", \"video_url\": \"$VIDEO_URL\"$EXTRA_PARAMS}";;
  remix)
    if [ -z "$VIDEO_URL" ]; then echo "Error: --video-url required for remix" >&2; exit 1; fi
    MODEL="fal-ai/kling-video/o3/$TIER/video-to-video/reference"
    PAYLOAD="{\"prompt\": \"$PROMPT\", \"video_url\": \"$VIDEO_URL\"$EXTRA_PARAMS}";;
  *)
    echo "Error: Unknown mode: $MODE" >&2; exit 1;;
esac

echo "Submitting $MODE ($TIER) to $MODEL..." >&2
SUBMIT=$(curl -s -X POST "https://queue.fal.run/$MODEL" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

REQUEST_ID=$(echo "$SUBMIT" | jq -r '.request_id // empty')
if [ -z "$REQUEST_ID" ]; then echo "Error: $SUBMIT" >&2; exit 1; fi

echo "Waiting (request: $REQUEST_ID)..." >&2
ELAPSED=0
while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
  STATUS=$(curl -s "https://queue.fal.run/$MODEL/requests/$REQUEST_ID/status?logs=1" \
    -H "Authorization: Key $FAL_KEY")
  STATE=$(echo "$STATUS" | jq -r '.status')
  case "$STATE" in
    COMPLETED)
      echo "Done!" >&2
      curl -s "https://queue.fal.run/$MODEL/requests/$REQUEST_ID" \
        -H "Authorization: Key $FAL_KEY" | jq .
      exit 0;;
    FAILED) echo "Failed!" >&2; echo "$STATUS" | jq . >&2; exit 1;;
    IN_QUEUE)
      POS=$(echo "$STATUS" | jq -r '.queue_position // "?"')
      echo "  Queue position: $POS (${ELAPSED}s)" >&2;;
    IN_PROGRESS)
      LOG=$(echo "$STATUS" | jq -r '.logs[-1].message // empty')
      echo "  Processing${LOG:+: $LOG} (${ELAPSED}s)" >&2;;
  esac
  sleep "$POLL_INTERVAL"
  ELAPSED=$((ELAPSED + POLL_INTERVAL))
done
echo "Timed out after ${TIMEOUT}s. Request: $REQUEST_ID" >&2; exit 1
