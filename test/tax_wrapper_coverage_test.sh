#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$ROOT/test/tax_wrapper_coverage.json"
GOLDEN="$ROOT/test/tax_wrapper_golden_test.sh"

python3 - "$ROOT" "$MANIFEST" "$GOLDEN" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
manifest = Path(sys.argv[2])
golden = Path(sys.argv[3])
rows = json.loads(manifest.read_text(encoding="utf-8"))
golden_text = golden.read_text(encoding="utf-8")

required = {
    "glaw-scorp-aaa",
    "glaw-partner-basis",
    "glaw-subpart-f",
    "glaw-combined-unitary",
    "glaw-tfrp",
    "glaw-ptet",
    "glaw-oic",
    "glaw-sfr",
    "glaw-wbo-award",
    "glaw-qm",
}
seen = set()
failures = []

if not rows:
    failures.append("coverage manifest is empty")

for idx, row in enumerate(rows, start=1):
    wrapper = row.get("wrapper", "")
    module = row.get("module", "")
    coverage = row.get("coverage", "")
    evidence = row.get("evidence", "")
    if wrapper in seen:
        failures.append(f"duplicate wrapper in manifest: {wrapper}")
    seen.add(wrapper)
    if not wrapper.startswith("glaw-"):
        failures.append(f"row {idx} wrapper must be a glaw-* command")
    if not (root / "bin" / wrapper).exists():
        failures.append(f"{wrapper} missing bin wrapper")
    if module != "inline" and not (root / "lib" / "bookkeeping" / module).exists():
        failures.append(f"{wrapper} module missing: {module}")
    evidence_paths = [item.strip() for item in evidence.split(";") if item.strip()]
    if not evidence_paths:
        failures.append(f"{wrapper} has no coverage evidence")
    for rel in evidence_paths:
        path = root / rel
        if not path.exists():
            failures.append(f"{wrapper} evidence missing: {rel}")
    if "wrapper-golden" in coverage and wrapper not in golden_text:
        failures.append(f"{wrapper} claims wrapper-golden coverage but is absent from tax_wrapper_golden_test.sh")
    if "lib-engine" in coverage:
        module_stem = Path(module).stem
        evidence_text = "\n".join((root / rel).read_text(encoding="utf-8") for rel in evidence_paths if (root / rel).exists())
        if module_stem not in evidence_text:
            failures.append(f"{wrapper} claims lib-engine coverage but evidence does not reference {module_stem}")
    if coverage not in {"wrapper-golden", "lib-engine", "wrapper-golden+lib-engine"}:
        failures.append(f"{wrapper} has unsupported coverage type: {coverage}")

missing_required = sorted(required - seen)
if missing_required:
    failures.append("manifest missing H-10 representative wrappers: " + ", ".join(missing_required))

if failures:
    print("\n".join("FAIL: " + item for item in failures), file=sys.stderr)
    raise SystemExit(1)

print(f"{len(rows)} passed; {len(required)} H-10 representative wrappers locked")
PY
