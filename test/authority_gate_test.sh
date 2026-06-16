#!/usr/bin/env bash
# authority_gate_test.sh — human-only acts fail closed unless a human actor authorizes them.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
AUTH="$ROOT/bin/glaw-authority"
GLAW="$ROOT/bin/glaw"
CHIEF="$ROOT/bin/glaw-chief-decision"
IRS="$ROOT/bin/glaw-irs-file"
OVERSIGHT="$ROOT/bin/glaw-oversight"

"$AUTH" check transmit >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "authority check blocks transmit without human actor"
"$AUTH" check transmit --human-authority "Alex Rivera, licensed attorney" >/tmp/glaw-auth-role.out 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'RBAC BLOCKED' /tmp/glaw-auth-role.out && echo 1 || echo 0)" "authority check blocks human actor without ADMIN role"
"$AUTH" check transmit --human-authority "Alex Rivera, licensed attorney" --role WRITER >/tmp/glaw-auth-writer.out 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'RBAC BLOCKED' /tmp/glaw-auth-writer.out && echo 1 || echo 0)" "authority check blocks WRITER from human-seal act"
"$AUTH" check transmit --human-authority "Alex Rivera, licensed attorney" --role ADMIN >/dev/null; rc=$?
ok "$([ "$rc" = 0 ] && grep -q '"role": "ADMIN"' "$TMP/audit/rbac.jsonl" && grep -q '"ring": "R4_HUMAN_SEAL"' "$TMP/audit/rbac.jsonl" && echo 1 || echo 0)" "authority check allows ADMIN human actor and audits ring"

"$GLAW" matter new "Authority Gate" >/dev/null
"$CHIEF" --chief "GLAW Chief Counsel" --decision "PROCEED" --signoff >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "Chief signoff blocks without human actor"
"$CHIEF" --chief "GLAW Chief Counsel" --decision "PROCEED" --signoff --human-authority "Alex Rivera, licensed attorney" --role ADMIN >/dev/null; rc=$?
ok "$([ "$rc" = 0 ] && grep -q '"human_authority_actor": "Alex Rivera, licensed attorney"' "$TMP/matters/authority-gate/decisions.jsonl" && echo 1 || echo 0)" "Chief signoff records human authority actor"

cat > "$TMP/1099.json" <<'JSON'
{
  "form_type": "1099-NEC",
  "tax_year": 2026,
  "payer": {
    "name": "Acme Inc.",
    "tin": "12-3456789",
    "address": {"street": "1 Main St", "city": "Miami", "state": "FL", "zip": "33101"}
  },
  "recipients": [
    {
      "name": "Vendor LLC",
      "tin": "98-7654321",
      "tin_type": "EIN",
      "amounts": {"box1_nonemployee_comp": 1000.0},
      "address": {"street": "2 Main St", "city": "Miami", "state": "FL", "zip": "33101"}
    }
  ]
}
JSON

"$IRS" submit "$TMP/1099.json" --live -o "$TMP" >/tmp/glaw-auth-irs.out 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'HUMAN AUTHORITY BLOCKED' /tmp/glaw-auth-irs.out && echo 1 || echo 0)" "IRS live submit blocks before transmission without human actor"

"$OVERSIGHT" halt --by "QA reviewer" --reason "live filing freeze" >/dev/null
"$IRS" submit "$TMP/1099.json" --live --human-authority "Alex Rivera, licensed attorney" --role ADMIN -o "$TMP" >/tmp/glaw-auth-irs-halt.out 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'OVERSIGHT BLOCKED' /tmp/glaw-auth-irs-halt.out && echo 1 || echo 0)" "IRS live submit blocks during Oversight Board halt even with ADMIN authority"
"$OVERSIGHT" resume --by "Alex Rivera" --role ADMIN --reason "test resume" >/dev/null
"$IRS" submit "$TMP/1099.json" --live --human-authority "Alex Rivera, licensed attorney" --role ADMIN -o "$TMP" >/tmp/glaw-auth-irs-ok.out 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && grep -q 'HUMAN AUTHORITY' /tmp/glaw-auth-irs-ok.out && echo 1 || echo 0)" "IRS live submit passes authority gate with human actor"

rm -rf "$TMP" /tmp/glaw-auth-role.out /tmp/glaw-auth-writer.out /tmp/glaw-auth-irs.out /tmp/glaw-auth-irs-halt.out /tmp/glaw-auth-irs-ok.out
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }
