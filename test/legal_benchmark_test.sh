#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
export GLAW_BENCHMARK_HOME="$TMP/legal-10k"

"$ROOT/bin/glaw-legal-benchmark" scaffold >/dev/null
"$ROOT/bin/glaw-legal-benchmark" validate >/dev/null
cat > "$GLAW_BENCHMARK_HOME/source-packets.jsonl" <<'JSON'
{"id":"PACKET-DE-001","authority_ids":["SRC-DE-001"],"citation":"8 Del. C. §122(18)","jurisdiction":"US-DE","source_url":"https://delcode.delaware.gov/title8/Title8.pdf","verification_status":"primary_source_retrieved"}
JSON
"$ROOT/bin/glaw-legal-benchmark" split > "$TMP/split.json"
python3 - "$TMP/split.json" "$GLAW_BENCHMARK_HOME/items.jsonl" <<'PY'
import json, sys
split = json.load(open(sys.argv[1]))["counts"]
assert split == {"development": 7000, "calibration": 1000, "locked-evaluation": 2000}, split
rows = [json.loads(line) for line in open(sys.argv[2]) if line.strip()]
assert len(rows) == 10000
assert rows[0]["id"] == "BENCH-000001" and rows[-1]["id"] == "BENCH-010000"
assert all(row["status"] == "DRAFT" for row in rows)
assert sum(bool(row["trap_types"]) for row in rows) == 2000
PY

cat > "$TMP/reviewer-1.json" <<'JSON'
{"reviewer_id":"COUNSEL-001","role":"attorney","jurisdiction":"US-DE","conflict_attestation":true}
JSON
cat > "$TMP/reviewer-2.json" <<'JSON'
{"reviewer_id":"COUNSEL-002","role":"attorney","jurisdiction":"US-DE","conflict_attestation":true}
JSON
"$ROOT/bin/glaw-legal-benchmark" reviewer-register --input "$TMP/reviewer-1.json" >/dev/null
"$ROOT/bin/glaw-legal-benchmark" reviewer-register --input "$TMP/reviewer-2.json" >/dev/null
cat > "$TMP/import.jsonl" <<'JSON'
{"id":"BENCH-000001","question":"What is the verified rule?","jurisdiction":"US-DE","gold_authorities":["SRC-DE-001"],"source_packet_id":"PACKET-DE-001","materiality":"HIGH"}
JSON
"$ROOT/bin/glaw-legal-benchmark" import --input "$TMP/import.jsonl" >/dev/null
cat > "$TMP/review-1.json" <<'JSON'
{"benchmark_id":"BENCH-000001","reviewer_id":"COUNSEL-001","decision":"REVIEW_REQUIRED","authorities":["SRC-DE-001"],"reasoning_summary":"Source packet requires counsel review.","materiality":"HIGH","conflict_attestation":true}
JSON
cat > "$TMP/review-2.json" <<'JSON'
{"benchmark_id":"BENCH-000001","reviewer_id":"COUNSEL-002","decision":"REVIEW_REQUIRED","authorities":["SRC-DE-001"],"reasoning_summary":"Independent review reaches the same result.","materiality":"HIGH","conflict_attestation":true}
JSON
"$ROOT/bin/glaw-legal-benchmark" review --input "$TMP/review-1.json" >/dev/null
"$ROOT/bin/glaw-legal-benchmark" review --input "$TMP/review-2.json" >/dev/null
"$ROOT/bin/glaw-legal-benchmark" release >/dev/null
python3 - "$GLAW_BENCHMARK_HOME/items.jsonl" <<'PY'
import json, sys
row = next(json.loads(line) for line in open(sys.argv[1]) if json.loads(line).get("id") == "BENCH-000001")
assert row["status"] == "RELEASED"
assert row["gold_decision"] == "REVIEW_REQUIRED"
assert row["reviewer_1"] == "COUNSEL-001"
assert row["reviewer_2"] == "COUNSEL-002"
PY
echo "ALL PASS"
