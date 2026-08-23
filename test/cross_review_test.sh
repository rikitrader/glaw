#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
RUN="$TMP/run"
mkdir -p "$RUN"
cat > "$RUN/snapshot.json" <<'JSON'
{"snapshot_id":"SNAP-1","matter_id":"M-1","shared_memory_hash":"a","source_set_hash":"b"}
JSON
cat > "$RUN/blue-first-pass.json" <<'JSON'
{"opinion_id":"OP-BLUE","claims":["position requires source review"]}
JSON
cat > "$RUN/red-first-pass.json" <<'JSON'
{"opinion_id":"OP-RED","claims":["position has a procedural risk"]}
JSON
"$ROOT/bin/glaw-cross-review" start --run-dir "$RUN" >/dev/null
python3 - "$RUN" "$ROOT/bin/glaw-cross-review" <<'PY'
import hashlib, json, subprocess, sys
from pathlib import Path
run, cli = Path(sys.argv[1]), sys.argv[2]
def state(): return json.loads((run / "cross-review.json").read_text())
def record(payload):
    p = run / "entry.json"
    p.write_text(json.dumps(payload))
    return subprocess.run([cli, "record", "--run-dir", str(run), "--input", str(p)], check=False, capture_output=True, text=True)
def hash_value(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
s = state()
rows = [{"phase":"RED_CROSS_REVIEW","actor":"victor_sterling","reviewer_id":"Victor-001","target_hash":s["blue_first_pass_hash"],"claims":["procedural risk requires response"],"evidence_refs":["SRC-1"],"unresolved_questions":["forum confirmation"],"decision":"OPEN"}]
assert record(rows[-1]).returncode == 0
rows.append({"phase":"BLUE_REBUTTAL","actor":"alexandra_vale","reviewer_id":"Alexandra-001","target_hash":hash_value(state()["phases"][-1]),"claims":["procedural risk is bounded"],"evidence_refs":["SRC-1"],"unresolved_questions":["forum confirmation"],"decision":"MAINTAINED"})
assert record(rows[-1]).returncode == 0
rows.append({"phase":"RED_SUR_REBUTTAL","actor":"victor_sterling","reviewer_id":"Victor-001","target_hash":hash_value(state()["phases"][-1]),"claims":["remaining uncertainty is material"],"evidence_refs":["SRC-1"],"unresolved_questions":["independent adjudication"],"decision":"MAINTAINED"})
assert record(rows[-1]).returncode == 0
rows.append({"phase":"ADJUDICATION","actor":"independent_adjudicator","reviewer_id":"Adjudicator-001","claims":["dispute is resolved for scoped question"],"evidence_refs":["SRC-1"],"unresolved_questions":["human counsel approval remains required"],"decision":"RESOLVED"})
assert record(rows[-1]).returncode == 0
r = subprocess.run([cli, "check", "--run-dir", str(run)], check=False, capture_output=True, text=True)
assert r.returncode == 0, r.stdout + r.stderr
assert json.loads(r.stdout)["status"] == "PASS"
print("cross-review protocol: ok")
PY
