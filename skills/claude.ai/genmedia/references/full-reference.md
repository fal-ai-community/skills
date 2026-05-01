# genmedia: Full CLI Reference

Complete command surface. SKILL.md has the trigger surface and quick patterns; this file is the manual.

## Install

Linux / macOS:

```bash
curl https://genmedia.sh/install -fsS | bash
```

Windows (PowerShell):

```powershell
irm https://genmedia.sh/install.ps1 | iex
```

## setup: configure

Interactive wizard:

```bash
genmedia setup
```

Configures:

- **API key**: saved encrypted to local config (or skip and use `FAL_KEY` env var)
- **Auto-load `.env`**: automatically load `FAL_KEY` from a project `.env`
- **Output mode**: `auto` (pretty in TTY, JSON when piped), `json` (always structured), `standard` (always human-readable)
- **Automatic updates**: background check; `GENMEDIA_NO_UPDATE=1` to disable

Non-interactive (agents / CI):

```bash
genmedia setup --non-interactive --api-key "$FAL_KEY"
genmedia setup --non-interactive --output-format json --no-auto-load-env --auto-update
```

| Flag | Description |
|---|---|
| `--non-interactive`, `-y` | Skip all prompts. Required when there is no TTY. |
| `--api-key <key>` | API key to save. Pass `""` to clear the saved key. |
| `--no-save-key` | With `--api-key`, do not persist the key to `config.json` (use `FAL_KEY` at runtime instead). |
| `--output-format <auto\|json\|standard>` | Default output mode. |
| `--auto-load-env` / `--no-auto-load-env` | Toggle auto-loading `FAL_KEY` from a project `.env`. |
| `--auto-update` / `--no-auto-update` | Toggle background update checks. |

API keys: <https://fal.ai/dashboard/keys>.

## models: search and inspect

```bash
genmedia models "text to video"
genmedia models "flux" --category text-to-image
genmedia models --category text-to-speech --limit 5
genmedia models --status all # include deprecated
genmedia models --endpoint_id fal-ai/flux/dev,fal-ai/flux/schnell # specific models
genmedia models --endpoint_id fal-ai/flux/dev --expand openapi-3.0
genmedia models "flux" --cursor <token> # pagination
```

| Option | Description |
|---|---|
| `--category` | `text-to-image`, `image-to-video`, `text-to-speech`, etc. |
| `--status` | `active` (default), `deprecated`, `all` |
| `--limit` | Max results (default 20) |
| `--cursor` | Pagination token from a previous response |
| `--endpoint_id` | Fetch specific model(s), comma-separated or repeated |
| `--expand` | `openapi-3.0`, `enterprise_status` |

## schema: inspect inputs/outputs

```bash
genmedia schema fal-ai/flux/dev
genmedia schema fal-ai/flux/dev --format openapi
```

| Option | Description |
|---|---|
| `--format` | `compact` (default) or `openapi` (full OpenAPI JSON) |

Always run `schema` before `run` for an unfamiliar endpoint. The exact field names matter, guessed flags fail with 422.

## run: execute a model

```bash
genmedia run fal-ai/flux/dev --prompt "a cat on the moon"
genmedia run fal-ai/flux/dev --prompt "a cat" --num_images 2
genmedia run fal-ai/flux/dev --prompt "a cat" --logs
genmedia run fal-ai/veo3.1 --prompt "a dog running" --async
genmedia run fal-ai/flux/dev --prompt "a cat" --download
genmedia run fal-ai/flux/dev --prompt "a cat" --num_images 3 \
 --download "./out/{index}.{ext}"
genmedia run fal-ai/flux/dev --help # introspect parameters as CLI flags
```

Any model input parameter can be passed as `--<param> <value>`. Run `genmedia run <endpoint_id> --help` to see a model's accepted parameters as CLI flags, or `genmedia schema <endpoint_id>` for the same as JSON.

| Option | Description |
|---|---|
| `--<param>` | Any model input parameter |
| `--logs` | Stream logs while the model runs (pretty mode only) |
| `--async` | Submit to queue without waiting, returns a `request_id` |
| `--download [template]` | Save every media URL in the result. Optional template uses `{index}`, `{name}`, `{ext}`, `{request_id}` placeholders. Omitted → cwd with source file names. Trailing `/` or existing dir → dir + source names. Plain filename + multiple outputs → `_1`, `_2` collision suffixes. Downloaded paths appear under `downloaded_files` in JSON. |

## status: async job

