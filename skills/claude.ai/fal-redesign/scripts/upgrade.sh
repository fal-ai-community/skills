#!/usr/bin/env bash
# fal-redesign upgrade: redesign an existing coded site via fal.ai (opus-4.7 + gpt-image-2/edit).
# Usage:
#   bash upgrade.sh --target <path|url> [--context "..."] [--variants N] [--out <dir>]
set -euo pipefail

# Resolve physical paths (-P) so symlinked installs (e.g. ~/.claude/skills/fal-redesign → repo)
# still locate the runtime correctly via the relative fallback.
SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -P "$SCRIPT_DIR/.." && pwd)"
RUNTIME_DIR="${FAL_SITE_RUNTIME:-$SKILL_DIR/runtime}"

# For local development, fall back to the monorepo-style layout.
if [ ! -f "$RUNTIME_DIR/bin/fal-site.mjs" ]; then
  CANDIDATE="$(cd "$SKILL_DIR/../../.." && pwd)"
  if [ -f "$CANDIDATE/bin/fal-site.mjs" ]; then
    RUNTIME_DIR="$CANDIDATE"
  fi
fi

if [ ! -f "$RUNTIME_DIR/bin/fal-site.mjs" ]; then
  echo "fal-redesign: runtime not found. Set FAL_SITE_RUNTIME=/abs/path/to/runtime." >&2
  exit 2
fi

if [ -z "${FAL_KEY:-}" ]; then
  echo "fal-redesign: FAL_KEY is not set. Get one at https://fal.ai/dashboard/keys and export it." >&2
  exit 1
fi

if [ ! -d "$RUNTIME_DIR/node_modules" ]; then
  echo "fal-redesign: installing runtime dependencies (first run only)..." >&2
  (cd "$RUNTIME_DIR" && npm install --silent)
fi

TARGET=""
CONTEXT=""
OUT=".fal-site-upgrade"
VARIANTS=1

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --context) CONTEXT="$2"; shift 2 ;;
    --variants|-n) VARIANTS="$2"; shift 2 ;;
    --out|-o) OUT="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,5p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *)
      echo "fal-redesign upgrade: unknown flag: $1" >&2
      exit 2 ;;
  esac
done

if [ -z "$TARGET" ]; then
  echo "fal-redesign upgrade: --target is required (path or URL)" >&2
  exit 2
fi

ARGS=("upgrade" "$TARGET" "-o" "$OUT" "--variants" "$VARIANTS")
if [ -n "$CONTEXT" ]; then
  ARGS+=("--context" "$CONTEXT")
fi

exec node "$RUNTIME_DIR/bin/fal-site.mjs" "${ARGS[@]}"
