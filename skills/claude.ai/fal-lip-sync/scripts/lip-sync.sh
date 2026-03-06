#!/bin/bash
set -e

# lip-sync.sh — Sync lips in existing video to new audio

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL="fal-ai/sync-lipsync/v2"
VIDEO_URL=""
AUDIO_URL=""
POLL_INTERVAL=3
TIMEOUT=600

show_help() {
  echo "Usage: $0 --video-url URL --audio-url URL [options]"
  echo ""
  echo "Options:"
  echo "  --video-url URL    Video to lip sync (required)"
  echo "  --audio-url URL    Audio to sync to (required)"
  echo "  --model, -m MODEL  Model endpoint (default: $MODEL)"
  echo "  --add-fal-key KEY  Store FAL_KEY in .env"
  echo "  --help, -h         Show this help"
  exit 0
}

[ -f "$SCRIPT_DIR/../.env" ] && source "$SCRIPT_DIR/../.env"
[ -f ".env" ] && source ".env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --video-url) VIDEO_URL="$2"; shift 2;;
    --audio-url) AUDIO_URL="$2"; shift 2;;
    --model|-m) MODEL="$2"; shift 2;;
    --add-fal-key) echo "FAL_KEY=$2" > .env; echo "API key saved." >&2; exit 0;;
    --help|-h) show_help;;
    *) echo "Unknown: $1" >&2; exit 1;;
  esac
done

if [ -z "$FAL_KEY" ]; then echo "Error: FAL_KEY not set." >&2; exit 1; fi
if [ -z "$VIDEO_URL" ]; then echo "Error: --video-url required" >&2; exit 1; fi
if [ -z "$AUDIO_URL" ]; then echo "Error: --audio-url required" >&2; exit 1; fi

PAYLOAD="{\"video_url\": \"$VIDEO_URL\", \"audio_url\": \"$AUDIO_URL\"}"

echo "Submitting lip sync to $MODEL..." >&2
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