```bash
genmedia status fal-ai/veo3.1 <request_id>
genmedia status fal-ai/veo3.1 <request_id> --result
genmedia status fal-ai/veo3.1 <request_id> --logs
genmedia status fal-ai/veo3.1 <request_id> --cancel
genmedia status fal-ai/veo3.1 <request_id> --download ./out/ # implies --result
```

| Option | Description |
|---|---|
| `--result` | Fetch the completed result |
| `--logs` | Show logs verbosely |
| `--cancel` | Cancel the queued job |
| `--download [template]` | Same template syntax as on `run`. Implies `--result`. |

## upload: file to fal.ai CDN

```bash
genmedia upload ./photo.jpg
genmedia upload https://example.com/image.png
```

Accepts a local path or a remote URL. Returns a CDN URL usable as model input.

## pricing: cost per call

```bash
genmedia pricing fal-ai/flux/dev
```

Use before running an unfamiliar premium endpoint. Some endpoints (GPT Image 2 at `quality=high`, Seedance Pro at long durations) are an order of magnitude more expensive than alternatives.

## docs: documentation search

```bash
genmedia docs "how to use LoRA"
genmedia docs "webhook callbacks"
```

Searches fal.ai documentation, guides, and API references.

## version / update

```bash
genmedia version # current version + any pending update
genmedia update # download and swap in latest
genmedia update --check # check only, no download
genmedia update --force # reinstall even if already on latest
```

When automatic updates are enabled (default), every TTY invocation may trigger a rate-limited (1/hour) background check that stages the next release. The next launch atomically swaps it in. `GENMEDIA_NO_UPDATE=1` disables all background checks; the manual `update` command still works.

## init: install the default skill bundle

```bash
genmedia init
genmedia init --force # overwrite existing files
```

Installs the default genmedia skill bundle (`genmedia-ref` + `genmedia` core skills) into `.agents/skills/` if the project has a `.agents/` directory, otherwise into `.claude/skills/`. Exits with a message if neither directory exists.

After `init`, agent sessions in that project can use the installed skills without calling `--help`. Commit the installed skills directory so teammates and other agents get the same context.

## skills: manage installed agent skills

```bash
genmedia skills list
genmedia skills install genmedia
genmedia skills update
genmedia skills remove genmedia
```

Installs, updates, lists, and removes agent skills from the genmedia registry.

## Agent-first design

All commands emit structured JSON when piped or called with `--json`:

```bash
genmedia run fal-ai/flux/dev --prompt "a cat" --json
genmedia models "text to video" --json | jq '.models[]'
```

For a machine-readable description of every command, argument, and option:

```bash
genmedia --help --json
```

Useful when bootstrapping an agent's context with the full CLI surface.

## Common patterns

### Run + download in one go

```bash
genmedia run fal-ai/flux/dev \
 --prompt "..." \
 --download "./out/{request_id}_{index}.{ext}" \
 --json
```

### Async submission, then poll until done

```bash
SUBMIT=$(genmedia run <endpoint_id> --prompt "..." --async --json)
REQ=$(echo "$SUBMIT" | jq -r '.request_id')

# Poll until status is COMPLETED
while true; do
 RES=$(genmedia status <endpoint_id> "$REQ" --json)
 STATUS=$(echo "$RES" | jq -r '.status')
 [ "$STATUS" = "COMPLETED" ] && break
 [ "$STATUS" = "FAILED" ] && { echo "$RES" | jq '.error'; exit 1; }
 sleep 5
done

genmedia status <endpoint_id> "$REQ" \
 --download "./out/{request_id}_{index}.{ext}" \
 --json
```

### Upload then reference

```bash
URL=$(genmedia upload ./input.png --json | jq -r '.url')
genmedia run fal-ai/nano-banana-pro/edit \
 --image_urls "$URL" \
 --prompt "..." \
 --download "./out/{request_id}_{index}.{ext}" \
 --json
```

### Inspect before run (always)

```bash
genmedia schema <endpoint_id> --json
genmedia pricing <endpoint_id> --json
```

## Errors

| Symptom | Likely cause | Fix |
|---|---|---|
| `422 Unprocessable Entity` | Wrong field name or missing required field | `genmedia schema <endpoint_id> --json` and read `validation_errors` |
| `401 Unauthorized` | Missing or invalid API key | `genmedia setup` or `export FAL_KEY=…` |
| `Endpoint not found` | Wrong endpoint ID, deprecated, or typo | `genmedia models "<task>" --json` to discover |
| Slow / timeout | Long-running generation | Use `--async`, then `genmedia status … --result` |

## Environment variables

- `FAL_KEY`: API key. Used at runtime when `--no-save-key` was set or no key was saved.
- `GENMEDIA_NO_UPDATE=1`: Disable automatic background update checks.
