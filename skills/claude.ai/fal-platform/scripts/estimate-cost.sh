#!/bin/bash

# fal.ai Cost Estimation Script
# Usage: ./estimate-cost.sh --model MODEL --calls N | --units N
# Returns estimated costs based on pricing data

set -e

FAL_API_BASE="https://api.fal.ai/v1"

# Default values
MODEL=""
CALLS=""
UNITS=""
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
            MODEL="$2"
            shift 2
            ;;
        --calls|-c)
            CALLS="$2"
            shift 2
            ;;
        --units|-u)
            UNITS="$2"
            shift 2
            ;;
        --json)
            OUTPUT_JSON=true
            shift
            ;;
        --help|-h)
            echo "fal.ai Cost Estimation Script" >&2
            echo "" >&2
            echo "Usage:" >&2
            echo "  ./estimate-cost.sh --model MODEL --calls N    Estimate by API calls" >&2
            echo "  ./estimate-cost.sh --model MODEL --units N    Estimate by units" >&2
            echo "" >&2
            echo "Options:" >&2
            echo "  --model, -m   Model ID (required)" >&2
            echo "  --calls, -c   Number of API calls to estimate" >&2
            echo "  --units, -u   Number of billing units to estimate" >&2
            echo "  --json        Output raw JSON" >&2
            echo "  --add-fal-key Setup FAL_KEY" >&2
            echo "" >&2
            echo "Examples:" >&2
            echo "  ./estimate-cost.sh --model \"fal-ai/flux/dev\" --calls 100" >&2
            echo "  ./estimate-cost.sh --model \"fal-ai/kling-video/v2/master/text-to-video\" --units 60" >&2
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

if [ -z "$MODEL" ]; then
    echo "Error: --model is required" >&2
    exit 1
fi

if [ -z "$CALLS" ] && [ -z "$UNITS" ]; then
    echo "Error: --calls or --units is required" >&2
    exit 1
fi

echo "Estimating cost for $MODEL..." >&2

# Get pricing info first
ENCODED_MODEL=$(echo "$MODEL" | sed 's/\//%2F/g')

PRICING_RESPONSE=$(curl -s -X GET "$FAL_API_BASE/models/pricing?endpoint_id=$ENCODED_MODEL" \
    -H "Authorization: Key $FAL_KEY" \
    -H "Content-Type: application/json")

# Check for errors
if echo "$PRICING_RESPONSE" | grep -q '"error"'; then
    ERROR_MSG=$(echo "$PRICING_RESPONSE" | grep -o '"message":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Error: $ERROR_MSG" >&2
    exit 1
fi

# Calculate estimate
QUANTITY="${CALLS:-$UNITS}"
ESTIMATE_TYPE="calls"
if [ -n "$UNITS" ]; then
    ESTIMATE_TYPE="units"
fi

echo "" >&2
if command -v python3 &> /dev/null; then
    python3 << PYTHON_EOF - "$PRICING_RESPONSE" "$MODEL" "$QUANTITY" "$ESTIMATE_TYPE"
import json
import sys

response = json.loads(sys.argv[1])
model = sys.argv[2]
quantity = float(sys.argv[3])
estimate_type = sys.argv[4]

print(f"Cost Estimate: {model}", file=sys.stderr)
print("=" * (len(model) + 15), file=sys.stderr)
print("", file=sys.stderr)

# Extract pricing data
prices = response.get('prices', [response] if isinstance(response, dict) else response)
if isinstance(prices, list) and len(prices) > 0:
    price_info = prices[0]
    unit_price = float(price_info.get('unit_price', 0))
    unit = price_info.get('unit', 'call')
    currency = price_info.get('currency', 'USD')

    # Calculate estimated cost
    estimated_cost = unit_price * quantity

    print(f"  Unit Price: {unit_price} {currency} per {unit}", file=sys.stderr)
    print(f"  Quantity: {quantity:.0f} {estimate_type}", file=sys.stderr)
    print(f"  Estimated Cost: {estimated_cost:.4f} {currency}", file=sys.stderr)

    # Output JSON
    result = {
        "model": model,
        "unit_price": unit_price,
        "unit": unit,
        "quantity": quantity,
        "estimated_cost": estimated_cost,
        "currency": currency
    }
    print(json.dumps(result))
else:
    print("  Unable to calculate estimate - pricing data not found", file=sys.stderr)
    print(json.dumps({"error": "pricing data not found"}))
PYTHON_EOF
else
    echo "  Python3 required for calculation" >&2
fi
