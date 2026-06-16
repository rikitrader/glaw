#!/usr/bin/env bash
# loop_test.sh - glaw-loop routes by gate state and refuses autonomous authority acts.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
INTAKE="$ROOT/bin/glaw-intake"
LOOP="$ROOT/bin/glaw-loop"
OVERSIGHT="$ROOT/bin/glaw-oversight"

"$GLAW" matter new "Loop Routing" >/dev/null
"$INTAKE" set workflow_track accounting-tax >/dev/null

"$LOOP" status --json > "$TMP/loop-status.json"; rc=$?
python3 - "$TMP/loop-status.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
ok = (
    data.get("matter") == "loop-routing"
    and data.get("next_gate") == "strategy"
    and data.get("owner") == "intake"
    and data.get("workflow_profile") == "accounting-tax"
    and "irs-examiner" in data.get("adversarial_required", [])
    and "quality routing only" in data.get("authority", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "loop status routes incomplete accounting-tax matter to intake and lists adversarial profile"

"$LOOP" once --json --max-iterations 2 --acceptance "route must name the owner and next gate" > "$TMP/loop-once.json"; rc=$?
python3 - "$TMP/loop-once.json" "$TMP/matters/loop-routing/loop_decisions.jsonl" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
ledger = [json.loads(line) for line in open(sys.argv[2], encoding="utf-8") if line.strip()]
checker = data.get("checker") or {}
criteria = checker.get("criteria") or []
ok = (
    data.get("quality_state") == "blocked"
    and checker.get("status") == "pass"
    and any(item.get("id") == "user_acceptance_1" for item in criteria)
    and len(ledger) == 1
    and ledger[0].get("decision_signature") == data.get("decision_signature")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "loop once writes checked routing decision with acceptance criteria"

"$LOOP" once --json --max-iterations 1 > "$TMP/loop-escalate.json"; rc=$?
python3 - "$TMP/loop-escalate.json" "$TMP/matters/loop-routing/loop_decisions.jsonl" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
ledger = [json.loads(line) for line in open(sys.argv[2], encoding="utf-8") if line.strip()]
checker = data.get("checker") or {}
failed = {item.get("id") for item in checker.get("failed", [])}
ok = (
    data.get("quality_state") == "human_escalation_required"
    and data.get("owner") == "human-oversight-board"
    and data.get("next_command") == "bin/glaw-oversight status"
    and (data.get("oversight") or {}).get("event") == "oversight_escalation"
    and "iteration_cap" in failed
    and len(ledger) == 2
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "loop escalates after iteration cap without convergence"

"$LOOP" status --json > "$TMP/loop-latched.json"; rc=$?
python3 - "$TMP/loop-latched.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
ok = (
    data.get("quality_state") == "human_escalation_required"
    and data.get("owner") == "human-oversight-board"
    and data.get("latched_from")
    and "remains latched" in data.get("reason", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "loop keeps non-convergence escalation latched until oversight resume"

"$LOOP" once --request-action file > "$TMP/loop-file.out" 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'HUMAN AUTHORITY BLOCKED' "$TMP/loop-file.out" && grep -q 'authority_blocked' "$TMP/matters/loop-routing/loop_decisions.jsonl" && echo 1 || echo 0)" "loop refuses and audits autonomous file request"

"$LOOP" once --json --request-action transmit > "$TMP/loop-transmit.json" 2>&1; rc=$?
python3 - "$TMP/loop-transmit.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
ok = data.get("quality_state") == "authority_blocked" and data.get("requested_action") == "transmit"
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "loop JSON reports authority-blocked transmit"

"$GLAW" matter new "Loop Compliance" >/dev/null
M2="$TMP/matters/loop-compliance"
mkdir -p "$M2/evidence"
printf 'Bank statement and engagement source fixture.\n' > "$M2/evidence/source.txt"
cat > "$M2/intake.json" <<'JSON'
{
  "status": "complete",
  "universal": {
    "matter_name": "Loop Compliance",
    "workflow_track": "accounting-tax",
    "client_names": ["Example Client LLC"],
    "parties": ["Example Client LLC", "Example Bank"],
    "jurisdiction": "US federal / Delaware",
    "goal": "Prepare source-backed accounting-tax file-readiness packet.",
    "source_documents": ["SRC-0001 bank statement and engagement source fixture"],
    "deadlines": ["2026-09-15 tax extension deadline"],
    "facts_timeline": ["SRC-0001 bank activity imported for reconciliation testing"],
    "open_questions": ["SRC-0001 identify unreconciled exceptions"],
    "conflicts_parties": ["Example Client LLC", "Example Bank"],
    "authorized_scope": "Accounting-tax analysis and workpaper preparation only."
  },
  "track_specific": {
    "bank_statement_sources": ["SRC-0001 evidence/source.txt"],
    "tax_years": ["2026"],
    "entity_tax_type": "partnership",
    "books_status": "open pending reconciliation",
    "irs_forms_needed": ["Form 1065"]
  },
  "review": {
    "completed_by": "Morgan Rivera"
  }
}
JSON
cat > "$M2/ethics.json" <<'JSON'
{
  "status": "complete",
  "conflicts_status": "cleared",
  "conflicts_source": "SRC-0001 conflicts checked against provided parties",
  "engagement": {
    "status": "drafted",
    "scope": "Accounting-tax analysis and workpaper preparation only.",
    "responsible_professional": "Alexandra Chen",
    "source": "SRC-0001 engagement authority and source fixture"
  }
}
JSON
cat > "$M2/timeline.jsonl" <<'JSONL'
{"ts":"2026-06-16T00:00:00Z","event":"intake_complete"}
{"ts":"2026-06-16T00:00:01Z","event":"conflicts_cleared"}
{"ts":"2026-06-16T00:00:02Z","event":"citations_verified"}
{"ts":"2026-06-16T00:00:03Z","event":"adversarial_done"}
{"ts":"2026-06-16T00:00:04Z","event":"red_flags_clear"}
JSONL
printf 'draft\n' > "$M2/.stage"
cat > "$M2/final_packet.json" <<'JSON'
{
  "status": "blocked",
  "compliance_manifest": [
    {
      "id": "accounting-control",
      "owner": "glaw-accounting",
      "status": "fail",
      "missing": ["bank_reconciliation", "tax_tie_out"],
      "detail": "accounting controls must pass before file-readiness"
    }
  ]
}
JSON
"$LOOP" status --matter loop-compliance --json > "$TMP/loop-compliance.json"; rc=$?
python3 - "$TMP/loop-compliance.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
failures = data.get("compliance_failures") or []
ok = (
    data.get("next_gate") == "file"
    and data.get("owner") == "accounting-control"
    and data.get("next_command") == "bin/glaw-accounting-control"
    and "accounting controls are blocked" in data.get("reason", "")
    and failures
    and failures[0].get("id") == "accounting-control"
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "loop routes failed accounting-control manifest to accounting-control owner"

cat > "$M2/final_packet.json" <<'JSON'
{
  "status": "blocked",
  "compliance_manifest": [
    {
      "id": "government-adversary",
      "owner": "glaw-adversarial",
      "status": "fail",
      "missing": ["government_adversary_manifest"],
      "detail": "no SEC/IRS/regulator RED-team attack survived against the source packet"
    }
  ]
}
JSON
"$LOOP" status --matter loop-compliance --json > "$TMP/loop-government-adversary.json"; rc=$?
python3 - "$TMP/loop-government-adversary.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
failures = data.get("compliance_failures") or []
ok = (
    data.get("next_gate") == "file"
    and data.get("owner") == "adversarial"
    and data.get("next_command") == "bin/glaw-adversarial status --profile auto"
    and "government-adversary manifest is blocked" in data.get("reason", "")
    and failures
    and failures[0].get("id") == "government-adversary"
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "loop routes failed government-adversary manifest to adversarial owner"

"$OVERSIGHT" halt --by "QA reviewer" --reason "test halt" >/dev/null
"$LOOP" status --json > "$TMP/loop-halted.json"; rc=$?
python3 - "$TMP/loop-halted.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
ok = (
    data.get("quality_state") == "human_escalation_required"
    and data.get("next_gate") == "oversight"
    and data.get("owner") == "human-oversight-board"
    and "kill-switch active" in data.get("reason", "")
    and (data.get("oversight") or {}).get("status") == "halted"
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "loop stops routing while oversight kill-switch is active"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }
