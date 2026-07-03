#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# claude-linkedin-suite installer
# Installs the LinkedIn Claude Code skills into ~/.claude/skills/ and sets up
# the credentials template. Safe to re-run (idempotent; backs up existing dirs).
# ---------------------------------------------------------------------------
set -euo pipefail

# Resolve the directory this script lives in (repo root), following symlinks.
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
REPO_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"

SKILLS_SRC="$REPO_DIR/skills"
SKILLS_DEST="$HOME/.claude/skills"
ENV_EXAMPLE="$REPO_DIR/config/linkedin-api.env.example"
ENV_DEST="$HOME/.config/linkedin-api.env"
TS="$(date +%Y%m%d-%H%M%S)"

bold() { printf '\033[1m%s\033[0m\n' "$1"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
info() { printf '  \033[34m•\033[0m %s\n' "$1"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; }

bold "claude-linkedin-suite — installer"
echo

# --- 1. Preconditions -------------------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found on PATH. Install Python 3.9+ and re-run." >&2
  exit 1
fi
ok "python3 found ($(python3 --version 2>&1))"
if [ ! -d "$SKILLS_SRC" ]; then
  echo "ERROR: '$SKILLS_SRC' not found. Run this script from inside the cloned repo." >&2
  exit 1
fi

# --- 2. Install skills ------------------------------------------------------
mkdir -p "$SKILLS_DEST"
info "Installing skills into $SKILLS_DEST"
for skill_path in "$SKILLS_SRC"/*/; do
  skill="$(basename "$skill_path")"
  target="$SKILLS_DEST/$skill"
  if [ -e "$target" ]; then
    backup="$SKILLS_DEST/.backup-$TS/$skill"
    mkdir -p "$(dirname "$backup")"
    mv "$target" "$backup"
    warn "existing '$skill' backed up to $backup"
  fi
  cp -R "$skill_path" "$target"
  ok "installed skill: /$skill"
done

# --- 3. Credentials template ------------------------------------------------
mkdir -p "$(dirname "$ENV_DEST")"
if [ -f "$ENV_DEST" ]; then
  ok "credentials already present at $ENV_DEST (left untouched)"
else
  cp "$ENV_EXAMPLE" "$ENV_DEST"
  chmod 600 "$ENV_DEST"
  warn "created credentials template at $ENV_DEST"
  warn "  → edit it and fill in LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_ID"
fi

# --- 4. Smoke check ---------------------------------------------------------
if python3 -c "import urllib.request, json, argparse" 2>/dev/null; then
  ok "python standard library OK (no pip install needed for current skills)"
fi

echo
bold "Done."
echo
echo "Installed commands (usable in Claude Code on this machine):"
echo "   /post-linkedin                 write & publish posts (text / image)"
echo "   /post-linkedin-feed-comments   comment on relevant posts in your feed"
echo "   /post-linkedin-posts-comment   reply to comments on your own posts"
echo
echo "Next steps:"
echo "   1. Add your credentials:   \$EDITOR $ENV_DEST"
echo "   2. (Comment skills only) sign into LinkedIn in Chrome — they drive a"
echo "      logged-in browser via the Chrome DevTools MCP."
echo "   3. Restart Claude Code so it picks up the new skills, then run /post-linkedin"
echo
echo "Verify publishing works (optional):"
echo "   python3 \"$SKILLS_DEST/post-linkedin/scripts/linkedin_post.py\" \"Hello from a new machine\""
