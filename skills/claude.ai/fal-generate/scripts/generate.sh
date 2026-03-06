#!/bin/bash

# fal.ai Generation Script with Queue Support
# Usage: ./generate.sh --prompt "..." [--model MODEL] [options]
# Returns: JSON with generated media URLs
#
# Queue Mode (default): Submits to queue, polls for completion
# Async Mode: Returns request_id immediately
# Sync Mode: Direct request (not recommended for long tasks)

set -e

FAL_QUEUE_ENDPOINT="https://queue.fal.run"
FAL_SYNC_ENDPOINT="https://fal.run"
FAL_TOKEN_ENDPOINT="https://rest.alpha.fal.ai/storage/auth/token?storage_type=fal-cdn-v3"

# Default values
MODEL="fal-ai/nano-banana-pro"
PROMPT=""
IMAGE_URL=""
IMAGE_FILE=""
IMAGE_SIZE="landscape_4_3"
NUM_IMAGES=1
MODE="queue"  # queue (default), async, sync
REQUEST_ID=""
ACTION="generate"  # generate, status, result, cancel
POLL_INTERVAL=2
MAX_POLL_TIME=600
LIFECYCLE=""
SHOW_LOGS=false

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
        --prompt|-p)
            PROMPT="$2"
            shift 2
            ;;
        --model|-m)
            MODEL="$2"
            shift 2
            ;;
        --image-url)
            IMAGE_URL="$2"
            shift 2
            ;;
        --file|--image)
            IMAGE_FILE="$2"
            shift 2
            ;;
        --size)
            case $2 in
                square) IMAGE_SIZE="square" ;;
                portrait) IMAGE_SIZE="portrait_4_3" ;;
                landscape) IMAGE_SIZE="landscape_4_3" ;;
                *) IMAGE_SIZE="$2" ;;
            esac
            shift 2
            ;;
        --num-images)
            NUM_IMAGES="$2"
            shift 2
            ;;
        # Mode options
        --async)
            MODE="async"
            shift
            ;;
        --sync)
            MODE="sync"
            shift
            ;;
        --logs)
            SHOW_LOGS=true
            shift
            ;;
        # Queue operations
        --status)
            ACTION="status"
            REQUEST_ID="$2"
            shift 2
            ;;
        --result)
            ACTION="result"
            REQUEST_ID="$2"
            shift 2
            ;;
        --cancel)
            ACTION="cancel"
            REQUEST_ID="$2"
            shift 2
            ;;
        # Polling options
        --poll-interval)
            POLL_INTERVAL="$2"
            shift 2
            ;;
        --timeout)
            MAX_POLL_TIME="$2"
            shift 2
            ;;
        # Object lifecycle (optional)
        --lifecycle)
            LIFECYCLE="$2"
            shift 2
            ;;
        # Schema lookup
        --schema)
            SCHEMA_MODEL="${2:-$MODEL}"
            ENCODED=$(echo "$SCHEMA_MODEL" | sed 's/\//%2F/g')
            echo "Fetching schema for $SCHEMA_MODEL..." >&2
            curl -s "https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=$ENCODED"
            exit 0
            ;;
        --help|-h)
            echo "fal.ai Generation Script (Queue-based)" >&2
            echo "" >&2
            echo "Usage:" >&2
            echo "  ./generate.sh --prompt \"...\" [options]" >&2
            echo "" >&2
            echo "Generation Options:" >&2
            echo "  --prompt, -p    Text description (required for generate)" >&2
            echo "  --model, -m     Model ID (default: fal-ai/nano-banana-pro)" >&2
            echo "  --image-url     Input image URL for I2V models" >&2
            echo "  --file, --image Local file (auto-uploads to fal CDN)" >&2
            echo "  --size          square, portrait, landscape" >&2
            echo "  --num-images    Number of images (default: 1)" >&2
            echo "" >&2
            echo "Mode Options:" >&2
            echo "  (default)       Queue mode - submit and poll until complete" >&2
            echo "  --async         Submit to queue, return request_id immediately" >&2
            echo "  --sync          Synchronous request (not recommended for video)" >&2
            echo "  --logs          Show generation logs while polling" >&2
            echo "" >&2
            echo "Queue Operations:" >&2
            echo "  --status ID     Check status of a queued request" >&2
            echo "  --result ID     Get result of a completed request" >&2
            echo "  --cancel ID     Cancel a queued request" >&2
            echo "" >&2
            echo "Advanced Options:" >&2
            echo "  --poll-interval Seconds between status checks (default: 2)" >&2
            echo "  --timeout       Max seconds to wait (default: 600)" >&2
            echo "  --lifecycle N   Object expiration in seconds (optional)" >&2
            echo "  --schema [MODEL] Get OpenAPI schema for model" >&2
            echo "  --add-fal-key   Setup FAL_KEY in .env" >&2
            echo "" >&2
            echo "Examples:" >&2
            echo "  # Generate image (waits for completion)" >&2
            echo "  ./generate.sh --prompt \"a sunset\" --model \"fal-ai/nano-banana-pro\"" >&2
            echo "" >&2
            echo "  # Generate video async (returns immediately)" >&2
            echo "  ./generate.sh --prompt \"ocean waves\" --model \"fal-ai/veo3\" --async" >&2
            echo "" >&2
            echo "  # Check status" >&2
            echo "  ./generate.sh --status \"request_id\" --model \"fal-ai/veo3\"" >&2
            echo "" >&2
            echo "  # Get result" >&2
            echo "  ./generate.sh --result \"request_id\" --model \"fal-ai/veo3\"" >&2
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# Validate FAL_KEY
if [ -z "$FAL_KEY" ]; then
    echo "Error: FAL_KEY not set" >&2
    echo "" >&2
    echo "Run: ./generate.sh --add-fal-key" >&2
    echo "Or:  export FAL_KEY=your_key_here" >&2
    exit 1
