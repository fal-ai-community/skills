#!/bin/bash

# fal.ai Text-to-Speech Script
# Usage: ./text-to-speech.sh --text "..." [--model MODEL] [--voice VOICE]
# Returns: JSON with audio URL

set -e

FAL_API_ENDPOINT="https://fal.run"

# Default values
MODEL="fal-ai/minimax/speech-2.8-turbo"
TEXT=""
VOICE=""

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
        --text)
            TEXT="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --voice)
            VOICE="$2"
            shift 2
            ;;
        --help|-h)
            echo "fal.ai Text-to-Speech Script" >&2
            echo "" >&2
            echo "Usage:" >&2
            echo "  ./text-to-speech.sh --text \"...\" [options]" >&2
            echo "" >&2
            echo "Options:" >&2
            echo "  --text          Text to convert (required)" >&2
            echo "  --model         Model ID (default: fal-ai/minimax/speech-2.8-turbo)" >&2
            echo "  --voice         Voice ID (model-specific)" >&2
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
    echo "Run: ./text-to-speech.sh --add-fal-key" >&2
    echo "Or:  export FAL_KEY=your_key_here" >&2
    exit 1
fi

if [ -z "$TEXT" ]; then
    echo "Error: --text is required" >&2
    exit 1
fi

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "Generating speech..." >&2
echo "Model: $MODEL" >&2
echo "" >&2

# Build payload
if [ -n "$VOICE" ]; then
    PAYLOAD=$(cat <<EOF
{
  "text": "$TEXT",
  "voice": "$VOICE"
}
EOF
)
else
    PAYLOAD=$(cat <<EOF
{
  "text": "$TEXT"
}
EOF
)
fi

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

echo "Speech generated!" >&2
echo "" >&2

# Extract audio URL
AUDIO_URL=$(echo "$RESPONSE" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "Audio URL: $AUDIO_URL" >&2

# Output JSON for programmatic use
echo "$RESPONSE"
