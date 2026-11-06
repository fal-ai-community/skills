---
name: genmedia
description: "Run fal models from a terminal with the genmedia CLI. Use for model discovery, schemas, pricing, uploads, execution and request recovery. MCP hosts use fal-media instead."
---

# genmedia CLI: fal.ai endpoint runner

`genmedia` is the agent-first CLI for fal.ai. It works in a terminal for humans (pretty output) and equally well for agents (structured JSON when piped or with `--json`). All other skills in this repo call `genmedia` for execution, they do not wrap the fal.ai HTTP API directly.

For the full command surface (every flag, every option, every example), see [references/full-reference.md](references/full-reference.md).

## Critical rules

1. **Always use `--json` when an agent will read the output.** Pretty mode is for humans only.
2. **Prefer smart routing for default-quality requests.** `genmedia run "<prompt>"` (no endpoint, no `--prompt` needed) classifies the prompt and routes to a sensible default per modality. Only do explicit endpoint discovery when the user names a model, asks for a non-default behavior (specific style, quality tier, parameter), or the smart-route default is wrong for the task.
3. **Never invent endpoint IDs.** When you do need a specific endpoint, use `genmedia models "<query>"` to discover (auto-filters by inferred modality) and `genmedia models --endpoint_id <id>` to verify.
4. **Inspect schema before running with custom params.** `genmedia schema <endpoint_id> --json` shows the exact field names. Smart routing only needs `prompt`; explicit endpoints with custom params need a schema check first or guessed flags fail with 422.
5. **Save files with `--download`, not curl.** The CLI handles authentication, naming, and file format detection.
6. **Use `--async` for long-running generation.** Image work usually completes inline; video/audio/3D usually need queue + status polling.

## Command index

| Command | Purpose |
|---------|---------|
| `genmedia setup` | Configure API key, output mode, auto-update |
| `genmedia models <query>` | Search the catalog (or `--category`, or `--endpoint_id`) |
| `genmedia schema <endpoint_id>` | Inspect inputs/outputs (compact or `--format openapi`) |
| `genmedia run <endpoint_id> --<param> <value>` | Execute a model |
| `genmedia status <endpoint_id> <request_id>` | Poll an async job (with `--result`, `--logs`, `--cancel`, `--download`) |
| `genmedia upload <path-or-url>` | Upload a local file or remote URL to the fal.ai CDN |
| `genmedia pricing <endpoint_id>` | Check cost per call |
| `genmedia docs <query>` | Search fal.ai documentation |
| `genmedia init` | Install the default skill bundle into `.agents/skills/` or `.claude/skills/` |
| `genmedia skills <list|install|update|remove>` | Manage installed agent skills |
| `genmedia version` / `genmedia update` | Check or apply CLI updates |

## Quick patterns

### Smart routing (preferred for default-quality requests)

The CLI classifies the prompt by modality (image / video / music / tts / 3d) and picks a sensible default endpoint. The output includes a `routed` block so you can verify which endpoint actually ran.

```bash
genmedia run "a cat on the moon" --json
genmedia run "a 5-second clip of a robot dancing" --json
genmedia run "narrate this paragraph in a calm voice" --json
```

Override anytime with an explicit endpoint id (positional that contains `/`):

```bash
genmedia run fal-ai/flux/dev --prompt "a cat on the moon" --json
```

### Discover when the user names a fuzzy task or wants a specific endpoint

`genmedia models "<query>"` auto-applies `--category` from the same classifier the smart router uses, so the result list is focused on the right modality. Pass `--no-classify` to disable, or `--category <cat>` to override.

```bash
genmedia models "background removal product image" --json
genmedia models --category text-to-video --limit 5 --json
genmedia models "video models with character consistency" --no-classify --json
genmedia docs "webhook callbacks" --json
```

### Run a specific model and download the result

```bash
genmedia run fal-ai/flux/dev \
 --prompt "a cat on the moon" \
 --download "./out/{request_id}_{index}.{ext}" \
 --json
```

### Async + poll

```bash
SUBMIT=$(genmedia run fal-ai/veo3.1 --prompt "a dog running" --async --json)
REQ=$(echo "$SUBMIT" | jq -r '.request_id')
genmedia status fal-ai/veo3.1 "$REQ" \
 --download "./out/{request_id}_{index}.{ext}" \
 --json
```

Smart routing also works for async — the response includes `routed` and `endpoint_id` so you know which endpoint to poll on `status`:

```bash
SUBMIT=$(genmedia run "a 30-second video of waves" --async --json)
REQ=$(echo "$SUBMIT" | jq -r '.request_id')
EP=$(echo "$SUBMIT" | jq -r '.endpoint_id')
genmedia status "$EP" "$REQ" --download "./out/" --json
```

### Upload then run

```bash
URL=$(genmedia upload ./photo.jpg --json | jq -r '.url')
genmedia run fal-ai/nano-banana-pro/edit \
 --image_urls "$URL" \
 --prompt "make the sky stormy" \
 --download "./out/{request_id}_{index}.{ext}" \
 --json
```

## Setup (first-time only)

If `genmedia` is not installed:

```bash
curl https://genmedia.sh/install -fsS | bash # Linux / macOS
irm https://genmedia.sh/install.ps1 | iex # Windows PowerShell
genmedia setup --non-interactive --api-key "$FAL_KEY"
```

For full setup details (output modes, auto-update, `.env` loading) see [full-reference.md](references/full-reference.md).
