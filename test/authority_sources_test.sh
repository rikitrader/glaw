#!/usr/bin/env bash
# authority_sources_test.sh - approved authority-source catalog contract.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
CORPUS="$ROOT/bin/glaw-citation-corpus"

"$CORPUS" sources --json > "$TMP/sources.json"; rc=$?
python3 - "$TMP/sources.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
sources = {row["id"]: row for row in data["sources"]}
required = {"us-code", "ecfr", "govinfo", "irs", "sec", "pcaob", "fasb", "courtlistener"}
domains = {domain for row in sources.values() for domain in row["domains"]}
checks = [
    required <= set(sources),
    {"irs.gov", "sec.gov", "pcaobus.org", "fasb.org", "asc.fasb.org"} <= domains,
]
sys.exit(0 if all(checks) else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "authority source catalog includes IRS/SEC/PCAOB/FASB/legal corpus sources"

"$CORPUS" sources --profile sec-reporting --json > "$TMP/sec-sources.json"; rc=$?
python3 - "$TMP/sec-sources.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
ids = {row["id"] for row in data["sources"]}
sys.exit(0 if {"sec", "pcaob", "fasb", "ecfr"} <= ids and "irs" not in ids else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "SEC-reporting source profile routes to SEC/PCAOB/FASB/eCFR"

"$CORPUS" sources --profile accounting-tax --json > "$TMP/accounting-tax-sources.json"; rc=$?
python3 - "$TMP/accounting-tax-sources.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
ids = {row["id"] for row in data["sources"]}
sys.exit(0 if {"irs", "sec", "pcaob", "fasb", "us-code"} <= ids else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "accounting-tax source profile includes tax, SEC, audit, GAAP, and statute sources"

"$GLAW" matter new "Authority Sources" >/dev/null
printf '%s\n' "PCAOB auditing standards source segment for issuer audit evidence." > "$TMP/pcaob.txt"
"$CORPUS" capture --id PCAOB-1 --source-url "https://pcaobus.org/oversight/standards" \
  --file "$TMP/pcaob.txt" --authenticated-copy \
  --segment "auditing standards source segment" >/dev/null; rc=$?
python3 - "$TMP/matters/authority-sources/citation_corpus.jsonl" <<'PY'
import json
import sys

row = json.loads(open(sys.argv[1], encoding="utf-8").read().splitlines()[-1])
checks = [
    row.get("trust_level") == "authenticated-copy",
    row.get("authority_source_id") == "pcaob",
    row.get("authority_source_kind") == "audit-authority",
    row.get("approved_authority_source") is True,
]
sys.exit(0 if all(checks) else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "PCAOB official-copy capture is approved and source-classified"

GLAW_AUTHORITY_DOMAINS="example.com" "$CORPUS" sources --json > "$TMP/sources-env.json"; rc=$?
python3 - "$TMP/sources-env.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
domains = {domain for row in data["sources"] for domain in row["domains"]}
sys.exit(0 if "example.com" not in domains else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "runtime environment cannot add authority-source domains"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }
