#!/bin/bash

# fal.ai Image Edit Script
# Usage: ./edit-image.sh --image-url URL --prompt "..." [--operation OP] [--mask-url URL] [--strength N]
# Returns: JSON with edited image URL

set -e

FAL_API_ENDPOINT="https://fal.run"

# Default values
IMAGE_URL=""
PROMPT=""
OPERATION="style"
MASK_URL=""
STRENGTH=0.75

# Check for --add-fal-key first
for arg in "$@"; do
    if [ "$arg" = "--add-fal-key" ]; then
        shift
        KEY_VALUE=""
        if [[ -n "$1" && ! "$1" =~ ^-- ]]; then
            KEY_VALUE="$1"
        fi
        if [ -z "$KEY_VALUE" ]; then
            echo "Enter your fal.ai API key:" >&2
            read -r KEY_VALUE
        fi
        if [ -n "$KEY_VALUE" ]; then
            grep -v "^FAL_KEY=" .env > .env.tmp 2>/dev/null || true
            mv .env.tmp .env 2>/dev/null || true
            echo "FAL_KEY=$KEY_VALUE" >> .env
            echo "FAL_KEY saved to .env" >&2
        fi
        exit 0
    fi
done

# Load .env if exists
if [ -f ".env" ]; then
    source .env 2>/dev/null || true
fi

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --image-url)
            IMAGE_URL="$2"
            shift 2
            ;;
        --prompt)
            PROMPT="$2"
            shift 2
            ;;
        --operation)
            OPERATION="$2"
            shift 2
            ;;
        --mask-url)
            MASK_URL="$2"
            shift 2
            ;;
        --strength)
            STRENGTH="$2"
            shift 2
            ;;
        --help|-h)
            echo "fal.ai Image Edit Script" >&2
            echo "" >&2
            echo "Usage:" >&2
            echo "  ./edit-image.sh --image-url URL --prompt \"...\" [options]" >&2
            echo "" >&2
            echo "Options:" >&2
            echo "  --image-url     Image URL to edit (required)" >&2
            echo "  --prompt        Edit description (required)" >&2
            echo "  --operation     Operation: style, remove, background, inpaint" >&2
            echo "  --mask-url      Mask URL (required for inpaint)" >&2
            echo "  --strength      Edit strength 0-1 (default: 0.75)" >&2
            echo "  --add-fal-key   Setup FAL_KEY in .env" >&2
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# Validate required inputs
if [ -z "$FAL_KEY" ]; then
    echo "Error: FAL_KEY not set" >&2
    echo "" >&2
    echo "Run: ./edit-image.sh --add-fal-key" >&2
    echo "Or:  export FAL_KEY=your_key_here" >&2
    exit 1
fi

if [ -z "$IMAGE_URL" ]; then
    echo "Error: --image-url is required" >&2
    exit 1
fi

if [ -z "$PROMPT" ]; then
    echo "Error: --prompt is required" >&2
    exit 1
fi

# Select model based on operation
case $OPERATION in
    style)
        MODEL="fal-ai/flux/dev/image-to-image"
        ;;
    remove)
        MODEL="bria/eraser"
        ;;
    background)
        MODEL="fal-ai/flux-pro/kontext"
        ;;
    inpaint)
        MODEL="fal-ai/flux-lora-fill"
        if [ -z "$MASK_URL" ]; then
            echo "Error: --mask-url is required for inpainting" >&2
            exit 1
        fi
        ;;
    *)
        echo "Unknown operation: $OPERATION" >&2
        echo "Supported: style, remove, background, inpaint" >&2
        exit 1
        ;;
esac

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "Editing image..." >&2
echo "Model: $MODEL" >&2
echo "Operation: $OPERATION" >&2
echo "" >&2

# Build payload based on operation
case $OPERATION in
    style)
        PAYLOAD=$(cat <<EOF
{
  "image_url": "$IMAGE_URL",
  "prompt": "$PROMPT",
  "strength": $STRENGTH
}
EOF
)
        ;;
    remove|background)
        PAYLOAD=$(cat <<EOF
{
  "image_url": "$IMAGE_URL",
  "prompt": "$PROMPT"
}
EOF
)
        ;;
    inpaint)
        PAYLOAD=$(cat <<EOF
{
  "image_url": "$IMAGE_URL",
  "mask_url": "$MASK_URL",
  "prompt": "$PROMPT"
}
EOF
)
        ;;
esac

# Make API request
RESPONSE=$(curl -s -X POST "$FAL_API_ENDPOINT/$MODEL" \
    -H "Authorization: Key $FAL_KEY" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

# Check for errors
if echo "$RESPONSE" | grep -q '"error"'; then
    ERROR_MSG=$(echo "$RESPONSE" | grep -o '"message":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -z "$ERROR_MSG" ]; then
        ERROR_MSG=$(echo "$RESPONSE" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
    fi
    echo "Error: $ERROR_MSG" >&2
    exit 1
fi

echo "Edit complete!" >&2
echo "" >&2

# Extract image URL
OUTPUT_URL=$(echo "$RESPONSE" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "Image URL: $OUTPUT_URL" >&2

# Output JSON for programmatic use
echo "$RESPONSE"
