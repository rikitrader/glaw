#!/usr/bin/env bash
# memory_test.sh - source-linked cross-matter memory and selective retrieval.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
LEARN="$ROOT/bin/glaw-learnings"
REFLECT="$ROOT/bin/glaw-reflect"

"$LEARN" add '{"error_class":"audit-gap","where":"test","wrong":"unsupported number","fix":"cite bank source","confidence":8}' >/tmp/glaw-memory-bad.out 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && grep -q 'source_links required' /tmp/glaw-memory-bad.out && echo 1 || echo 0)" "memory add blocks unsourced defect"

"$LEARN" add '{"error_class":"cite-caption","where":"matter/a","wrong":"case cited without reporter","fix":"verify caption and reporter","authority":"https://www.courtlistener.com/","confidence":9,"matter":"alpha-tax"}' >/dev/null
"$LEARN" add '{"error_class":"state-deadline","where":"matter/b","wrong":"deadline copied from memory","fix":"cite current state source","source_links":["matter:beta docket SRC-0001"],"confidence":8,"matter":"beta-docket"}' >/dev/null
"$LEARN" add '{"error_class":"scotus-misuse","where":"matter/c","wrong":"off-point Supreme Court authority","fix":"confirm holding supports proposition","authority":"https://www.courtlistener.com/","confidence":9,"matter":"gamma-litigation"}' >/dev/null
"$LEARN" add '{"error_class":"bank-rec-gap","where":"matter/d","wrong":"tie-out issue accepted without bank reconciliation","fix":"route to CFO and IRS audit reviewer before tax treatment","source_links":["matter:delta accounting SRC-0002"],"confidence":6,"matter":"delta-close","workflow_track":"accounting-tax"}' >/dev/null
"$LEARN" add '{"error_class":"trial-tieout-gap","where":"matter/e","wrong":"tie-out issue accepted without evidentiary foundation","fix":"route to trial counsel for exhibit and witness foundation","source_links":["matter:epsilon trial SRC-0003"],"confidence":10,"matter":"epsilon-trial","workflow_track":"litigation"}' >/dev/null
"$LEARN" add '{"error_class":"sec-disclosure-gap","where":"matter/f","wrong":"support issue accepted without 10-K and 8-K tie-out","fix":"route to SEC reporting and PCAOB reviewers before disclosure sign-off","source_links":["matter:zeta sec SRC-0004"],"confidence":6,"matter":"zeta-sec","workflow_track":"sec-reporting"}' >/dev/null
"$LEARN" add '{"error_class":"tax-return-gap","where":"matter/g","wrong":"support issue accepted without return-to-ledger tie-out","fix":"route to IRS audit reviewer and tax compliance before filing workpapers","source_links":["matter:eta tax SRC-0005"],"confidence":7,"matter":"eta-tax","workflow_track":"tax"}' >/dev/null
"$LEARN" add '{"error_class":"corpus-grounding-gap","where":"matter/h","wrong":"support issue accepted without trusted corpus segment","fix":"route to legal research for allowlisted corpus capture and groundedness audit","source_links":["matter:theta research SRC-0006"],"confidence":8,"matter":"theta-cites","workflow_track":"legal-research"}' >/dev/null

"$LEARN" query "reporter caption" --json > "$TMP/query.json"; rc=$?
python3 - "$TMP/query.json" <<'PY'
import json
import sys

rows = json.load(open(sys.argv[1], encoding="utf-8"))
ok = bool(rows) and rows[0].get("error_class") == "cite-caption" and rows[0].get("memory_id", "").startswith("MEM-")
ok = ok and rows[0].get("source_links")
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "memory query returns ranked source-linked result"

"$LEARN" preflight alpha-tax --query "citation reporter" > "$TMP/preflight.txt"; rc=$?
ok "$([ "$rc" = 0 ] && grep -q 'KNOWN DEFECTS' "$TMP/preflight.txt" && grep -q 'cite-caption' "$TMP/preflight.txt" && grep -q 'MEM-' "$TMP/preflight.txt" && echo 1 || echo 0)" "memory preflight emits source-linked digest"

