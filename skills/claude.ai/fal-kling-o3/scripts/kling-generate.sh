#!/bin/bash
set -e

# kling-generate.sh — Generate images with Kling O3

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL="fal-ai/kling-image/o3/text-to-image"
PROMPT=""
ASPECT_RATIO="1:1"
EXTRA_PARAMS=""

show_help() {
  echo "Usage: $0 --prompt TEXT [options]"
  echo ""
  echo "Options:"
  echo "  --prompt, -p TEXT       Image description (required)"
  echo "  --aspect-ratio RATIO    1:1, 16:9, 9:16, 4:3, 3:4 (default: 1:1)"
  echo "  --param KEY=VALUE       Extra parameter (repeatable)"
  echo "  --add-fal-key KEY       Store FAL_KEY in .env"
  echo "  --help, -h              Show this help"
  exit 0
}

[ -f "$SCRIPT_DIR/../.env" ] && source "$SCRIPT_DIR/../.env"
[ -f ".env" ] && source ".env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt|-p) PROMPT="$2"; shift 2;;
    --aspect-ratio) ASPECT_RATIO="$2"; shift 2;;
    --param) EXTRA_PARAMS="$EXTRA_PARAMS, \"$(echo "$2" | cut -d= -f1)\": \"$(echo "$2" | cut -d= -f2)\""; shift 2;;
    --add-fal-key) echo "FAL_KEY=$2" > .env; echo "API key saved." >&2; exit 0;;
    --help|-h) show_help;;
    *) echo "Unknown: $1" >&2; exit 1;;
  esac
done

if [ -z "$FAL_KEY" ]; then echo "Error: FAL_KEY not set." >&2; exit 1; fi
if [ -z "$PROMPT" ]; then echo "Error: --prompt required" >&2; exit 1; fi

PAYLOAD="{\"prompt\": \"$PROMPT\", \"aspect_ratio\": \"$ASPECT_RATIO\"$EXTRA_PARAMS}"

echo "Generating with Kling O3 Image..." >&2
SUBMIT=$(curl -s -X POST "https://queue.fal.run/$MODEL" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

REQUEST_ID=$(echo "$SUBMIT" | jq -r '.request_id // empty')
if [ -z "$REQUEST_ID" ]; then echo "Error: $SUBMIT" >&2; exit 1; fi

echo "Waiting (request: $REQUEST_ID)..." >&2
ELAPSED=0
TIMEOUT=300
POLL=3
while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
  STATUS=$(curl -s "https://queue.fal.run/$MODEL/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY")
  STATE=$(echo "$STATUS" | jq -r '.status')
  case "$STATE" in
    COMPLETED)
      echo "Done!" >&2
      curl -s "https://queue.fal.run/$MODEL/requests/$REQUEST_ID" \
        -H "Authorization: Key $FAL_KEY" | jq .
      exit 0;;
    FAILED) echo "Failed: $STATUS" >&2; exit 1;;
    *) echo "  $STATE (${ELAPSED}s)" >&2;;
  esac
  sleep "$POLL"
  ELAPSED=$((ELAPSED + POLL))
done
echo "Timed out. Request: $REQUEST_ID" >&2; exit 1
