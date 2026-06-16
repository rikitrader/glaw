#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass=0
fail(){ echo "FAIL: $1" >&2; exit 1; }
ok(){ pass=$((pass+1)); }

"$ROOT/bin/glaw-constitution-score" scaffold > "$TMP/scaffold.json"
python3 -m json.tool "$TMP/scaffold.json" >/dev/null
"$ROOT/bin/glaw-constitution-score" "$TMP/scaffold.json" --json > "$TMP/report.json" || true
python3 - "$TMP/report.json" <<'PY'
import json, sys
r=json.load(open(sys.argv[1]))
assert r["scrutiny_tier"] == "strict", r
assert "civil-liberties challenger" in r["adversarial_lenses"], r
assert "authorized human" in r["human_authority_boundary"], r
assert r["status"] == "blocked", r
PY
ok

printf '{"matter":"no-source","government_actor":true,"legitimate_interest":"safety"}' > "$TMP/no-source.json"
if "$ROOT/bin/glaw-constitution-score" "$TMP/no-source.json" --json > "$TMP/no-source-report.json"; then
  fail "missing source support should fail closed"
fi
grep -q "missing SRC-#### source support" "$TMP/no-source-report.json"
ok

cat > "$TMP/clean.json" <<'JSON'
{
  "matter": "clean-rational-basis",
  "sources": ["SRC-0001"],
  "government_actor": true,
  "legitimate_interest": "administrative efficiency",
  "nexus_evidence": "SRC-0001 record evidence supports the classification",
  "tailoring_evidence": "SRC-0001 narrow timing rule",
  "less_restrictive_means_analyzed": true
}
JSON
"$ROOT/bin/glaw-constitution-score" "$TMP/clean.json" --json > "$TMP/clean-report.json"
python3 - "$TMP/clean-report.json" <<'PY'
import json, sys
r=json.load(open(sys.argv[1]))
assert r["status"] == "pass", r
assert r["scrutiny_tier"] == "rational-basis", r
assert r["source_ids"] == ["SRC-0001"], r
PY
ok

echo "$pass passed"
