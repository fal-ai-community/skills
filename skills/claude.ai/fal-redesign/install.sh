#!/usr/bin/env bash
# fal-redesign: one-command installer
#
#   curl -fsSL https://raw.githubusercontent.com/fal-ai-community/skills/main/skills/claude.ai/fal-redesign/install.sh | bash
#
# Downloads the skill into ~/.claude/skills/fal-redesign so Claude Code / Codex /
# Claude.ai Projects can invoke it. No git required.
set -euo pipefail

REPO="fal-ai-community/skills"
BRANCH="main"
SUBDIR="skills/claude.ai/fal-redesign"
TARGET="${FAL_DESIGN_TARGET:-${HOME}/.claude/skills/fal-redesign}"

say()   { printf '  %s\n' "$*"; }
good()  { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn()  { printf '  \033[33m⚠\033[0m %s\n' "$*"; }
fail()  { printf '  \033[31m✗\033[0m %s\n' "$*" >&2; exit 1; }

printf '\n  \033[1mfal-redesign installer\033[0m\n\n'

command -v curl >/dev/null 2>&1 || fail "curl is required"
command -v tar  >/dev/null 2>&1 || fail "tar is required"
command -v node >/dev/null 2>&1 || fail "node 18+ is required (https://nodejs.org)"

NODE_MAJOR=$(node -v | sed 's/v//' | cut -d. -f1)
[ "$NODE_MAJOR" -ge 18 ] || fail "node 18+ is required (have $(node -v))"
good "node $(node -v)"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

say "fetching ${REPO}@${BRANCH}…"
curl -fsSL "https://codeload.github.com/${REPO}/tar.gz/refs/heads/${BRANCH}" | tar -xz -C "$TMP"
SRC="$(find "$TMP" -maxdepth 1 -type d -name "skills-*" | head -n1)/${SUBDIR}"
[ -d "$SRC" ] || fail "archive layout unexpected: ${SUBDIR} not found"

mkdir -p "$(dirname "$TARGET")"
if [ -e "$TARGET" ] || [ -L "$TARGET" ]; then
  BACKUP="${TARGET}.bak.$(date +%s)"
  warn "existing install at ${TARGET}: moved to ${BACKUP}"
  mv "$TARGET" "$BACKUP"
fi

cp -R "$SRC" "$TARGET"
chmod +x "$TARGET"/scripts/*.sh 2>/dev/null || true
chmod +x "$TARGET"/install.sh 2>/dev/null || true
good "installed → ${TARGET}"

printf '\n'
if [ -z "${FAL_KEY:-}" ]; then
  warn "FAL_KEY is not set"
  say  "  get a key      https://fal.ai/dashboard/keys"
  say  "  then export it  export FAL_KEY=your_key   # add to ~/.zshrc or ~/.bashrc"
else
  good "FAL_KEY is set"
fi

cat <<EOF

  Next steps:
    In Claude Code or Codex, open a project and run:
      /fal-redesign upgrade ./your-site.html

    Or call the script directly:
      bash ${TARGET}/scripts/upgrade.sh --target ./your-site.html

  Docs:   https://github.com/${REPO}/tree/${BRANCH}/${SUBDIR}
  Issues: https://github.com/${REPO}/issues

EOF