"$LEARN" query "tie-out issue" --track accounting-tax --json > "$TMP/track-accounting.json"; rc=$?
python3 - "$TMP/track-accounting.json" <<'PY'
import json
import sys

rows = json.load(open(sys.argv[1], encoding="utf-8"))
ok = bool(rows) and rows[0].get("error_class") == "bank-rec-gap" and rows[0].get("score_track_boost") == 12
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "memory query weights accounting-tax workflow track"

"$LEARN" query "tie-out issue" --track litigation --json > "$TMP/track-litigation.json"; rc=$?
python3 - "$TMP/track-litigation.json" <<'PY'
import json
import sys

rows = json.load(open(sys.argv[1], encoding="utf-8"))
ok = bool(rows) and rows[0].get("error_class") == "trial-tieout-gap" and rows[0].get("score_track_boost") == 12
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "memory query weights litigation workflow track"

"$LEARN" preflight --query "tie-out issue" --track accounting-tax > "$TMP/preflight-track.txt"; rc=$?
ok "$([ "$rc" = 0 ] && grep -q 'bank-rec-gap' "$TMP/preflight-track.txt" && echo 1 || echo 0)" "memory preflight honors workflow-track weighting"

EVAL_SPEC='{"cases":[
  {"name":"sec-reporting support issue","query":"support issue","track":"sec-reporting","expect_error_class":"sec-disclosure-gap"},
  {"name":"tax support issue","query":"support issue","track":"tax","expect_error_class":"tax-return-gap"},
  {"name":"legal research support issue","query":"support issue","track":"legal-research","expect_error_class":"corpus-grounding-gap"},
  {"name":"accounting tie-out issue","query":"tie-out issue","track":"accounting-tax","expect_error_class":"bank-rec-gap"},
  {"name":"litigation tie-out issue","query":"tie-out issue","track":"litigation","expect_error_class":"trial-tieout-gap"}
]}'
"$LEARN" eval "$EVAL_SPEC" --json > "$TMP/eval.json"; rc=$?
python3 - "$TMP/eval.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
results = data.get("results", [])
ok = (
    data.get("status") == "pass"
    and data.get("passed") == 5
    and {row.get("got") for row in results} >= {
        "sec-disclosure-gap",
        "tax-return-gap",
        "corpus-grounding-gap",
        "bank-rec-gap",
        "trial-tieout-gap",
    }
    and all(row.get("score_track_boost") == 12 for row in results)
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "memory eval passes multi-department retrieval quality fixtures"

BAD_EVAL='{"cases":[{"name":"bad expected route","query":"support issue","track":"sec-reporting","expect_error_class":"tax-return-gap"}]}'
"$LEARN" eval "$BAD_EVAL" --json > "$TMP/eval-bad.json"; rc=$?
python3 - "$TMP/eval-bad.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
ok = data.get("status") == "fail" and data.get("failed") == 1
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "memory eval fails closed on wrong expected retrieval"

"$REFLECT" --apply > "$TMP/reflect.txt"; rc=$?
ok "$([ "$rc" = 0 ] && grep -q 'Wrote 1 new synthesized knowledge rules' "$TMP/reflect.txt" && grep -q 'Qdrant' "$TMP/reflect.txt" && echo 1 || echo 0)" "reflection writes source-linked synthesized rule in isolated store"

"$LEARN" query "cite discipline" --type knowledge --json > "$TMP/knowledge.json"; rc=$?
python3 - "$TMP/knowledge.json" <<'PY'
import json
import sys

rows = json.load(open(sys.argv[1], encoding="utf-8"))
ok = bool(rows) and rows[0].get("type") == "knowledge" and rows[0].get("source_links")
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "memory query retrieves synthesized knowledge by type"

"$LEARN" stats > "$TMP/stats.txt"; rc=$?
ok "$([ "$rc" = 0 ] && grep -q "store: $TMP/learnings/learnings.jsonl" "$TMP/stats.txt" && grep -q 'source-linked: 9/9' "$TMP/stats.txt" && echo 1 || echo 0)" "memory stats reports isolated source-linked store"

rm -rf "$TMP" /tmp/glaw-memory-bad.out
echo
echo "0 failures - $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS"; exit 0; } || { echo "FAILURES"; exit 1; }
