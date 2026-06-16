#!/usr/bin/env bash
# gate_docs_consistency_test.sh - public docs must match the executable gate contract.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
pass=0

fail(){ echo "FAIL: $1" >&2; exit 1; }
ok(){ pass=$((pass+1)); }

if grep -R "Four hard gates" "$ROOT/README.md" "$ROOT/SKILL.md" "$ROOT/docs" "$ROOT/lib/workflow.md" >/dev/null 2>&1; then
  fail "stale 'Four hard gates' wording remains"
fi
ok

for doc in "$ROOT/README.md" "$ROOT/SKILL.md" "$ROOT/docs/WORKFLOWS.md" "$ROOT/docs/org-chart-and-usage.md" "$ROOT/lib/workflow.md"; do
  for marker in \
    "Structured intake" \
    "Conflicts cleared" \
    "Citations verified" \
    "Adversarial RED" \
    "Chief/Council" \
    "UPL disclaimer" \
    "Docket gate"; do
    grep -q "$marker" "$doc" || fail "${doc#$ROOT/} missing gate marker: $marker"
  done
done
ok

for event in \
  "intake_complete" \
  "conflicts_cleared" \
  "citations_verified" \
  "adversarial_done" \
  "red_flags_clear" \
  "final_packet_ready" \
  "chief_approved" \
  "docket_gate_complete"; do
  grep -q "$event" "$ROOT/bin/glaw-gate" || fail "bin/glaw-gate missing event: $event"
done
ok

echo "$pass passed"
