#!/usr/bin/env bash
# gate_docs_consistency_test.sh - public docs must match the executable gate contract.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
pass=0

fail(){ echo "FAIL: $1" >&2; exit 1; }
ok(){ pass=$((pass+1)); }

if grep -R -iE "\b(four|4)[ -]?(hard )?gates\b|the 4 gates|GLAW's 4 gates" \
  "$ROOT/README.md" "$ROOT/SKILL.md" "$ROOT/ROADMAP.md" "$ROOT/docs" "$ROOT/lib/workflow.md" >/dev/null 2>&1; then
  fail "stale four-gate wording remains"
fi
ok

for doc in "$ROOT/README.md" "$ROOT/SKILL.md" "$ROOT/ROADMAP.md" "$ROOT/docs/WORKFLOWS.md" "$ROOT/docs/org-chart-and-usage.md" "$ROOT/lib/workflow.md"; do
  for marker in \
    "Structured intake" \
    "conflicts" \
    "citation" \
    "adversarial" \
    "red flag" \
    "final packet" \
    "Chief/Council" \
    "UPL" \
    "docket"; do
    grep -qi "$marker" "$doc" || fail "${doc#$ROOT/} missing gate marker: $marker"
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

grep -q -- "--profile sec-reporting --audit-tieout" "$ROOT/docs/WORKFLOWS.md" \
  || fail "docs/WORKFLOWS.md must document SEC reporting accounting-control audit tie-out"
grep -q "SEC audit/ICFR/PCAOB tie-out" "$ROOT/docs/tools.md" \
  || fail "docs/tools.md must document SEC audit/ICFR/PCAOB tie-out gate"
ok

echo "$pass passed"
