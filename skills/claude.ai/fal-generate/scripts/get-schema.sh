#!/bin/bash

# fal.ai Model Schema Script
# Usage: ./get-schema.sh --model MODEL
# Returns: OpenAPI 3.0 schema for the model

set -e

FAL_SCHEMA_ENDPOINT="https://fal.ai/api/openapi/queue/openapi.json"

# Default values
MODEL=""
OUTPUT_JSON=false
SHOW_INPUT=false
SHOW_OUTPUT=false

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

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --model|-m)
            MODEL="$2"
            shift 2
            ;;
        --input|-i)
            SHOW_INPUT=true
            shift
            ;;
        --output|-o)
            SHOW_OUTPUT=true
            shift
            ;;
        --json)
            OUTPUT_JSON=true
            shift
            ;;
        --help|-h)
            echo "fal.ai Model Schema Script" >&2
            echo "" >&2
            echo "Usage:" >&2
            echo "  ./get-schema.sh --model MODEL [options]" >&2
            echo "" >&2
            echo "Options:" >&2
            echo "  --model, -m     Model ID (required)" >&2
            echo "  --input, -i     Show only input schema" >&2
            echo "  --output, -o    Show only output schema" >&2
            echo "  --json          Output raw JSON" >&2
            echo "  --add-fal-key   Setup FAL_KEY in .env" >&2
            echo "" >&2
            echo "Examples:" >&2
            echo "  ./get-schema.sh --model \"fal-ai/flux-pro/v1.1-ultra\"" >&2
            echo "  ./get-schema.sh --model \"fal-ai/kling-video/v2.6/pro/image-to-video\" --input" >&2
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$MODEL" ]; then
    echo "Error: --model is required" >&2
    exit 1
fi

# URL encode the model ID
ENCODED_MODEL=$(echo "$MODEL" | sed 's/\//%2F/g')

echo "Fetching schema for $MODEL..." >&2

# Fetch OpenAPI schema
RESPONSE=$(curl -s -X GET "$FAL_SCHEMA_ENDPOINT?endpoint_id=$ENCODED_MODEL" \
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

# Parse and display schema summary
if command -v python3 &> /dev/null; then
    python3 << 'PYTHON_EOF' - "$RESPONSE" "$MODEL" "$SHOW_INPUT" "$SHOW_OUTPUT"
import json
import sys

response = json.loads(sys.argv[1])
model = sys.argv[2]
show_input = sys.argv[3] == "true"
show_output = sys.argv[4] == "true"

# Get metadata
info = response.get('info', {})
metadata = info.get('x-fal-metadata', {})
schemas = response.get('components', {}).get('schemas', {})

print("", file=sys.stderr)
print(f"Model: {model}", file=sys.stderr)
print("=" * (len(model) + 7), file=sys.stderr)

# Category
category = metadata.get('category', 'unknown')
print(f"Category: {category}", file=sys.stderr)

# URLs
if metadata.get('playgroundUrl'):
    print(f"Playground: {metadata['playgroundUrl']}", file=sys.stderr)
if metadata.get('documentationUrl'):
    print(f"Docs: {metadata['documentationUrl']}", file=sys.stderr)

# Find input/output schemas
input_schema = None
output_schema = None

for name, schema in schemas.items():
    if 'Input' in name and name != 'QueueStatus':
        input_schema = schema
    elif 'Output' in name and name != 'QueueStatus':
        output_schema = schema

# Show input schema
if input_schema and (show_input or (not show_input and not show_output)):
    print("", file=sys.stderr)
    print("Input Parameters", file=sys.stderr)
    print("-" * 16, file=sys.stderr)

    props = input_schema.get('properties', {})
    required = input_schema.get('required', [])
    order = input_schema.get('x-fal-order-properties', list(props.keys()))

    for prop_name in order:
        if prop_name not in props:
            continue
        prop = props[prop_name]

        # Type
        prop_type = prop.get('type', 'any')
        if 'enum' in prop:
            prop_type = f"enum: {prop['enum']}"
        elif 'anyOf' in prop:
            types = [t.get('type', t.get('enum', ['?'])) for t in prop['anyOf']]
            prop_type = f"oneOf: {types}"

        # Required marker
        req_mark = "*" if prop_name in required else " "

        # Default value
        default = prop.get('default', '')
        default_str = f" (default: {default})" if default != '' else ""

        print(f"  {req_mark} {prop_name}: {prop_type}{default_str}", file=sys.stderr)

        # Description
        desc = prop.get('description', '')
        if desc:
            # Truncate long descriptions
            if len(desc) > 60:
                desc = desc[:57] + "..."
            print(f"      {desc}", file=sys.stderr)

# Show output schema
if output_schema and (show_output or (not show_input and not show_output)):
    print("", file=sys.stderr)
    print("Output Fields", file=sys.stderr)
    print("-" * 13, file=sys.stderr)

    props = output_schema.get('properties', {})
    order = output_schema.get('x-fal-order-properties', list(props.keys()))

    for prop_name in order:
        if prop_name not in props:
            continue
        prop = props[prop_name]

        prop_type = prop.get('type', 'any')
        if prop_type == 'array':
            items = prop.get('items', {})
            item_type = items.get('type', items.get('$ref', '').split('/')[-1])
            prop_type = f"array<{item_type}>"

        print(f"  {prop_name}: {prop_type}", file=sys.stderr)

print("", file=sys.stderr)
print("* = required parameter", file=sys.stderr)
PYTHON_EOF
fi

# Output full JSON for programmatic use
echo "$RESPONSE"
