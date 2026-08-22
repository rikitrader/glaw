#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLI="$ROOT/bin/glaw-transaction-comps"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/input.json" <<'JSON'
{"analysis_id":"TC-0001","currency":"USD","transactions":[
  {"transaction_id":"T1","target":"Alpha","enterprise_value":1000,"ltm_revenue":500,"ltm_ebitda":100,"source_ids":["SRC-1"]},
  {"transaction_id":"T2","target":"Beta","enterprise_value":1500,"ltm_revenue":600,"ltm_ebitda":150,"source_ids":["SRC-2"]},
  {"transaction_id":"T3","target":"Gamma","enterprise_value":1200,"ltm_revenue":600,"ltm_ebitda":100,"source_ids":["SRC-3"]}
]}
JSON

"$CLI" validate "$TMP/input.json" | rg '"valid": true'
"$CLI" analyze "$TMP/input.json" | rg '"median": 2.0'
"$CLI" analyze "$TMP/input.json" | rg '"median": 10.0'
echo "transaction comps contract: ok"
