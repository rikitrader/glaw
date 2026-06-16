"""Human-authority gate for acts GLAW may prepare but not autonomously commit."""
from __future__ import annotations

import os


HUMAN_ONLY_ACTIONS = {
    "charge",
    "efile",
    "e-file",
    "file",
    "pay",
    "serve",
    "sign",
    "submit-live",
    "transmit",
}


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def authority_actor(explicit_actor: str = "") -> str:
    actor = explicit_actor.strip() or os.environ.get("GLAW_HUMAN_AUTHORITY_ACTOR", "").strip()
    if actor:
        return actor
    if _truthy(os.environ.get("GLAW_HUMAN_AUTHORITY")):
        return os.environ.get("USER", "human-operator").strip() or "human-operator"
    return ""


def human_authority_error(action: str, context: str = "") -> str:
    action = action.strip() or "human-only action"
    detail = f" for {context}" if context else ""
    return (
        f"HUMAN AUTHORITY BLOCKED: {action}{detail} is reserved to a human licensed/authorized actor.\n"
        "Quality gates can approve readiness, but they do not authorize filing, service, signature, "
        "payment, charge, or live transmission.\n"
        "Pass --human-authority '<name/role>' or set GLAW_HUMAN_AUTHORITY_ACTOR after the human actor "
        "has authorized the act."
    )


def require_human_authority(action: str, *, actor: str = "", context: str = "") -> tuple[bool, str]:
    normalized = action.strip().lower()
    if normalized not in HUMAN_ONLY_ACTIONS:
        return True, authority_actor(actor)
    authorized = authority_actor(actor)
    if authorized:
        return True, authorized
    return False, human_authority_error(action, context)
