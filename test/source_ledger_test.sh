#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
printf 'source fixture\n' > "$TMP/source.md"
"$ROOT/bin/glaw-source-ledger" add "$TMP/sources.jsonl" SRC-0001 "$TMP/source.md" --kind earnings-release >/dev/null
"$ROOT/bin/glaw-source-ledger" validate "$TMP/sources.jsonl" | rg '"valid": true'
echo "source ledger contract: ok"
