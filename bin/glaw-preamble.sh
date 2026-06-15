#!/usr/bin/env bash
# Shared preamble emitted by every GLAW skill (the firm's "open the file before
# you talk" reflex). Echoes the active matter, its type, stage, and any deadline
# inside 14 days. Sourced/run at the top of each stage skill. Never fails hard.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GLAW="$SCRIPT_DIR/glaw"
[ -x "$GLAW" ] || GLAW="${CODEX_HOME:-$HOME/.codex}/skills/glaw/bin/glaw"
[ -x "$GLAW" ] || GLAW="$HOME/.claude/skills/glaw/bin/glaw"
SLUG="$("$GLAW" slug 2>/dev/null || echo "")"
echo "GLAW_VERSION: $("$GLAW" version 2>/dev/null || echo unknown)"
if [ -z "$SLUG" ]; then
  echo "ACTIVE_MATTER: none"
  echo "HINT: open one with — glaw matter new \"<matter name>\""
else
  HOME_DIR="$("$GLAW" home 2>/dev/null)/matters/$SLUG"
  TYPE="$(grep -E '^type:' "$HOME_DIR/matter.md" 2>/dev/null | sed -E 's/^type:[[:space:]]*//; s/[[:space:]]*#.*//')"
  STAGE="$("$GLAW" stage 2>/dev/null || echo intake)"
  CONFLICTS="$(grep -A1 'Conflicts check' "$HOME_DIR/matter.md" 2>/dev/null | grep -E 'status:' | sed -E 's/.*status:[[:space:]]*//; s/[[:space:]]*#.*//')"
  echo "ACTIVE_MATTER: $SLUG"
  echo "MATTER_TYPE: ${TYPE:-unset}"
  echo "STAGE: $STAGE"
  echo "CONFLICTS: ${CONFLICTS:-PENDING}"
  echo "--- deadlines due within 14 days ---"
  "$GLAW" docket upcoming 14 2>/dev/null || true
fi
