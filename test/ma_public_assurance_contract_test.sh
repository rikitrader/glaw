#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

python3 - "$ROOT" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
catalog = json.loads((root / "lib/lane-catalog.json").read_text())
missing = []
for dept, entries in catalog["departments"].items():
    for item in entries:
        path = root / "seats" / item["seat"] / "SKILL.md"
        if not path.exists(): missing.append(str(path))
        else:
            text = path.read_text()
            if f"name: {item['seat']}" not in text: missing.append(f"name mismatch: {path}")
if missing:
    print("\n".join(missing)); raise SystemExit(1)
print("catalog seats: ok")
PY

"$ROOT/bin/glaw-lane" scaffold --lane-id LANE-0002 --matter DEAL-0001 --department public-markets --lane earnings-communications --owner ir-seat --artifact-type earnings-release > "$TMP/lane.json"
"$ROOT/bin/glaw-lane" validate "$TMP/lane.json" | rg '"valid": true'
printf 'artifact fixture\n' > "$TMP/release.md"
"$ROOT/bin/glaw-artifact" manifest --manifest-id MAN-0001 --lane-id LANE-0002 "$TMP/release.md" > "$TMP/manifest.json"
"$ROOT/bin/glaw-artifact" validate "$TMP/manifest.json" | rg '"valid": true'
echo "M&A/public-markets/assurance contract: ok"
