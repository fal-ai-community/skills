#!/usr/bin/env bash
# fal-redesign describe: re-run VLM#2 (build-spec + tokens) on an already-generated after.png,
# without redoing the screenshot + gpt-image-2/edit passes. Useful for iterating on the spec only.
# Usage:
#   bash describe.sh --after <path/to/after.png> [--out <dir>]
set -euo pipefail

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
  echo "fal-redesign: runtime not found. Set FAL_SITE_RUNTIME=/abs/path/to/runtime." >&2
  exit 2
fi
if [ -z "${FAL_KEY:-}" ]; then
  echo "fal-redesign: FAL_KEY is not set." >&2
  exit 1
fi
if [ ! -d "$RUNTIME_DIR/node_modules" ]; then
  echo "fal-redesign: installing runtime dependencies (first run only)..." >&2
  (cd "$RUNTIME_DIR" && npm install --silent)
fi

AFTER=""
OUT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --after) AFTER="$2"; shift 2 ;;
    --out|-o) OUT="$2"; shift 2 ;;
    -h|--help) sed -n '2,5p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "fal-redesign describe: unknown flag: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$AFTER" ]; then
  echo "fal-redesign describe: --after <path> is required" >&2
  exit 2
fi

ARGS=("describe" "$AFTER")
if [ -n "$OUT" ]; then ARGS+=("-o" "$OUT"); fi

exec node "$RUNTIME_DIR/bin/fal-site.mjs" "${ARGS[@]}"
