#!/usr/bin/env bash
# gate_test.sh — regression test for bin/glaw-gate (the code-enforced hard gates).
# Zero spend. Isolates via a temp GLAW_HOME so it never touches real matters.
# Asserts: a guarded stage is BLOCKED (exit 1) until its prerequisite gate events are
# logged, then CLEAR (exit 0); unguarded stages are always clear.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
GATE="$HERE/../bin/glaw-gate"
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
M="$TMP/matters/m"; mkdir -p "$M"; : > "$M/timeline.jsonl"; echo m > "$TMP/.active"
log(){ printf '{"ts":"t","event":"%s"}\n' "$1" >> "$M/timeline.jsonl"; }
chk(){ "$GATE" check "$1" m >/dev/null 2>&1; echo $?; }   # echoes exit code

# unguarded transitions are always clear
ok "$([ "$(chk structure)" = 0 ] && echo 1 || echo 0)" "unguarded stage 'structure' is CLEAR"
ok "$([ "$(chk draft)" = 0 ] && echo 1 || echo 0)"     "unguarded stage 'draft' is CLEAR"

# intake + gate 1: strategy needs intake_complete and conflicts_cleared
ok "$([ "$(chk strategy)" = 1 ] && echo 1 || echo 0)" "strategy BLOCKED before intake_complete + conflicts_cleared"
log intake_complete
ok "$([ "$(chk strategy)" = 1 ] && echo 1 || echo 0)" "strategy STILL BLOCKED with only intake_complete"
log conflicts_cleared
ok "$([ "$(chk strategy)" = 0 ] && echo 1 || echo 0)" "strategy CLEAR after intake_complete + conflicts_cleared"

# file gate: citations, adversarial, red flags, final packet, and chief approval
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED with no file gates"
log citations_verified
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED with only citations_verified"
log adversarial_done
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED before red_flags_clear"
log red_flags_clear
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED before final_packet_ready"
log final_packet_ready
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED before chief_approved"
log chief_approved
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED before verified final packet artifacts"
cat > "$M/final_packet.json" <<'JSON'
{
  "status": "ready",
  "gates": {
    "intake_complete": true,
    "conflicts_cleared": true,
    "ethics_gate_complete": true,
    "citations_verified": true,
    "citation_gate_complete": true,
    "adversarial_done": true,
    "accounting_adversarial_complete": true,
    "accounting_council_complete": true,
    "red_flags_clear": true,
    "upl_footer_clear": true
  }
}
JSON
printf '{"final_gate":"approved"}\n' > "$M/decisions.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after all file gates"

ok "$([ "$(chk matter-retro)" = 1 ] && echo 1 || echo 0)" "matter-retro BLOCKED before docket gate"
log docket_gate_complete
ok "$([ "$(chk matter-retro)" = 1 ] && echo 1 || echo 0)" "matter-retro STILL BLOCKED before docket_done"
log docket_done
ok "$([ "$(chk matter-retro)" = 0 ] && echo 1 || echo 0)" "matter-retro CLEAR after docket completion"

# status reflects state
S="$("$GATE" status m 2>&1)"
ok "$(echo "$S" | grep -q '✅ conflicts_cleared' && echo 1 || echo 0)" "status shows conflicts_cleared ✅"
ok "$(echo "$S" | grep -q '✅ intake_complete' && echo 1 || echo 0)" "status shows intake_complete ✅"
ok "$(echo "$S" | grep -q '✅ adversarial_done' && echo 1 || echo 0)" "status shows adversarial_done ✅"
ok "$(echo "$S" | grep -q '✅ red_flags_clear' && echo 1 || echo 0)" "status shows red_flags_clear ✅"
ok "$(echo "$S" | grep -q '✅ final_packet_ready' && echo 1 || echo 0)" "status shows final_packet_ready ✅"
ok "$(echo "$S" | grep -q '✅ chief_approved' && echo 1 || echo 0)" "status shows chief_approved ✅"
ok "$(echo "$S" | grep -q '✅ docket_gate_complete' && echo 1 || echo 0)" "status shows docket_gate_complete ✅"
ok "$(echo "$S" | grep -q '✅ docket_done' && echo 1 || echo 0)" "status shows docket_done ✅"

# the live glaw 'stage' command refuses to advance past an unmet gate (integration)
GLAW_BIN="$HERE/../bin/glaw"
N="$TMP/matters/n"; mkdir -p "$N"; : > "$N/timeline.jsonl"; echo intake > "$N/.stage"; echo n > "$TMP/.active"
"$GLAW_BIN" stage strategy >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && [ "$(cat "$N/.stage")" = intake ] && echo 1 || echo 0)" "glaw stage refuses advance without intake/conflicts + leaves .stage unchanged"
"$GLAW_BIN" stage strategy --force >/dev/null 2>&1
ok "$([ "$(cat "$N/.stage")" = strategy ] && grep -q gate_override "$N/timeline.jsonl" && echo 1 || echo 0)" "glaw stage --force advances + logs gate_override"

F="$TMP/matters/f"; mkdir -p "$F"; : > "$F/timeline.jsonl"; echo draft > "$F/.stage"; echo f > "$TMP/.active"
"$GLAW_BIN" stage file --force >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && [ "$(cat "$F/.stage")" = draft ] && echo 1 || echo 0)" "glaw stage file --force refuses final filing"

rm -rf "$TMP"
echo
echo "${fail:-0} failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }
