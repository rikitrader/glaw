#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
printf 'registry fixture\n' > "$TMP/artifact.md"
"$ROOT/bin/glaw-registry" init "$TMP/registry.jsonl" --registry-id REG-0001 --actor "GLAW Governor"
"$ROOT/bin/glaw-registry" register "$TMP/registry.jsonl" --artifact-id ART-0001 --kind artifact --path "$TMP/artifact.md" --department accounting-assurance --lane technical-accounting-memo --owner glaw-accounting --version v1 --risk-class high --source-id SRC-0001 --actor "GLAW Governor"
if "$ROOT/bin/glaw-registry" validate "$TMP/registry.jsonl"; then
  echo "expected high-risk approval gate to block" >&2
  exit 1
fi
"$ROOT/bin/glaw-registry" approve "$TMP/registry.jsonl" --artifact-id ART-0001 --decision approve --reviewer "Alex Rivera" --role "Controller" --rationale "Reviewed source, version, calculation, and accounting impact."
"$ROOT/bin/glaw-registry" validate "$TMP/registry.jsonl" | rg '"valid": true'
printf 'tamper\n' >> "$TMP/artifact.md"
if "$ROOT/bin/glaw-registry" validate "$TMP/registry.jsonl"; then
  echo "expected changed artifact hash to block" >&2
  exit 1
fi
echo "registry contract: ok"