fi

# Handle local file upload
if [ -n "$IMAGE_FILE" ]; then
    if [ ! -f "$IMAGE_FILE" ]; then
        echo "Error: File not found: $IMAGE_FILE" >&2
        exit 1
    fi

    FILENAME=$(basename "$IMAGE_FILE")
    EXTENSION="${FILENAME##*.}"
    EXTENSION_LOWER=$(echo "$EXTENSION" | tr '[:upper:]' '[:lower:]')

    # Detect content type
    case "$EXTENSION_LOWER" in
        jpg|jpeg) CONTENT_TYPE="image/jpeg" ;;
        png) CONTENT_TYPE="image/png" ;;
        gif) CONTENT_TYPE="image/gif" ;;
        webp) CONTENT_TYPE="image/webp" ;;
        mp4) CONTENT_TYPE="video/mp4" ;;
        mov) CONTENT_TYPE="video/quicktime" ;;
        *) CONTENT_TYPE="application/octet-stream" ;;
    esac

    echo "Uploading $FILENAME..." >&2

    # Step 1: Get CDN token
    TOKEN_RESPONSE=$(curl -s -X POST "$FAL_TOKEN_ENDPOINT" \
        -H "Authorization: Key $FAL_KEY" \
        -H "Content-Type: application/json" \
        -d '{}')

    CDN_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    CDN_TOKEN_TYPE=$(echo "$TOKEN_RESPONSE" | grep -o '"token_type":"[^"]*"' | cut -d'"' -f4)
    CDN_BASE_URL=$(echo "$TOKEN_RESPONSE" | grep -o '"base_url":"[^"]*"' | cut -d'"' -f4)

    if [ -z "$CDN_TOKEN" ] || [ -z "$CDN_BASE_URL" ]; then
        echo "Error: Failed to get CDN token" >&2
        exit 1
    fi

    # Step 2: Upload file
    UPLOAD_RESPONSE=$(curl -s -X POST "${CDN_BASE_URL}/files/upload" \
        -H "Authorization: $CDN_TOKEN_TYPE $CDN_TOKEN" \
        -H "Content-Type: $CONTENT_TYPE" \
        -H "X-Fal-File-Name: $FILENAME" \
        --data-binary "@$IMAGE_FILE")

    # Check for upload error
    if echo "$UPLOAD_RESPONSE" | grep -q '"error"'; then
        ERROR_MSG=$(echo "$UPLOAD_RESPONSE" | grep -o '"message":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo "Upload error: $ERROR_MSG" >&2
        exit 1
    fi

    # Extract URL
    IMAGE_URL=$(echo "$UPLOAD_RESPONSE" | grep -o '"access_url":"[^"]*"' | cut -d'"' -f4)

    if [ -z "$IMAGE_URL" ]; then
        echo "Error: Failed to get URL from upload response" >&2
        exit 1
    fi

    echo "Uploaded: $IMAGE_URL" >&2
fi

# Build headers
HEADERS=(-H "Authorization: Key $FAL_KEY" -H "Content-Type: application/json")

# Add lifecycle header if specified
if [ -n "$LIFECYCLE" ]; then
    HEADERS+=(-H "X-Fal-Object-Lifecycle-Preference: {\"expiration_duration_seconds\": $LIFECYCLE}")
fi

# Handle queue operations
case $ACTION in
    status)
        if [ -z "$REQUEST_ID" ]; then
            echo "Error: Request ID required for --status" >&2
            exit 1
        fi
        LOGS_PARAM=""
        if [ "$SHOW_LOGS" = true ]; then
            LOGS_PARAM="?logs=1"
        fi
        echo "Checking status for $REQUEST_ID..." >&2
        RESPONSE=$(curl -s -X GET "$FAL_QUEUE_ENDPOINT/$MODEL/requests/$REQUEST_ID/status$LOGS_PARAM" "${HEADERS[@]}")

        # Parse and display status
        STATUS=$(echo "$RESPONSE" | grep -oE '"status"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*: *"//' | sed 's/"$//')
        echo "Status: $STATUS" >&2

        if [ "$STATUS" = "IN_QUEUE" ]; then
            POSITION=$(echo "$RESPONSE" | grep -o '"queue_position":[0-9]*' | cut -d':' -f2)
            [ -n "$POSITION" ] && echo "Queue position: $POSITION" >&2
        fi

        echo "$RESPONSE"
        exit 0
        ;;
    result)
        if [ -z "$REQUEST_ID" ]; then
            echo "Error: Request ID required for --result" >&2
            exit 1
        fi
        echo "Getting result for $REQUEST_ID..." >&2
        RESPONSE=$(curl -s -X GET "$FAL_QUEUE_ENDPOINT/$MODEL/requests/$REQUEST_ID" "${HEADERS[@]}")

        # Check for error
        if echo "$RESPONSE" | grep -q '"error"'; then
            ERROR_MSG=$(echo "$RESPONSE" | grep -o '"message":"[^"]*"' | head -1 | cut -d'"' -f4)
            echo "Error: $ERROR_MSG" >&2
            exit 1
        fi

        # Extract URL
        if echo "$RESPONSE" | grep -q '"video"'; then
            URL=$(echo "$RESPONSE" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)
            echo "Video URL: $URL" >&2
        elif echo "$RESPONSE" | grep -q '"images"'; then
            URL=$(echo "$RESPONSE" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)
            echo "Image URL: $URL" >&2
        fi

        echo "$RESPONSE"
        exit 0
        ;;
    cancel)
        if [ -z "$REQUEST_ID" ]; then
            echo "Error: Request ID required for --cancel" >&2
            exit 1
        fi
        echo "Cancelling request $REQUEST_ID..." >&2
        RESPONSE=$(curl -s -X PUT "$FAL_QUEUE_ENDPOINT/$MODEL/requests/$REQUEST_ID/cancel" "${HEADERS[@]}")
        echo "$RESPONSE"
        exit 0
        ;;
