#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
export PYTHONPATH="$ROOT/lib"

python3 - "$TMP" <<'PY'
import json, pathlib, sys
from legal_governor.claim_graph import validate_claims
from legal_governor.confidence import pass_threshold
from legal_governor.evaluation import summarize, wilson_interval
from legal_governor.premise import extract, validate
from legal_governor.quote_validator import validate as quote
from legal_governor.retrieval import hybrid

assert validate(extract("Because Delaware law guarantees founders permanent control."))
assert quote("not present", "authoritative text") == "NO_MATCH"
assert validate_claims([{"id":"C1","text":"rule","materiality":"HIGH","type":"LEGAL RULE","entailment":"NOT_SUPPORTED","supporting_source_ids":[]}])
assert pass_threshold({"retrievalCompleteness":"UNKNOWN"})[0] is False
assert hybrid("founder consent", [], [], semantic_results=None)["semantic_status"] == "UNAVAILABLE"
low, high = wilson_interval(0, 100)
assert 0 <= low <= high < 0.1
rows = [{"decision":"PASS","material_error":False} for _ in range(1000)]
assert summarize(rows)["acceptance"] is True
print("ALL PASS")
PY
