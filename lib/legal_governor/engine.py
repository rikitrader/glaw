"""Legal Governor orchestration: support and challenge must both clear."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from legal_governor import adverse_authority, authority_verifier, citation_validator, contradiction_engine
from legal_governor import enforceability, jurisdiction, mandatory_law, red_team
from legal_governor import parity, rag
from legal_governor.provenance import load as load_sources
from legal_governor.verification_bundle import validate as validate_bundle
from legal_governor.audit_log import append
from legal_governor.drafting_gate import evaluate as evaluate_drafting
from legal_governor.statuses import BLOCK, LEGAL_REVIEW_REQUIRED, PASS, PASS_WITH_RISK, public_status

REQUIRED_TOP = ("objective", "jurisdictions", "governing_documents", "mandatory_law", "supporting_authority", "adverse_authority", "red_team", "enforceability", "propositions", "citations", "independent_reviews", "verification_bundle")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def scaffold() -> dict[str, Any]:
    return {
        "schema": "glaw-legal-governor/v1",
        "objective": "",
        "jurisdictions": [{"governing_law": "", "forum": "", "court": "", "claim_or_task": "", "choice_of_law_basis": ""}],
        "governing_documents": [],
        "mandatory_law": {"status": "", "authorities": [], "unwaivable_rights": []},
        "supporting_authority": [],
        "adverse_authority": [],
        "red_team": {"completed_roles": [], "surviving_attacks": []},
        "enforceability": {},
        "propositions": [],
        "citations": [],
        "contradictions": [],
        "independent_reviews": {"proposition_agent": {"status": ""}, "challenge_agent": {"status": ""}},
        "verification_bundle": {"premises": [], "claims": [], "quotes": [], "holdings": [], "precedent_treatment": [], "temporal": [], "confidence_vector": {}},
        "rag_context_sha256": "",
        "agent_parity": "",
        "counsel_review": {"required": True, "reviewer": "", "status": "pending"},
    }


def assess(payload: dict[str, Any], source_map: dict[str, dict] | None = None) -> dict[str, Any]:
    failures: list[str] = []
    if payload.get("schema") != "glaw-legal-governor/v1":
        failures.append("schema must be glaw-legal-governor/v1")
    failures.extend(f"{key} is missing" for key in REQUIRED_TOP if payload.get(key) in (None, "", [], {}))
    for index, record in enumerate(payload.get("jurisdictions") or [], start=1):
        failures.extend(f"jurisdictions[{index}]: {item}" for item in jurisdiction.validate(record))
    failures.extend(mandatory_law.validate(payload.get("mandatory_law", {})))
    failures.extend(authority_verifier.validate(payload.get("propositions", [])))
    failures.extend(adverse_authority.validate(payload.get("supporting_authority", []), payload.get("adverse_authority", [])))
    failures.extend(red_team.validate(payload.get("red_team", {})))
    failures.extend(enforceability.validate(payload.get("enforceability", {})))
    failures.extend(citation_validator.validate(payload.get("citations", [])))
    failures.extend(contradiction_engine.validate(payload.get("contradictions", [])))
    failures.extend(validate_bundle(payload.get("verification_bundle", {}), source_map or {}))
    if not str(payload.get("rag_context_sha256", "")).strip():
        failures.append("RAG context digest is missing")
    if payload.get("agent_parity") != "pass":
        failures.append("Claude/Codex parity is not verified")
    reviews = payload.get("independent_reviews", {})
    if reviews.get("proposition_agent", {}).get("status") not in {"complete", "pass"}:
        failures.append("proposition agent review is incomplete")
    if reviews.get("challenge_agent", {}).get("status") not in {"complete", "pass"}:
        failures.append("challenge agent review is incomplete")
    component_statuses = {"legal_governor": LEGAL_REVIEW_REQUIRED if failures else PASS_WITH_RISK}
    internal_status = BLOCK if any("missing" in item or "unverified" in item for item in failures) else (LEGAL_REVIEW_REQUIRED if failures else PASS_WITH_RISK)
    report = {
        "schema": "glaw-legal-governor-report/v1",
        "issued_at": _now(),
        "objective": payload.get("objective"),
        "internal_status": internal_status,
        "component_statuses": component_statuses,
        "status": public_status(internal_status, counsel_required=True),
        "drafting": {},
        "failures": sorted(set(failures)),
        "required_labels": ["CURRENT LAW", "BEST CLIENT ARGUMENT", "BEST OPPOSING ARGUMENT", "LIKELY JUDICIAL RESPONSE"],
        "authority_rule": "UNVERIFIED — DO NOT RELY",
        "counsel_review": {"required": True, "status": "pending"},
        "rag_context_sha256": payload.get("rag_context_sha256", ""),
        "agent_parity": payload.get("agent_parity", "missing"),
    }
    report["drafting"] = evaluate_drafting(report)
    return report


def draft_gate(report: dict[str, Any]) -> dict[str, Any]:
    return evaluate_drafting(report)


def write_assessment(matter: Path, payload: dict[str, Any]) -> dict[str, Any]:
    rag_result = rag.verify(matter)
    parity_result = parity.verify(matter)
    payload = dict(payload)
    if rag_result.get("status") == "PASS":
        payload["rag_context_sha256"] = rag_result.get("context_sha256", "")
    if parity_result.get("status") == "PASS":
        payload["agent_parity"] = "pass"
    source_map = {str(row.get("id")): row for row in load_sources(matter)}
    payload["verification_bundle"] = dict(payload.get("verification_bundle") or {})
    payload["verification_bundle"].setdefault("source_count", len(source_map))
    report = assess(payload, source_map)
    workpapers = matter / "workpapers"
    workpapers.mkdir(parents=True, exist_ok=True)
    (workpapers / "legal-governor-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    append(matter / "workpapers" / "legal-governor-audit.jsonl", {"event": "legal_governor_assessment", "status": report["status"], "failures": report["failures"]})
    return report
