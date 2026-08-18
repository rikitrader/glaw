"""Final-packet/file gate for the Legal Governor chain.

The gate is fail-closed when a matter opts into governed analysis. Legacy
matters remain readable until explicitly activated by the intake flag or the
dependency matrix command; once activated, missing or stale evidence blocks.
"""
from __future__ import annotations

import json
from pathlib import Path

from legal_governor.parity import verify as verify_parity
from legal_governor.rag import verify as verify_rag
from legal_governor.provenance import load as load_sources
from legal_governor.verification_bundle import validate as validate_bundle


def _read(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def required(matter: Path) -> bool:
    intake = _read(matter / "intake.json")
    matrix = matter / "workpapers" / "dependency-matrix.json"
    return intake.get("legal_governor_required") is True or matrix.is_file()


def evaluate(matter: Path) -> dict:
    active = required(matter)
    if not active:
        return {"status": "not_required", "required": False, "failures": [], "context_sha256": ""}
    failures: list[str] = []
    rag = verify_rag(matter)
    parity = verify_parity(matter)
    report_path = matter / "workpapers" / "legal-governor-report.json"
    report = _read(report_path)
    bundle_path = matter / "workpapers" / "verification-bundle.json"
    bundle = _read(bundle_path)
    bundle_failures = validate_bundle(bundle, {str(row.get("id")): row for row in load_sources(matter)})
    if rag.get("status") != "PASS":
        failures.extend(f"rag:{item}" for item in rag.get("failures", []))
    if parity.get("status") != "PASS":
        failures.extend(f"parity:{item}" for item in parity.get("failures", []))
    if not report_path.is_file():
        failures.append("legal-governor report is missing")
    elif not report:
        failures.append("legal-governor report is invalid JSON")
    else:
        if report.get("drafting", {}).get("status") != "PASS":
            failures.append("legal-governor drafting gate is not PASS")
        if report.get("rag_context_sha256") != rag.get("context_sha256"):
            failures.append("legal-governor report is not bound to current RAG context")
        if report.get("agent_parity") != "pass":
            failures.append("legal-governor report does not record Claude/Codex parity")
    if not bundle_path.is_file():
        failures.append("verification bundle is missing")
    failures.extend(f"verification:{item}" for item in bundle_failures)
    return {
        "status": "pass" if not failures else "fail",
        "required": True,
        "failures": sorted(set(failures)),
        "context_sha256": rag.get("context_sha256", ""),
        "rag": rag,
        "parity": parity,
        "report_path": str(report_path.relative_to(matter)) if report_path.exists() else "workpapers/legal-governor-report.json",
        "verification_bundle_path": str(bundle_path.relative_to(matter)) if bundle_path.exists() else "workpapers/verification-bundle.json",
    }
