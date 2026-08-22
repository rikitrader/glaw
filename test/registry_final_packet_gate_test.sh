#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
printf 'approved artifact\n' > "$TMP/artifact.md"
"$ROOT/bin/glaw-registry" init "$TMP/registry.jsonl" --registry-id REG-0001 --actor "GLAW Governor" >/dev/null
"$ROOT/bin/glaw-registry" register "$TMP/registry.jsonl" --artifact-id ART-0001 --kind artifact --path "$TMP/artifact.md" --department accounting-assurance --lane technical-accounting-memo --owner glaw-accounting --version v1 --risk-class high --actor "GLAW Governor" >/dev/null
"$ROOT/bin/glaw-registry" approve "$TMP/registry.jsonl" --artifact-id ART-0001 --decision approve --reviewer "Alex Rivera" --role "Controller" --rationale "Reviewed and approved." >/dev/null
python3 - "$ROOT" "$TMP" <<'PY'
import importlib.machinery
import importlib.util
import pathlib
import sys
root = pathlib.Path(sys.argv[1])
matter = pathlib.Path(sys.argv[2])
loader = importlib.machinery.SourceFileLoader("glaw_final_packet", str(root / "bin/glaw-final-packet"))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
manifest = module.registry_manifest(matter, root, {})
assert manifest["status"] == "pass", manifest
assert manifest["required"] is True
rows = {row["id"]: row for row in module.compliance_manifest(
    "accounting", {}, accounting_control={"status":"not_required"},
    government_adversary_rows=[], source_manifest=[], senior_review_evidence_manifest=[],
    red_flag_resolution_evidence_manifest=[], nonblocking_red_flags=[], reviewer_identity=[],
    report_quality_manifest=[], premium_lane_rows=[], premium_objective_audit={},
    materialized_source_ingest={}, registry_manifest=manifest,
)}
assert rows["enterprise-registry"]["status"] == "pass"
matter.joinpath("artifact.md").write_text("tampered\n")
manifest = module.registry_manifest(matter, root, {})
assert manifest["status"] == "fail", manifest
missing = module.registry_manifest(matter / "missing-matter", root, {"universal":{"registry_required":True}})
assert missing["status"] == "fail", missing
print("final-packet registry gate contract: ok")
PY
