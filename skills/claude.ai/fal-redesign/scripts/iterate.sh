#!/usr/bin/env bash
# fal-redesign iterate: screenshot the implemented site, compare to a reference after.png,
# emit a delta-spec of residual pixel-level fixes.
# Usage:
#   bash iterate.sh --target <path|url> --reference <path/to/after.png> [--out <dir>]
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
  echo "fal-redesign: FAL_KEY is not set. Get one at https://fal.ai/dashboard/keys and export it." >&2
  exit 1
fi

if [ ! -d "$RUNTIME_DIR/node_modules" ]; then
  echo "fal-redesign: installing runtime dependencies (first run only)..." >&2
  (cd "$RUNTIME_DIR" && npm install --silent)
fi

TARGET=""
REFERENCE=""
OUT=".fal-site-upgrade"

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --reference) REFERENCE="$2"; shift 2 ;;
    --out|-o) OUT="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,6p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *)
      echo "fal-redesign iterate: unknown flag: $1" >&2
      exit 2 ;;
  esac
done

if [ -z "$TARGET" ]; then
  echo "fal-redesign iterate: --target is required (path or URL to the implemented site)" >&2
  exit 2
fi
if [ -z "$REFERENCE" ]; then
  echo "fal-redesign iterate: --reference is required (path to the after.png reference)" >&2
  exit 2
fi

exec node "$RUNTIME_DIR/bin/fal-site.mjs" iterate "$TARGET" --reference "$REFERENCE" -o "$OUT"
