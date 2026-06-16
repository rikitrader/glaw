#!/usr/bin/env bash
# policy_test.sh - policy-as-fail-closed CI/doctor contract regression.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"
POLICY="$ROOT/bin/glaw-policy"

"$POLICY" check --json > "$TMP/policy.json"; rc=$?
python3 - "$TMP/policy.json" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
ids = {item["id"] for item in data["checks"]}
need = {"ci_policy_contract", "doctor_required_tests", "gate_required_artifacts", "pre_push_gate"}
sys.exit(0 if data["status"] == "pass" and need <= ids else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "policy check passes current repo contract"

FIX="$TMP/repo"
mkdir -p "$FIX/.github/workflows" "$FIX/bin" "$FIX/.githooks"
cp "$ROOT/.github/workflows/ci.yml" "$FIX/.github/workflows/ci.yml"
cp "$ROOT/bin/glaw-policy" "$FIX/bin/glaw-policy"
cp "$ROOT/bin/glaw-commit-gate" "$FIX/bin/glaw-commit-gate"
cp "$ROOT/bin/glaw-doctor" "$FIX/bin/glaw-doctor"
cp "$ROOT/bin/glaw-gate" "$FIX/bin/glaw-gate"
cp "$ROOT/bin/glaw-final-packet" "$FIX/bin/glaw-final-packet"
cp "$ROOT/setup" "$FIX/setup"
cp "$ROOT/.githooks/pre-commit" "$FIX/.githooks/pre-commit"
cp "$ROOT/.githooks/pre-push" "$FIX/.githooks/pre-push"
chmod +x "$FIX/bin/glaw-policy" "$FIX/bin/glaw-doctor"
python3 - "$FIX/.github/workflows/ci.yml" <<'PY'
import pathlib
import sys
p = pathlib.Path(sys.argv[1])
text = p.read_text(encoding="utf-8")
p.write_text(text.replace("python3 bin/glaw-policy check", "echo policy skipped"), encoding="utf-8")
PY
"$POLICY" check --root "$FIX" --json > "$TMP/policy-fail.json"; rc=$?
python3 - "$TMP/policy-fail.json" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
failed = {item["id"] for item in data["failed"]}
sys.exit(0 if data["status"] == "fail" and "ci_policy_contract" in failed else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "policy check fails closed when CI omits policy gate"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }
