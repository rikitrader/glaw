#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
python3 - "$ROOT" "$TMP" <<'PY'
import json, pathlib, subprocess, sys
root, tmp = map(pathlib.Path, sys.argv[1:])
catalog = json.loads((root / "lib/lane-catalog.json").read_text())
n = 0
for department, items in catalog["departments"].items():
    for item in items:
        n += 1
        out = tmp / f"{n}.json"
        with out.open("w") as fh:
            subprocess.run([str(root / "bin/glaw-lane"), "scaffold", "--lane-id", f"LANE-{n:04d}", "--matter", "MAT-0001", "--department", department, "--lane", item["name"], "--owner", item["seat"], "--artifact-type", item["record_type"]], check=True, stdout=fh)
        subprocess.run([str(root / "bin/glaw-lane"), "validate", str(out)], check=True, stdout=subprocess.DEVNULL)
print(f"all lane contracts: {n} ok")
PY