esac

# Generate action requires prompt
if [ -z "$PROMPT" ]; then
    echo "Error: --prompt is required" >&2
    exit 1
fi

# Build the request payload based on model type
if [[ "$MODEL" == *"image-to-video"* ]] || [[ "$MODEL" == *"i2v"* ]]; then
    if [ -z "$IMAGE_URL" ]; then
        echo "Error: --image-url is required for image-to-video models" >&2
        exit 1
    fi
    PAYLOAD=$(cat <<EOF
{"prompt": "$PROMPT", "image_url": "$IMAGE_URL"}
EOF
)
elif [[ "$MODEL" == *"video"* ]] || [[ "$MODEL" == *"veo"* ]] || [[ "$MODEL" == *"text-to-video"* ]]; then
    PAYLOAD=$(cat <<EOF
{"prompt": "$PROMPT"}
EOF
)
else
    PAYLOAD=$(cat <<EOF
{"prompt": "$PROMPT", "image_size": "$IMAGE_SIZE", "num_images": $NUM_IMAGES}
EOF
)
fi

# Synchronous mode
if [ "$MODE" = "sync" ]; then
    echo "Generating with $MODEL (sync mode)..." >&2
    RESPONSE=$(curl -s -X POST "$FAL_SYNC_ENDPOINT/$MODEL" "${HEADERS[@]}" -d "$PAYLOAD")

    if echo "$RESPONSE" | grep -q '"error"'; then
        ERROR_MSG=$(echo "$RESPONSE" | grep -o '"message":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo "Error: $ERROR_MSG" >&2
        exit 1
    fi

    echo "Generation complete!" >&2
    if echo "$RESPONSE" | grep -q '"video"'; then
        URL=$(echo "$RESPONSE" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo "Video URL: $URL" >&2
    elif echo "$RESPONSE" | grep -q '"images"'; then
        URL=$(echo "$RESPONSE" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo "Image URL: $URL" >&2
    fi

    echo "$RESPONSE"
    exit 0
fi

# Queue mode (async or poll)
echo "Submitting to queue: $MODEL..." >&2

SUBMIT_RESPONSE=$(curl -s -X POST "$FAL_QUEUE_ENDPOINT/$MODEL" "${HEADERS[@]}" -d "$PAYLOAD")

# Check for submit error
if echo "$SUBMIT_RESPONSE" | grep -q '"error"'; then
    ERROR_MSG=$(echo "$SUBMIT_RESPONSE" | grep -o '"message":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Error: $ERROR_MSG" >&2
    exit 1
fi

# Extract request_id and URLs (handle both "key": "value" and "key":"value" formats)
REQUEST_ID=$(echo "$SUBMIT_RESPONSE" | grep -oE '"request_id"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*: *"//' | sed 's/"$//')
STATUS_URL=$(echo "$SUBMIT_RESPONSE" | grep -oE '"status_url"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*: *"//' | sed 's/"$//')
RESPONSE_URL=$(echo "$SUBMIT_RESPONSE" | grep -oE '"response_url"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*: *"//' | sed 's/"$//')
CANCEL_URL=$(echo "$SUBMIT_RESPONSE" | grep -oE '"cancel_url"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*: *"//' | sed 's/"$//')

if [ -z "$REQUEST_ID" ]; then
    echo "Error: Failed to get request_id" >&2
    echo "$SUBMIT_RESPONSE" >&2
    exit 1
fi

echo "Request ID: $REQUEST_ID" >&2

# Async mode - return immediately
if [ "$MODE" = "async" ]; then
    echo "" >&2
    echo "Request submitted. Use these commands to check:" >&2
    echo "  Status: ./generate.sh --status \"$REQUEST_ID\" --model \"$MODEL\"" >&2
    echo "  Result: ./generate.sh --result \"$REQUEST_ID\" --model \"$MODEL\"" >&2
    echo "  Cancel: ./generate.sh --cancel \"$REQUEST_ID\" --model \"$MODEL\"" >&2
    echo "$SUBMIT_RESPONSE"
    exit 0
fi

# Queue mode - poll until complete
echo "Waiting for completion..." >&2

ELAPSED=0
LAST_STATUS=""

while [ $ELAPSED -lt $MAX_POLL_TIME ]; do
    sleep $POLL_INTERVAL
    ELAPSED=$((ELAPSED + POLL_INTERVAL))

    LOGS_PARAM=""
    if [ "$SHOW_LOGS" = true ]; then
        LOGS_PARAM="?logs=1"
    fi

    STATUS_RESPONSE=$(curl -s -X GET "${STATUS_URL}${LOGS_PARAM}" "${HEADERS[@]}")
    STATUS=$(echo "$STATUS_RESPONSE" | grep -oE '"status"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*: *"//' | sed 's/"$//')

    # Show status change
    if [ "$STATUS" != "$LAST_STATUS" ]; then
        case $STATUS in
            IN_QUEUE)
                POSITION=$(echo "$STATUS_RESPONSE" | grep -o '"queue_position":[0-9]*' | cut -d':' -f2)
                echo "Status: IN_QUEUE (position: ${POSITION:-?})" >&2
                ;;
            IN_PROGRESS)
                echo "Status: IN_PROGRESS" >&2
                ;;
            COMPLETED)
                echo "Status: COMPLETED" >&2
                ;;
            *)
                echo "Status: $STATUS" >&2
                ;;
        esac
        LAST_STATUS="$STATUS"
    fi

    # Show logs if enabled
    if [ "$SHOW_LOGS" = true ]; then
        LOGS=$(echo "$STATUS_RESPONSE" | grep -o '"logs":\[[^]]*\]' | head -1)
        if [ -n "$LOGS" ] && [ "$LOGS" != "[]" ]; then
            echo "$LOGS" | tr ',' '\n' | grep -o '"message":"[^"]*"' | cut -d'"' -f4 | while read -r log; do
                echo "  > $log" >&2
            done
        fi
    fi

    if [ "$STATUS" = "COMPLETED" ]; then
        break
    fi

    if [ "$STATUS" = "FAILED" ]; then
        echo "Error: Generation failed" >&2
        echo "$STATUS_RESPONSE"
        exit 1
    fi
done

if [ "$STATUS" != "COMPLETED" ]; then
    echo "Error: Timeout after ${MAX_POLL_TIME}s" >&2
    echo "Request ID: $REQUEST_ID" >&2
    echo "Check status with: ./generate.sh --status \"$REQUEST_ID\" --model \"$MODEL\"" >&2
    exit 1
fi

# Get final result
echo "Fetching result..." >&2
RESULT=$(curl -s -X GET "$RESPONSE_URL" "${HEADERS[@]}")

# Check for error in result
if echo "$RESULT" | grep -q '"error"'; then
    ERROR_MSG=$(echo "$RESULT" | grep -o '"message":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Error: $ERROR_MSG" >&2
    exit 1
fi

echo "" >&2
echo "Generation complete!" >&2

# Extract and display URL
if echo "$RESULT" | grep -q '"video"'; then
    URL=$(echo "$RESULT" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Video URL: $URL" >&2
elif echo "$RESULT" | grep -q '"images"'; then
    URL=$(echo "$RESULT" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Image URL: $URL" >&2
fi

# Output JSON
echo "$RESULT"
