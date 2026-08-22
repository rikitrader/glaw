#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
REQ="$ROOT/test/fixtures/prophet_pipeline_request.json"

"$ROOT/bin/glaw-prophet-pipeline" validate "$REQ" > "$TMP/valid.json"
"$ROOT/bin/glaw-prophet-pipeline" run "$REQ" --workers 2 > "$TMP/result.json"
python3 - "$TMP/valid.json" "$TMP/result.json" <<'PY'
import json, sys
valid, result = [json.load(open(path)) for path in sys.argv[1:]]
assert valid["valid"] is True
assert result["schema_version"] == "prophet-results/v1"
assert result["status"] == "REVIEW"
assert result["data_integration"]["source_count"] == 1
assert result["data_integration"]["policy_count"] == 2
assert result["calculation"]["capabilities"]["multithreading"] is True
assert result["calculation"]["capabilities"]["avx_cpus"] is False
assert result["calculation"]["capabilities"]["gpu_acceleration"] is False
assert len(result["scenarios"]["deterministic"]) == 2
assert result["scenarios"]["stochastic"]["seed"] == 42
assert result["scenarios"]["stochastic"]["iterations"] == 25
assert "duration_gap" in result["alm"]
assert result["reporting"]["ifrs17"]["status"] == "prepared_for_review"
assert result["reporting"]["gl"]["journal_posting"] == "BLOCKED_PENDING_ACCOUNTING_MAPPING"
assert result["release_gate"]["qualified_actuary_required"] is True
PY

if "$ROOT/bin/glaw-prophet-pipeline" run "$REQ" --workers 0 >/dev/null 2>&1; then exit 1; fi
python3 - "$TMP/external.json" "$REQ" <<'PY'
import json, sys
data = json.load(open(sys.argv[2])); data["provider"] = "external-prophet"; json.dump(data, open(sys.argv[1], "w"))
PY
if "$ROOT/bin/glaw-prophet-pipeline" run "$TMP/external.json" >/dev/null 2>&1; then exit 1; fi
echo "prophet pipeline contract tests passed"
