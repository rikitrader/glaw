#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 - "$ROOT" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1])
required=("Identity:", "Soul:", "Domain:", "Report voice:", "Counter-lens:")
rows=[]
for path in sorted((root/"seats").glob("glaw-*/SKILL.md")):
    text=path.read_text(encoding="utf-8")
    missing=[field for field in required if field not in text]
    if missing: rows.append(f"{path.relative_to(root)} missing {', '.join(missing)}")
if rows:
    print("\n".join(rows)); raise SystemExit(1)
print(f"seat posture contract: {len(list((root/'seats').glob('glaw-*/SKILL.md')))} seats pass identity/soul/domain/report/counter-lens")
PY
