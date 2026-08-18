"""Fail-closed Alexandra Vale / Victor Sterling review orchestration.

These are application-level professional constitutions, not people or licensed
attorneys. Provider output is evidence for verification, never legal authority.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import IntEnum
from pathlib import Path
from typing import Any

from legal_governor.audit_log import append
from legal_governor.providers import ProviderResultStatus, configured_agent_provider, provider_for


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


class AttackLevel(IntEnum):
    ROUTINE = 1
    SKEPTICAL = 2
    LITIGATION_READY = 3
    HOSTILE_COUNSEL = 4
    EXISTENTIAL_RED_TEAM = 5


@dataclass(frozen=True)
class AgentConstitution:
    agent_id: str
    display_name: str
    role: str
    team: str
    mission: str
    posture: str
    non_negotiable_rules: tuple[str, ...]
    permitted_actions: tuple[str, ...]
    prohibited_actions: tuple[str, ...]
    default_attack_level: int
    constitution_version: str = "1.0"


ALEXANDRA = AgentConstitution(
    "alexandra_vale", "Alexandra Vale", "Chief Defense & Structural Counsel", "BLUE",
    "Build and strengthen the strongest legally supportable position.",
    "Aggressive, precise, skeptical, structural, litigation-aware, source-driven.",
    ("Never fabricate law, facts, quotations, or certainty.", "Separate advocacy from current law.", "Preserve adverse authority.", "Never override the Legal Governor."),
    ("read_shared", "read_blue_private", "search_sources", "write_blue_private", "write_blue_opinion"),
    ("read_red_private", "write_shared", "write_governor", "declare_authority_verified"),
    int(AttackLevel.HOSTILE_COUNSEL),
)

VICTOR = AgentConstitution(
    "victor_sterling", "Victor Sterling", "Chief Adversarial & Litigation Counsel", "RED",
    "Defeat, invalidate, narrow, or materially weaken the proposed position.",
    "Hostile, relentless, procedural, evidentiary, technical, source-driven.",
    ("Assume the preferred conclusion may be wrong.", "Never fabricate law, facts, quotations, or certainty.", "Search independently for adverse authority.", "Never override the Legal Governor."),
    ("read_shared", "read_red_private", "search_sources", "write_red_private", "write_red_opinion"),
    ("read_blue_private", "write_shared", "write_governor", "declare_authority_verified"),
    int(AttackLevel.EXISTENTIAL_RED_TEAM),
)

SPECIALISTS = {
    "alexandra_vale": ("BLUE-CORP", "BLUE-LIT", "BLUE-APP", "BLUE-REM"),
    "victor_sterling": ("RED-INV", "RED-PROC", "RED-AUTH", "RED-EVID"),
}


@dataclass
class MemoryItem:
    memory_id: str
    matter_id: str
    category: str
    content: str
    epistemic_status: str
    source_id: str | None = None
    source_hash: str | None = None
    source_location: str | None = None
    created_at: str = field(default_factory=now)
    verified_at: str | None = None
    verified_by: str | None = None
    jurisdiction: str | None = None
    relevant_date: str | None = None
    superseded: bool = False
    superseded_by: str | None = None
    confidence_class: str = "UNVERIFIED"
    tags: list[str] = field(default_factory=list)


@dataclass
class SharedMatterMemory:
    matter_id: str
    verified_facts: list[MemoryItem] = field(default_factory=list)
    disputed_facts: list[MemoryItem] = field(default_factory=list)
    client_allegations: list[MemoryItem] = field(default_factory=list)
    governing_documents: list[MemoryItem] = field(default_factory=list)
    verified_authorities: list[MemoryItem] = field(default_factory=list)
    adverse_authorities: list[MemoryItem] = field(default_factory=list)
    procedural_history: list[MemoryItem] = field(default_factory=list)
    court_orders: list[MemoryItem] = field(default_factory=list)
    evidence: list[MemoryItem] = field(default_factory=list)
    unresolved_questions: list[MemoryItem] = field(default_factory=list)
    governor_determinations: list[MemoryItem] = field(default_factory=list)


@dataclass
class PrivateMemory:
    matter_id: str
    owner: str
    items: list[MemoryItem] = field(default_factory=list)


@dataclass(frozen=True)
class MatterSnapshot:
    snapshot_id: str
    matter_id: str
    shared_memory_hash: str
    source_set_hash: str
    governing_document_hashes: tuple[str, ...]
    created_at: str


@dataclass
class AgentRun:
    run_id: str
    matter_id: str
    agent_id: str
    phase: str
    snapshot_id: str
    provider: str
    model: str
    prompt_version: str
    started_at: str
    completed_at: str | None = None
    status: str = "STARTED"
    input_hash: str = ""
    output_hash: str | None = None
    structured_output_id: str | None = None
    error_code: str | None = None
    mode: str | None = None
    cli_version: str | None = None
    exit_code: int | None = None
    timed_out: bool = False
    fallback_used: bool = False


class MemoryFirewall:
    """Repository-level access control; prompts are not the security boundary."""
    def __init__(self, shared: SharedMatterMemory, blue: PrivateMemory, red: PrivateMemory):
        self.shared, self.blue, self.red = shared, blue, red

    def read(self, agent_id: str, domain: str) -> Any:
        allowed = {"alexandra_vale": {"shared", "blue_private"}, "victor_sterling": {"shared", "red_private"}}
        if domain not in allowed.get(agent_id, set()):
            raise PermissionError(f"{agent_id} cannot read {domain}")
        return {"shared": self.shared, "blue_private": self.blue, "red_private": self.red}[domain]

    def write(self, agent_id: str, domain: str, item: MemoryItem) -> None:
        expected = "blue_private" if agent_id == "alexandra_vale" else "red_private"
        if domain != expected:
            raise PermissionError(f"{agent_id} cannot write {domain}")
        (self.blue if domain == "blue_private" else self.red).items.append(item)

    def promote(self, item: MemoryItem) -> None:
        if item.epistemic_status not in {"VERIFIED_FACT", "LEGAL_RULE"}:
            raise ValueError("private finding requires verification before shared-memory promotion")
        if not item.source_id or not item.source_hash or not item.verified_by:
            raise ValueError("verified shared memory requires source_id, source_hash, and verified_by")
        self.shared.verified_authorities.append(item)


def _json(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {k: _json(v) for k, v in asdict(value).items()}
    if isinstance(value, dict): return {k: _json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [_json(v) for v in value]
    return value


def create_snapshot(matter_id: str, shared: SharedMatterMemory, source_packets: list[dict], documents: list[dict]) -> MatterSnapshot:
    shared_hash, source_hash = digest(_json(shared)), digest(source_packets)
    docs = tuple(digest(row) for row in documents)
    return MatterSnapshot(f"SNAP-{digest([matter_id, shared_hash, source_hash])[:16]}", matter_id, shared_hash, source_hash, docs, now())


def _request(agent: AgentConstitution, question: str, packet: dict, snapshot: MatterSnapshot) -> dict:
    # Retrieved/source text is data, not executable instructions.
    return {"agent_id": agent.agent_id, "constitution_version": agent.constitution_version, "mission": agent.mission, "rules": list(agent.non_negotiable_rules), "phase": "INDEPENDENT_FIRST_PASS", "snapshot_id": snapshot.snapshot_id, "matter_id": snapshot.matter_id, "question": question, "source_packet": {"id": packet.get("id"), "authority_ids": packet.get("authority_ids", []), "source_url": packet.get("source_url"), "verification_status": packet.get("verification_status")}, "output_schema": "structured_opinion_only; proposed authorities remain unverified"}


def _unavailable(agent: AgentConstitution, question: str, snapshot: MatterSnapshot, error: str) -> dict:
    base = {"opinion_id": f"OP-{agent.team}-{digest([snapshot.snapshot_id, question, agent.agent_id])[:16]}", "matter_id": snapshot.matter_id, "snapshot_id": snapshot.snapshot_id, "agent_id": agent.agent_id, "generated_at": now(), "status": "AGENT_UNAVAILABLE", "provider_error": error, "claims": [], "supporting_authorities": [], "adverse_authorities": [], "unresolved_questions": ["Provider execution is unavailable; counsel review required."], "recommended_governor_status": "REVIEW_REQUIRED"}
    if agent.team == "BLUE": base.update({"objective": question, "proposed_position": None, "factual_dependencies": [], "legal_dependencies": [], "structural_recommendations": [], "fallback_positions": [], "remedy_strategy": [], "material_risks": []})
    else: base.update({"target_position": question, "attack_theories": [], "factual_attacks": [], "procedural_attacks": [], "evidentiary_attacks": [], "remedy_attacks": [], "catastrophic_failure_modes": []})
    base["output_hash"] = digest(base)
    return base


def _first_pass(agent: AgentConstitution, provider_name: str, question: str, packet: dict, snapshot: MatterSnapshot, outdir: Path) -> tuple[dict, AgentRun]:
    request = _request(agent, question, packet, snapshot)
    configured = configured_agent_provider(agent.agent_id) if provider_name == "configured" else provider_for(provider_name, os.environ.get("ALEXANDRA_MODE" if agent.agent_id == "alexandra_vale" else "VICTOR_MODE", "subscription_cli"))
    run = AgentRun(f"RUN-{agent.team}-{digest([snapshot.snapshot_id, question])[:16]}", snapshot.matter_id, agent.agent_id, "INDEPENDENT_FIRST_PASS", snapshot.snapshot_id, configured.name, "unreported", "dual-attorney-v1", now(), input_hash=digest(request))
    try:
        string_array = {"type": "array", "items": {"type": "string"}}
        schema = {"type": "object", "properties": {"claims": string_array, "supporting_authorities": string_array, "adverse_authorities": string_array, "assumptions": string_array, "uncertainties": string_array, "risk_findings": string_array, "recommended_status": {"type": "string"}}, "required": ["claims", "supporting_authorities", "adverse_authorities", "uncertainties", "recommended_status"]}
        provider_result = configured.analyze(json.dumps(request, sort_keys=True), matter_id=snapshot.matter_id, agent_id=agent.agent_id, output_schema=schema)
        run.mode = getattr(provider_result, "mode", None)
        run.model = getattr(provider_result, "model", None) or run.model
        run.cli_version = getattr(provider_result, "cli_version", None)
        run.exit_code = getattr(provider_result, "exit_code", None)
        run.timed_out = getattr(provider_result, "status", None) == ProviderResultStatus.TIMEOUT.value
        run.fallback_used = bool(getattr(provider_result, "fallback_used", False))
        if not hasattr(provider_result, "status") or provider_result.status != ProviderResultStatus.SUCCESS.value:
            error = getattr(provider_result, "error_message", None) or getattr(provider_result, "error_code", None) or "provider did not return a successful structured result"
            opinion = _unavailable(agent, question, snapshot, error)
            run.status = "AGENT_UNAVAILABLE" if getattr(provider_result, "status", "") in {ProviderResultStatus.AUTH_REQUIRED.value, ProviderResultStatus.CLI_NOT_FOUND.value, ProviderResultStatus.UNAVAILABLE.value, ProviderResultStatus.API_KEY_MISSING.value} else "INVALID_PROVIDER_OUTPUT"
            run.error_code = getattr(provider_result, "error_code", None) or getattr(provider_result, "status", "PROVIDER_ERROR")
            run.output_hash = opinion["output_hash"]
        else:
            opinion = provider_result.parsed_output or {}
            opinion.update({"opinion_id": f"OP-{agent.team}-{digest([snapshot.snapshot_id, question, agent.agent_id])[:16]}", "matter_id": snapshot.matter_id, "snapshot_id": snapshot.snapshot_id, "agent_id": agent.agent_id, "provider": provider_result.provider, "mode": provider_result.mode, "status": "COMPLETE", "provider_result_status": provider_result.status})
            run.status, run.output_hash = "COMPLETE", digest(opinion)
    except Exception as exc:
        opinion = _unavailable(agent, question, snapshot, str(exc)); run.status = "INVALID_PROVIDER_OUTPUT"; run.error_code = "INVALID_PROVIDER_OUTPUT"; run.output_hash = opinion["output_hash"]
    run.completed_at, run.structured_output_id = now(), opinion.get("opinion_id")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"{agent.team.lower()}-first-pass.json").write_text(json.dumps(opinion, indent=2, sort_keys=True) + "\n")
    (outdir / f"{agent.team.lower()}-run.json").write_text(json.dumps(_json(run), indent=2, sort_keys=True) + "\n")
    return opinion, run


def execute_question(root: Path, item: dict, packet: dict, *, blue_provider: str = "configured", red_provider: str = "configured", run_blue: bool = True, run_red: bool = True) -> dict:
    matter_id, outdir = f"benchmark-{item['id'].lower()}", root / "runs" / item["id"]
    shared = SharedMatterMemory(matter_id, unresolved_questions=[MemoryItem(f"MEM-{item['id']}", matter_id, "unresolved_question", item["question"], "UNKNOWN", source_id=packet.get("id"), source_location=packet.get("source_url"), jurisdiction=item.get("jurisdiction"))])
    firewall = MemoryFirewall(shared, PrivateMemory(matter_id, "alexandra_vale"), PrivateMemory(matter_id, "victor_sterling"))
    snapshot = create_snapshot(matter_id, shared, [packet], [])
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "snapshot.json").write_text(json.dumps(_json(snapshot), indent=2, sort_keys=True) + "\n")
    append(outdir / "audit.jsonl", {"event": "SNAPSHOT_CREATED", "matter_id": matter_id, "snapshot_id": snapshot.snapshot_id})
    if run_blue:
        blue, blue_run = _first_pass(ALEXANDRA, blue_provider, item["question"], packet, snapshot, outdir)
        append(outdir / "audit.jsonl", {"event": "BLUE_COMPLETED", "status": blue_run.status, "output_hash": blue_run.output_hash})
    else:
        blue_run = AgentRun(f"RUN-BLUE-SKIPPED-{item['id']}", matter_id, ALEXANDRA.agent_id, "INDEPENDENT_FIRST_PASS", snapshot.snapshot_id, "not_run", "not_run", "dual-attorney-v1", now(), status="NOT_RUN", completed_at=now(), error_code="AGENT_NOT_SELECTED")
    if run_red:
        red, red_run = _first_pass(VICTOR, red_provider, item["question"], packet, snapshot, outdir)
        append(outdir / "audit.jsonl", {"event": "RED_COMPLETED", "status": red_run.status, "output_hash": red_run.output_hash})
    else:
        red_run = AgentRun(f"RUN-RED-SKIPPED-{item['id']}", matter_id, VICTOR.agent_id, "INDEPENDENT_FIRST_PASS", snapshot.snapshot_id, "not_run", "not_run", "dual-attorney-v1", now(), status="NOT_RUN", completed_at=now(), error_code="AGENT_NOT_SELECTED")
    disagreements = [] if blue_run.status == red_run.status == "COMPLETE" else [{"disagreement_id": f"DIS-{item['id']}", "topic": "independent-first-pass-availability", "blue_position": blue_run.status, "red_position": red_run.status, "resolution_status": "UNRESOLVED", "materiality": "CRITICAL"}]
    (outdir / "disagreements.json").write_text(json.dumps(disagreements, indent=2, sort_keys=True) + "\n")
    reasons = []
    if blue_run.status != "COMPLETE": reasons.append("BLUE_AGENT_NOT_RUN" if blue_run.status == "NOT_RUN" else ("BLUE_AGENT_UNAVAILABLE" if blue_run.status == "AGENT_UNAVAILABLE" else "BLUE_INVALID_PROVIDER_OUTPUT"))
    if red_run.status != "COMPLETE": reasons.append("RED_AGENT_NOT_RUN" if red_run.status == "NOT_RUN" else ("RED_AGENT_UNAVAILABLE" if red_run.status == "AGENT_UNAVAILABLE" else "RED_INVALID_PROVIDER_OUTPUT"))
    if disagreements: reasons.append("INDEPENDENT_FIRST_PASS_INCOMPLETE")
    governor = {"decision": "REVIEW_REQUIRED", "internal_status": "LEGAL_REVIEW_REQUIRED", "reason_codes": reasons, "required_human_review": True, "matter_id": matter_id, "snapshot_id": snapshot.snapshot_id, "created_at": now()}
    governor["decision_hash"] = digest(governor)
    (outdir / "governor.json").write_text(json.dumps(governor, indent=2, sort_keys=True) + "\n")
    append(outdir / "audit.jsonl", {"event": "GOVERNOR_DECISION", "decision": governor["decision"], "reason_codes": reasons})
    return {"benchmark_id": item["id"], "matter_id": matter_id, "snapshot_id": snapshot.snapshot_id, "blue_status": blue_run.status, "red_status": red_run.status, "governor_status": governor["decision"], "reason_codes": reasons, "run_dir": str(outdir)}


def execute_pilot(root: Path, items: list[dict], packets: dict[str, dict], *, blue_provider: str = "configured", red_provider: str = "configured", agents: str = "both") -> dict:
    results, failures = [], []
    for item in items:
        packet = packets.get(item.get("source_packet_id"))
        if not packet: failures.append(f"{item.get('id')}: missing source packet"); continue
        results.append(execute_question(root, item, packet, blue_provider=blue_provider, red_provider=red_provider, run_blue=agents in {"both", "alexandra"}, run_red=agents in {"both", "victor"}))
    # EXECUTED means every requested item was processed; it is deliberately
    # distinct from a legal Governor PASS.
    return {"status": "EXECUTED" if not failures else "BLOCK", "count": len(results), "failures": failures, "results": results}
