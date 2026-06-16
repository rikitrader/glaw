#!/usr/bin/env bash
# oversight_test.sh - kill-switch and Oversight Board ledger behavior.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
OVERSIGHT="$ROOT/bin/glaw-oversight"

"$OVERSIGHT" status --json > "$TMP/status.json"; rc=$?
python3 - "$TMP/status.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
sys.exit(0 if data.get("status") == "active" and data.get("state", {}).get("halted") is False else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "oversight starts active"

"$OVERSIGHT" halt --by "Board Chair" --reason "material control concern" --json > "$TMP/halt.json"; rc=$?
python3 - "$TMP/halt.json" "$TMP/oversight/oversight.jsonl" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
rows=[json.loads(line) for line in open(sys.argv[2]) if line.strip()]
ok=data.get("status") == "halted" and data.get("state", {}).get("halted") is True and rows[-1].get("event") == "kill_switch_halted"
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "halt records kill-switch state and ledger row"

"$OVERSIGHT" resume --by "Board Chair" --role WRITER --reason "not enough authority" --json > "$TMP/resume-blocked.json" 2>&1; rc=$?
python3 - "$TMP/resume-blocked.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
sys.exit(0 if data.get("status") == "blocked" else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "resume requires ADMIN authority"

"$OVERSIGHT" resume --by "Board Chair" --role ADMIN --reason "control issue resolved" --json > "$TMP/resume.json"; rc=$?
python3 - "$TMP/resume.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
sys.exit(0 if data.get("status") == "active" and data.get("state", {}).get("halted") is False else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "ADMIN can resume with reason"

"$OVERSIGHT" escalate --matter matter-one --reason "loop did not converge" --source "SRC-0001 route evidence" --json > "$TMP/escalate.json"; rc=$?
python3 - "$TMP/escalate.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
sys.exit(0 if data.get("event") == "oversight_escalation" and data.get("status") == "open" else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "escalation records open oversight item"

"$OVERSIGHT" decision --matter matter-one --decision approve --by "Board Chair" --role ADMIN --reason "SRC-0001 controls clear" --source "SRC-0001 controls memo" --json > "$TMP/decision.json"; rc=$?
python3 - "$TMP/decision.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
sys.exit(0 if data.get("event") == "oversight_decision" and data.get("decision") == "approve" else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "ADMIN can record Board decision"

"$OVERSIGHT" validate-policy --json > "$TMP/policy.json"; rc=$?
python3 - "$TMP/policy.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ok=(
    data.get("status") == "pass"
    and data.get("required_trigger_count") == 6
    and data.get("decision_rule_count") == 5
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "bundled Oversight Board policy pack validates"

"$OVERSIGHT" policy --json > "$TMP/policy-show.json"; rc=$?
python3 - "$TMP/policy-show.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
policy=data.get("policy", {})
triggers={item.get("id") for item in policy.get("escalation_triggers", [])}
acts=set(policy.get("prohibited_autonomous_acts", []))
ok=(
    data.get("status") == "pass"
    and "accounting-control-failure" in triggers
    and "government-adversary-failure" in triggers
    and {"file", "sign", "submit-live"} <= acts
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "policy pack exposes accounting/government escalation and human-only acts"

cat > "$TMP/bad-policy.json" <<'JSON'
{
  "schema_version": 1,
  "name": "Bad Policy",
  "authority_boundary": "GLAW can act alone",
  "prohibited_autonomous_acts": ["file"],
  "escalation_triggers": [],
  "decision_rules": [],
  "required_evidence": ["none"]
}
JSON
"$OVERSIGHT" validate-policy --path "$TMP/bad-policy.json" --json > "$TMP/bad-policy.out" 2>&1; rc=$?
python3 - "$TMP/bad-policy.out" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
failure_ids={item.get("id") for item in data.get("failures", [])}
ok=data.get("status") == "fail" and "human_seal" in failure_ids and "required_escalation_triggers" in failure_ids
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "malformed Oversight Board policy fails closed"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }
