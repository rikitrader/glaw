#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 - "$ROOT" <<'PY'
import json, sys
from pathlib import Path
root=Path(sys.argv[1])
d=json.loads((root/"lib/deploy-parity-exceptions.json").read_text())
assert d["schema"] == "glaw-deploy-parity-exceptions/v1"
row=next(x for x in d["exceptions"] if x["command"] == "glaw-asylum-sworn-statement")
assert row["production_reliance"] == "blocked_until_reconciled"
for key in ("owner","reason","review_by","source"):
    assert row[key]
print("ALL PASS")
PY
