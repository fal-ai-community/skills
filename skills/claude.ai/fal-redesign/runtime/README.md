# fal-site

Generate N Awwwards / FWA-tier single-file HTML site variations from any context, powered by [fal.ai](https://fal.ai) (OpenRouter text LLM + `gpt-image-2` for hero art).

## Install & run

```bash
export FAL_KEY=... # https://fal.ai/dashboard/keys
npx fal-site "a calm Parisian coffee subscription, warm editorial feel"
```

By default you get 6 variants, each in a different Awwwards/FWA-inspired direction (swiss editorial, brutalist mono, kinetic type, glass 3D, dark neon, etc.).

## Usage

```
npx fal-site "<free-form context>"
npx fal-site --file brief.txt -n 10
cat email.txt | npx fal-site --stdin -n 8 -o ~/Desktop/out
```

### Options
- `-n, --variants <N>`: how many variations (default `6`, max `12`)
- `-o, --out <dir>`: output directory (default `./fal-site-out`)
- `--no-hero`: skip the gpt-image-2 hero (faster, tiny HTML)
- `--concurrency <N>`: parallel variant builds (default `3`)
- `--list-directions`: print available design directions
- `--model <id>`: override the text model (default `anthropic/claude-sonnet-4.6`)

### Output

Every run creates a timestamped folder. Each variant is a fully self-contained `index.html` (Tailwind CDN + inline base64 hero), drop it on Vercel, email it, or open it directly.

```
fal-site-out/
 1714656000000-fal/
 index.html # gallery of all variants
 brief.json
 01-swiss-editorial/index.html
 02-brutalist-mono/index.html
 ...
```

## How it works

1. **Brief extraction**: `openrouter/router` turns your context into a structured JSON brief (brand, tagline, sections, tone, palette hint, hero image prompt).
2. **Variant generation**: for each design direction we ask the LLM to produce a complete single-file `index.html` that would be credible on Awwwards / FWA, using Tailwind via CDN.
3. **Hero image**: `fal-ai/gpt-image-2` renders a cinematic hero per variant; the image is downloaded and inlined as a `data:` URI, so each `index.html` is truly standalone.

No runtime deps, plain Node 18+ (`fetch` built-in).
