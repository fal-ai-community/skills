#!/bin/bash
set -e

# analyze.sh — Analyze an image (segment, detect, OCR, describe, QA)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
IMAGE_URL=""
OPERATION=""
QUERY=""
MODEL=""

show_help() {
  echo "Usage: $0 --image-url URL --operation OP [--query TEXT] [options]"
  echo ""
  echo "Operations: segment, detect, ocr, describe, qa"
  echo ""
  echo "Options:"
  echo "  --image-url URL     Image URL (required)"
  echo "  --operation OP      Operation to perform (required)"
  echo "  --query, -q TEXT    Query text (for segment/qa)"
  echo "  --model, -m MODEL   Override model endpoint"
  echo "  --add-fal-key KEY   Store FAL_KEY in .env"
  echo "  --help, -h          Show this help"
  exit 0
}

[ -f "$SCRIPT_DIR/../.env" ] && source "$SCRIPT_DIR/../.env"
[ -f ".env" ] && source ".env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --image-url) IMAGE_URL="$2"; shift 2;;
    --operation) OPERATION="$2"; shift 2;;
    --query|-q) QUERY="$2"; shift 2;;
    --model|-m) MODEL="$2"; shift 2;;
    --add-fal-key) echo "FAL_KEY=$2" > .env; echo "API key saved." >&2; exit 0;;
    --help|-h) show_help;;
    *) echo "Unknown: $1" >&2; exit 1;;
  esac
done

if [ -z "$FAL_KEY" ]; then echo "Error: FAL_KEY not set." >&2; exit 1; fi
if [ -z "$IMAGE_URL" ]; then echo "Error: --image-url required" >&2; exit 1; fi
if [ -z "$OPERATION" ]; then echo "Error: --operation required" >&2; exit 1; fi

# Auto-select model
if [ -z "$MODEL" ]; then
  case "$OPERATION" in
    segment) MODEL="fal-ai/sam-3/image";;
    detect) MODEL="fal-ai/florence-2-large/object-detection";;
    ocr) MODEL="fal-ai/got-ocr/v2";;
    describe) MODEL="fal-ai/florence-2-large/detailed-caption";;
    qa) MODEL="fal-ai/llava-next";;
    *) echo "Error: Unknown operation: $OPERATION" >&2; exit 1;;
  esac
fi

# Build payload
case "$OPERATION" in
  segment)
    if [ -n "$QUERY" ]; then
      PAYLOAD="{\"image_url\": \"$IMAGE_URL\", \"text_prompt\": \"$QUERY\"}"
    else
      PAYLOAD="{\"image_url\": \"$IMAGE_URL\"}"
    fi;;
  qa)
    QUERY="${QUERY:-What is in this image?}"
    PAYLOAD="{\"image_url\": \"$IMAGE_URL\", \"prompt\": \"$QUERY\"}";;
  *)
    PAYLOAD="{\"image_url\": \"$IMAGE_URL\"}";;
esac

echo "Running $OPERATION with $MODEL..." >&2
RESULT=$(curl -s -X POST "https://fal.run/$MODEL" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

if echo "$RESULT" | jq -e '.error' > /dev/null 2>&1; then
  echo "Error: $RESULT" >&2; exit 1
fi

echo "$RESULT" | jq .
