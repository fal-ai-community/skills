#!/bin/bash
set -e

# tryon.sh — Virtual try-on: apply garment onto person photo

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL="fal-ai/fashn/tryon/v1.5"
PERSON_URL=""
GARMENT_URL=""
TYPE=""
QUALITY="balanced"

show_help() {
  echo "Usage: $0 --person-url URL --garment-url URL [options]"
  echo ""
  echo "Options:"
  echo "  --person-url URL    Person/model photo URL (required)"
  echo "  --garment-url URL   Garment/clothing image URL (required)"
  echo "  --type TYPE         Garment type: top, bottom, full-body, dress"
  echo "  --quality Q         speed, balanced, quality (default: balanced)"
  echo "  --model, -m MODEL   Model (default: $MODEL)"
  echo "  --add-fal-key KEY   Store FAL_KEY in .env"
  echo "  --help, -h          Show this help"
  exit 0
}

[ -f "$SCRIPT_DIR/../.env" ] && source "$SCRIPT_DIR/../.env"
[ -f ".env" ] && source ".env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --person-url) PERSON_URL="$2"; shift 2;;
    --garment-url) GARMENT_URL="$2"; shift 2;;
    --type) TYPE="$2"; shift 2;;
    --quality) QUALITY="$2"; shift 2;;
    --model|-m) MODEL="$2"; shift 2;;
    --add-fal-key) echo "FAL_KEY=$2" > .env; echo "API key saved." >&2; exit 0;;
    --help|-h) show_help;;
    *) echo "Unknown: $1" >&2; exit 1;;
  esac
done

if [ -z "$FAL_KEY" ]; then echo "Error: FAL_KEY not set." >&2; exit 1; fi
if [ -z "$PERSON_URL" ]; then echo "Error: --person-url required" >&2; exit 1; fi
if [ -z "$GARMENT_URL" ]; then echo "Error: --garment-url required" >&2; exit 1; fi

PAYLOAD="{\"model_image\": \"$PERSON_URL\", \"garment_image\": \"$GARMENT_URL\""
if [ -n "$TYPE" ]; then PAYLOAD="$PAYLOAD, \"category\": \"$TYPE\""; fi
PAYLOAD="$PAYLOAD}"

echo "Running virtual try-on with $MODEL..." >&2
RESULT=$(curl -s -X POST "https://fal.run/$MODEL" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

if echo "$RESULT" | jq -e '.error' > /dev/null 2>&1; then
  echo "Error: $RESULT" >&2; exit 1
fi

echo "$RESULT" | jq .
