---
name: fal-platform
description: fal.ai Platform APIs for model management, pricing, usage tracking, and cost estimation. Use when user asks "show pricing", "check usage", "estimate cost", "setup fal", "add API key", or platform management tasks.
metadata:
  author: fal-ai
  version: "1.0.0"
---

# fal.ai Platform

Platform APIs for model management, pricing, usage tracking, and cost estimation.

## Scripts

| Script | Purpose |
|--------|---------|
| `setup.sh` | Setup FAL_KEY and configuration |
| `pricing.sh` | Get model pricing information |
| `usage.sh` | Check usage and billing |
| `estimate-cost.sh` | Estimate costs for operations |
| `requests.sh` | List and manage requests |

## Setup & Configuration

### Add FAL_KEY

```bash
# Interactive setup
bash /mnt/skills/user/fal-platform/scripts/setup.sh --add-fal-key

# Set key directly
bash /mnt/skills/user/fal-platform/scripts/setup.sh --add-fal-key "your_key_here"

# Show current config
bash /mnt/skills/user/fal-platform/scripts/setup.sh --show-config
```

This adds FAL_KEY to your `.env` file for persistent use.

## Model Pricing

Get pricing for any model:

```bash
# Single model pricing
bash /mnt/skills/user/fal-platform/scripts/pricing.sh --model "fal-ai/flux/dev"

# Multiple models
bash /mnt/skills/user/fal-platform/scripts/pricing.sh --model "fal-ai/flux/dev,fal-ai/kling-video/v2/master/text-to-video"

# All pricing for a category
bash /mnt/skills/user/fal-platform/scripts/pricing.sh --category "text-to-image"
```

**Output:**
```
fal-ai/flux/dev
  Price: $0.025 per image
  Unit: image

fal-ai/kling-video/v2/master/text-to-video
  Price: $0.50 per second
  Unit: video_second
```

## Usage Tracking

Check your usage and spending:

```bash
# Current period usage
bash /mnt/skills/user/fal-platform/scripts/usage.sh

# Filter by model
bash /mnt/skills/user/fal-platform/scripts/usage.sh --model "fal-ai/flux/dev"

# Date range
bash /mnt/skills/user/fal-platform/scripts/usage.sh --start "2024-01-01" --end "2024-01-31"

# Specific timeframe
bash /mnt/skills/user/fal-platform/scripts/usage.sh --timeframe "day"
```

**Timeframes:** `minute`, `hour`, `day`, `week`, `month`

## Estimate Cost

Estimate costs before running:

```bash
# Estimate by API calls (historical pricing)
bash /mnt/skills/user/fal-platform/scripts/estimate-cost.sh \
  --model "fal-ai/flux/dev" \
  --calls 100

# Estimate by units
bash /mnt/skills/user/fal-platform/scripts/estimate-cost.sh \
  --model "fal-ai/kling-video/v2/master/text-to-video" \
  --units 60 \
  --type "unit_price"
```

**Output:**
```
Cost Estimate for fal-ai/flux/dev
  Quantity: 100 calls
  Estimated Cost: $2.50
```

## Request Management

List and manage requests:

```bash
# List recent requests
bash /mnt/skills/user/fal-platform/scripts/requests.sh --model "fal-ai/flux/dev" --limit 10

# Delete request payloads (cleanup)
bash /mnt/skills/user/fal-platform/scripts/requests.sh --delete "request_id_here"
```

## API Endpoints Reference

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Model Search | `GET /models` | GET |
| Pricing | `GET /models/pricing` | GET |
| Usage | `GET /models/usage` | GET |
| List Requests | `GET /models/requests/by-endpoint` | GET |
| Delete Payloads | `DELETE /models/requests/{id}/payloads` | DELETE |

**Base URL:** `https://api.fal.ai/v1`

## Common Flags (All Scripts)

All scripts support these common flags:

```bash
--add-fal-key [KEY]   # Add/update FAL_KEY in .env
--help, -h            # Show help
--json                # Output raw JSON
--quiet, -q           # Suppress status messages
```

## Troubleshooting

### API Key Required
```
Error: FAL_KEY required for this operation

Run: bash /mnt/skills/user/fal-platform/scripts/setup.sh --add-fal-key
```

### Permission Denied
```
Error: API key doesn't have permission for this operation

Some operations require admin API keys. Check your key permissions at:
https://fal.ai/dashboard/keys
```
