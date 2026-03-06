#!/bin/bash

# fal.ai Pricing Script
# Usage: ./pricing.sh --model MODEL [--category CATEGORY]
# Returns pricing information for models

set -e

FAL_API_BASE="https://api.fal.ai/v1"

# Default values
MODELS=""
CATEGORY=""
OUTPUT_JSON=false

# Check for --add-fal-key first
for arg in "$@"; do
    if [ "$arg" = "--add-fal-key" ]; then
        bash "$(dirname "$0")/setup.sh" "$@"
        exit $?
    fi
done

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --model|-m)
            MODELS="$2"
            shift 2
            ;;
        --category|-c)
            CATEGORY="$2"
            shift 2
            ;;
        --json)
            OUTPUT_JSON=true
            shift
            ;;
        --help|-h)
            echo "fal.ai Pricing Script" >&2
            echo "" >&2
            echo "Usage:" >&2
            echo "  ./pricing.sh --model MODEL           Get pricing for model(s)" >&2
            echo "  ./pricing.sh --category CATEGORY     Get pricing for category" >&2
            echo "" >&2
            echo "Options:" >&2
            echo "  --model, -m     Model ID(s), comma-separated" >&2
            echo "  --category, -c  Filter by category" >&2
            echo "  --json          Output raw JSON" >&2
            echo "  --add-fal-key   Setup FAL_KEY" >&2
            echo "" >&2
            echo "Examples:" >&2
            echo "  ./pricing.sh --model \"fal-ai/flux/dev\"" >&2
            echo "  ./pricing.sh --model \"fal-ai/flux/dev,fal-ai/kling-video/v2/master/text-to-video\"" >&2
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# Load .env if exists
if [ -f ".env" ]; then
    source .env 2>/dev/null || true
fi

# Check for FAL_KEY
if [ -z "$FAL_KEY" ]; then
    echo "Error: FAL_KEY required" >&2
    echo "" >&2
    echo "Run: ./setup.sh --add-fal-key" >&2
    exit 1
fi

if [ -z "$MODELS" ] && [ -z "$CATEGORY" ]; then
    echo "Error: --model or --category required" >&2
    exit 1
fi

echo "Fetching pricing information..." >&2

# Build endpoint URL
if [ -n "$MODELS" ]; then
    # URL encode the model IDs
    ENCODED_MODELS=$(echo "$MODELS" | sed 's/,/%2C/g' | sed 's/\//%2F/g')
    ENDPOINT="$FAL_API_BASE/models/pricing?endpoint_id=$ENCODED_MODELS"
else
    ENDPOINT="$FAL_API_BASE/models?category=$CATEGORY&include_pricing=true"
fi

# Make API request
RESPONSE=$(curl -s -X GET "$ENDPOINT" \
    -H "Authorization: Key $FAL_KEY" \
    -H "Content-Type: application/json")

# Check for errors
if echo "$RESPONSE" | grep -q '"error"'; then
    ERROR_MSG=$(echo "$RESPONSE" | grep -o '"message":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Error: $ERROR_MSG" >&2
    exit 1
fi

if [ "$OUTPUT_JSON" = true ]; then
    echo "$RESPONSE"
    exit 0
fi

# Parse and display pricing
echo "" >&2
if command -v python3 &> /dev/null; then
    python3 << 'PYTHON_EOF' - "$RESPONSE"
import json
import sys

response = json.loads(sys.argv[1])
data = response.get('data', response)

if isinstance(data, list):
    for item in data:
        endpoint = item.get('endpoint_id', 'Unknown')
        pricing = item.get('pricing', {})
        print(f"{endpoint}", file=sys.stderr)

        if pricing:
            price = pricing.get('price', 'N/A')
            unit = pricing.get('unit', 'call')
            print(f"  Price: ${price} per {unit}", file=sys.stderr)
        else:
            print(f"  Pricing: Not available", file=sys.stderr)
        print("", file=sys.stderr)
elif isinstance(data, dict):
    for endpoint, info in data.items():
        print(f"{endpoint}", file=sys.stderr)
        if isinstance(info, dict):
            price = info.get('price', info.get('unit_price', 'N/A'))
            unit = info.get('unit', info.get('billing_unit', 'call'))
            print(f"  Price: ${price} per {unit}", file=sys.stderr)
        print("", file=sys.stderr)
PYTHON_EOF
fi

echo "$RESPONSE"
