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

# gate 1: strategy needs conflicts_cleared
ok "$([ "$(chk strategy)" = 1 ] && echo 1 || echo 0)" "strategy BLOCKED before conflicts_cleared"
log conflicts_cleared
ok "$([ "$(chk strategy)" = 0 ] && echo 1 || echo 0)" "strategy CLEAR after conflicts_cleared"

# gates 2+3: file needs citations_verified AND adversarial_done
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED with neither cites nor adversarial"
log citations_verified
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED with only citations_verified"
log adversarial_done
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after both citations_verified + adversarial_done"

# status reflects state
S="$("$GATE" status m 2>&1)"
ok "$(echo "$S" | grep -q '✅ conflicts_cleared' && echo 1 || echo 0)" "status shows conflicts_cleared ✅"
ok "$(echo "$S" | grep -q '✅ adversarial_done' && echo 1 || echo 0)" "status shows adversarial_done ✅"

# the live glaw 'stage' command refuses to advance past an unmet gate (integration)
GLAW_BIN="$HERE/../bin/glaw"
N="$TMP/matters/n"; mkdir -p "$N"; : > "$N/timeline.jsonl"; echo intake > "$N/.stage"; echo n > "$TMP/.active"
"$GLAW_BIN" stage strategy >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && [ "$(cat "$N/.stage")" = intake ] && echo 1 || echo 0)" "glaw stage refuses advance + leaves .stage unchanged"
"$GLAW_BIN" stage strategy --force >/dev/null 2>&1
ok "$([ "$(cat "$N/.stage")" = strategy ] && grep -q gate_override "$N/timeline.jsonl" && echo 1 || echo 0)" "glaw stage --force advances + logs gate_override"

rm -rf "$TMP"
echo
echo "${fail:-0} failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }
