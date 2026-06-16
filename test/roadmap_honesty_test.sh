#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROADMAP="$ROOT/ROADMAP.md"

pass=0
fail(){ echo "FAIL: $1" >&2; exit 1; }
ok(){ pass=$((pass+1)); }

for stale in \
  "No persistent cross-matter memory" \
  "No host embedding" \
  "Citations not corpus-backed" \
  "No constitutional/legislative/judicial seats" \
  "Suggested build order: branch seats"
do
  if grep -q "$stale" "$ROADMAP"; then
    fail "ROADMAP.md still carries stale shipped-gap phrase: $stale"
  fi
done
ok

for shipped in \
  "glaw-learnings" \
  "glaw-host" \
  "glaw-mcp" \
  "glaw-extism" \
  "citation corpus capture rejects off-allowlist URLs" \
  "/glaw-constitutional" \
  "tax wrapper golden/coverage manifest" \
  "jurisdiction/packs/us-core"
do
  if ! grep -q "$shipped" "$ROADMAP"; then
    fail "ROADMAP.md missing shipped-state marker: $shipped"
  fi
done
ok

echo "$pass passed"
