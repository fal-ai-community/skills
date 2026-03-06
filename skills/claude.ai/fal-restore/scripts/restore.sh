#!/bin/bash
set -e

# restore.sh — Restore image quality (deblur, denoise, dehaze, fix-face, document)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
IMAGE_URL=""
OPERATION=""
MODEL=""
FIDELITY=""

show_help() {
  echo "Usage: $0 --image-url URL --operation OP [options]"
  echo ""
  echo "Operations: deblur, denoise, dehaze, fix-face, document"
  echo ""
  echo "Options:"
  echo "  --image-url URL     Image URL (required)"
  echo "  --operation OP      Restoration operation (required)"
  echo "  --model, -m MODEL   Override model endpoint"
  echo "  --fidelity F        For fix-face: 0.0-1.0 (0=max quality, 1=faithful)"
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
    --model|-m) MODEL="$2"; shift 2;;
    --fidelity) FIDELITY="$2"; shift 2;;
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
    deblur) MODEL="fal-ai/nafnet/deblur";;
    denoise) MODEL="fal-ai/nafnet/denoise";;
    dehaze) MODEL="fal-ai/mix-dehaze-net";;
    fix-face) MODEL="fal-ai/codeformer";;
    document) MODEL="fal-ai/docres";;
    *) echo "Error: Unknown operation: $OPERATION" >&2; exit 1;;
  esac
fi

# Build payload
PAYLOAD="{\"image_url\": \"$IMAGE_URL\""
if [ "$OPERATION" = "fix-face" ] && [ -n "$FIDELITY" ]; then
  PAYLOAD="$PAYLOAD, \"fidelity\": $FIDELITY"
fi
PAYLOAD="$PAYLOAD}"

echo "Running $OPERATION with $MODEL..." >&2
RESULT=$(curl -s -X POST "https://fal.run/$MODEL" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

if echo "$RESULT" | jq -e '.error' > /dev/null 2>&1; then
  echo "Error: $RESULT" >&2; exit 1
fi

echo "$RESULT" | jq .
