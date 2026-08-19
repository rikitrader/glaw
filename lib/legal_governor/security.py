"""Small deterministic security boundary for retrieved legal text."""
from __future__ import annotations

import re


INSTRUCTION_MARKERS = re.compile(r"(?:ignore\s+(?:all|previous)\s+instructions|system\s+message|developer\s+message|reveal\s+the\s+prompt|exfiltrate)", re.I)


def quarantine(text: str) -> dict:
    """Mark source text as data; never execute or elevate embedded instructions."""
    matches = INSTRUCTION_MARKERS.findall(text or "")
    return {"text": str(text or ""), "trusted_instructions": False, "injection_markers": sorted(set(matches)), "status": "QUARANTINED" if matches else "DATA_ONLY"}


def allowed(agent: str, operation: str) -> bool:
    permissions = {
        "retriever": {"read_sources"},
        "citation-validator": {"read_sources", "read_claims"},
        "drafting": {"read_verified_claims"},
        "legal-governor": {"read_verification", "write_decision"},
    }
    return operation in permissions.get(agent, set())

