#!/bin/bash
set -e

# realtime.sh — Real-time image generation (sub-second)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL="fal-ai/flux-2/klein/realtime"
PROMPT=""
SIZE="square"
SEED=""
LORA_URL=""
LORA_SCALE=""
NUM_IMAGES=1

show_help() {
  echo "Usage: $0 --prompt TEXT [options]"
  echo ""
  echo "Options:"
  echo "  --prompt, -p TEXT       Image description (required)"
  echo "  --model, -m MODEL       Model (default: $MODEL)"
  echo "  --size SIZE             square, landscape, portrait (default: square)"
  echo "  --seed N                Random seed for reproducibility"
  echo "  --lora-url URL          LoRA weights URL"
  echo "  --lora-scale N          LoRA scale 0.0-1.0 (default: 1.0)"
  echo "  --num-images N          Number of images (default: 1)"
  echo "  --add-fal-key KEY       Store FAL_KEY in .env"
  echo "  --help, -h              Show this help"
  exit 0
}

[ -f "$SCRIPT_DIR/../.env" ] && source "$SCRIPT_DIR/../.env"
[ -f ".env" ] && source ".env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt|-p) PROMPT="$2"; shift 2;;
    --model|-m) MODEL="$2"; shift 2;;
    --size) SIZE="$2"; shift 2;;
    --seed) SEED="$2"; shift 2;;
    --lora-url) LORA_URL="$2"; shift 2;;
    --lora-scale) LORA_SCALE="$2"; shift 2;;
    --num-images) NUM_IMAGES="$2"; shift 2;;
    --add-fal-key) echo "FAL_KEY=$2" > .env; echo "API key saved." >&2; exit 0;;
    --help|-h) show_help;;
    *) echo "Unknown: $1" >&2; exit 1;;
  esac
done

if [ -z "$FAL_KEY" ]; then echo "Error: FAL_KEY not set." >&2; exit 1; fi
if [ -z "$PROMPT" ]; then echo "Error: --prompt required" >&2; exit 1; fi

# Map size to dimensions
case "$SIZE" in
  square) IMAGE_SIZE="{\"width\": 1024, \"height\": 1024}";;
  landscape) IMAGE_SIZE="{\"width\": 1344, \"height\": 768}";;
  portrait) IMAGE_SIZE="{\"width\": 768, \"height\": 1344}";;
  *) IMAGE_SIZE="{\"width\": 1024, \"height\": 1024}";;
esac

# Build payload
PAYLOAD="{\"prompt\": \"$PROMPT\", \"image_size\": $IMAGE_SIZE, \"num_images\": $NUM_IMAGES"
if [ -n "$SEED" ]; then PAYLOAD="$PAYLOAD, \"seed\": $SEED"; fi
if [ -n "$LORA_URL" ]; then
  SCALE="${LORA_SCALE:-1.0}"
  PAYLOAD="$PAYLOAD, \"loras\": [{\"path\": \"$LORA_URL\", \"scale\": $SCALE}]"
fi
PAYLOAD="$PAYLOAD}"

# Real-time = synchronous API (no queue)
echo "Generating (real-time)..." >&2
START_TIME=$(date +%s%N 2>/dev/null || date +%s)

RESULT=$(curl -s -X POST "https://fal.run/$MODEL" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

END_TIME=$(date +%s%N 2>/dev/null || date +%s)

if echo "$RESULT" | jq -e '.error' > /dev/null 2>&1; then
  echo "Error: $RESULT" >&2; exit 1
fi

# Calculate duration (nanoseconds if available, else seconds)
if [ ${#START_TIME} -gt 10 ]; then
  DURATION_MS=$(( (END_TIME - START_TIME) / 1000000 ))
  echo "Generated in ${DURATION_MS}ms" >&2
else
  DURATION_S=$((END_TIME - START_TIME))
  echo "Generated in ${DURATION_S}s" >&2
fi

echo "$RESULT" | jq .
