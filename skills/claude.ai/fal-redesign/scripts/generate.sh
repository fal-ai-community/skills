#!/usr/bin/env bash
# fal-site generate: greenfield site generation via fal.ai (brief -> mockup -> HTML).
# Usage:
#   bash generate.sh --context "<freeform>" [--variants 4] [--concurrency 2] [--out <dir>] [--mockup-only]
set -euo pipefail

# Resolve physical paths (-P) so symlinked installs still locate the runtime.
SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -P "$SCRIPT_DIR/.." && pwd)"
RUNTIME_DIR="${FAL_SITE_RUNTIME:-$SKILL_DIR/runtime}"

if [ ! -f "$RUNTIME_DIR/bin/fal-site.mjs" ]; then
  CANDIDATE="$(cd "$SKILL_DIR/../../.." && pwd)"
  if [ -f "$CANDIDATE/bin/fal-site.mjs" ]; then
    RUNTIME_DIR="$CANDIDATE"
  fi
fi

if [ ! -f "$RUNTIME_DIR/bin/fal-site.mjs" ]; then
  echo "fal-site: runtime not found. Set FAL_SITE_RUNTIME=/abs/path/to/runtime." >&2
  exit 2
fi

if [ -z "${FAL_KEY:-}" ]; then
  echo "fal-site: FAL_KEY is not set. Get one at https://fal.ai/dashboard/keys and export it." >&2
  exit 1
fi

if [ ! -d "$RUNTIME_DIR/node_modules" ]; then
  echo "fal-site: installing runtime dependencies (first run only)..." >&2
  (cd "$RUNTIME_DIR" && npm install --silent)
fi

CONTEXT=""
VARIANTS=4
CONCURRENCY=2
OUT="fal-site-out"
MOCKUP_ONLY=""

while [ $# -gt 0 ]; do
  case "$1" in
    --context) CONTEXT="$2"; shift 2 ;;
    --variants|-n) VARIANTS="$2"; shift 2 ;;
    --concurrency) CONCURRENCY="$2"; shift 2 ;;
    --out|-o) OUT="$2"; shift 2 ;;
    --mockup-only) MOCKUP_ONLY="--mockup-only"; shift ;;
    -h|--help)
      sed -n '2,5p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *)
      echo "fal-site generate: unknown flag: $1" >&2
      exit 2 ;;
  esac
done

if [ -z "$CONTEXT" ]; then
  echo "fal-site generate: --context is required (freeform brief)" >&2
  exit 2
fi

ARGS=("generate" "$CONTEXT" "-n" "$VARIANTS" "--concurrency" "$CONCURRENCY" "-o" "$OUT")
if [ -n "$MOCKUP_ONLY" ]; then
  ARGS+=("$MOCKUP_ONLY")
fi

exec node "$RUNTIME_DIR/bin/fal-site.mjs" "${ARGS[@]}"
