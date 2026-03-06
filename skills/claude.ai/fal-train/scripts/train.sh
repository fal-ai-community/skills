#!/bin/bash
set -e

# train.sh — Submit a LoRA training job to fal.ai

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL="fal-ai/flux-lora-fast-training"
IMAGES_URL=""
TRIGGER_WORD=""
STEPS=1000
CHECK_STATUS=false
ENDPOINT=""
REQUEST_ID=""
EXTRA_PARAMS=""

show_help() {
  echo "Usage: $0 --images-url URL --trigger-word WORD [options]"
  echo "       $0 --status --endpoint MODEL --request-id ID"
  echo ""
  echo "Options:"
  echo "  --images-url URL      URL to zip of training images (required)"
  echo "  --trigger-word WORD   Trigger word for the LoRA (required)"
  echo "  --model, -m MODEL     Training model (default: $MODEL)"
  echo "  --steps N             Training steps (default: $STEPS)"
  echo "  --status              Check training job status"
  echo "  --endpoint MODEL      Endpoint for status check"
  echo "  --request-id ID       Request ID for status check"
  echo "  --param KEY=VALUE     Extra parameter (repeatable)"
  echo "  --add-fal-key KEY     Store FAL_KEY in .env"
  echo "  --help, -h            Show this help"
  exit 0
}

[ -f "$SCRIPT_DIR/../.env" ] && source "$SCRIPT_DIR/../.env"
[ -f ".env" ] && source ".env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --images-url) IMAGES_URL="$2"; shift 2;;
    --trigger-word) TRIGGER_WORD="$2"; shift 2;;
    --model|-m) MODEL="$2"; shift 2;;
    --steps) STEPS="$2"; shift 2;;
    --status) CHECK_STATUS=true; shift;;
    --endpoint) ENDPOINT="$2"; shift 2;;
    --request-id) REQUEST_ID="$2"; shift 2;;
    --param) EXTRA_PARAMS="$EXTRA_PARAMS \"$(echo "$2" | cut -d= -f1)\": \"$(echo "$2" | cut -d= -f2)\","; shift 2;;
    --add-fal-key) echo "FAL_KEY=$2" > .env; echo "API key saved." >&2; exit 0;;
    --help|-h) show_help;;
    *) echo "Unknown: $1" >&2; exit 1;;
  esac
done

if [ -z "$FAL_KEY" ]; then echo "Error: FAL_KEY not set." >&2; exit 1; fi

# Status check mode
if [ "$CHECK_STATUS" = true ]; then
  if [ -z "$ENDPOINT" ] || [ -z "$REQUEST_ID" ]; then
    echo "Error: --endpoint and --request-id required for --status" >&2; exit 1
  fi
  curl -s "https://queue.fal.run/$ENDPOINT/requests/$REQUEST_ID/status?logs=1" \
    -H "Authorization: Key $FAL_KEY" | jq .
  exit 0
fi

# Training mode
if [ -z "$IMAGES_URL" ]; then echo "Error: --images-url required" >&2; exit 1; fi
if [ -z "$TRIGGER_WORD" ]; then echo "Error: --trigger-word required" >&2; exit 1; fi

PAYLOAD=$(cat <<EOF
{
  "images_data_url": "$IMAGES_URL",
  "trigger_word": "$TRIGGER_WORD",
  "steps": $STEPS,
  $EXTRA_PARAMS
  "is_style": false
}
EOF
)

echo "Submitting training to $MODEL..." >&2
echo "  Images: $IMAGES_URL" >&2
echo "  Trigger: $TRIGGER_WORD" >&2
echo "  Steps: $STEPS" >&2

SUBMIT=$(curl -s -X POST "https://queue.fal.run/$MODEL" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

REQ_ID=$(echo "$SUBMIT" | jq -r '.request_id // empty')
if [ -z "$REQ_ID" ]; then echo "Error: $SUBMIT" >&2; exit 1; fi

echo "" >&2
echo "Training submitted!" >&2
echo "Request ID: $REQ_ID" >&2
echo "" >&2
echo "Training takes 5-30 minutes. Check status with:" >&2
echo "  $0 --status --endpoint $MODEL --request-id $REQ_ID" >&2
echo "" >&2
echo "$REQ_ID"
