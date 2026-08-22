#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 - "$ROOT" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
mapping = json.loads((root / "lib/prophet-actuary-agent-map.json").read_text())
catalog = json.loads((root / "lib/lane-catalog.json").read_text())["departments"]["actuarial-risk"]
posture = mapping["professional_posture"]
lanes = {row["name"] for row in catalog}
agents = mapping["agents"]
assert len(agents) == 38
assert {row["id"] for row in agents} == {f"AGENT-{i:02d}" for i in range(38)}
assert all(row["seat"].startswith("glaw-actuary-") for row in agents)
assert all(lane in lanes for row in agents for lane in row["lanes"])
assert {"AGENT-00", "AGENT-20", "AGENT-26", "AGENT-37"}.issubset({row["id"] for row in agents})
assert {"Actuarial Science", "Mathematics", "Statistics", "Risk Management", "related field"}.issubset(set(posture["education"]))
assert {"ASA", "ACAS"}.issubset(set(posture["credentials"]))
assert posture["human_review_required_for_material_production_use"] is True
assert posture["qualification_verification_required"] is True
print("prophet-actuary agent map: 38 agents covered")
PY
