"""Human-authority gate for acts GLAW may prepare but not autonomously commit."""
from __future__ import annotations

import os

from glaw_rbac import require_permission


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


def human_authority_error(action: str, context: str = "", rbac_message: str = "") -> str:
    action = action.strip() or "human-only action"
    detail = f" for {context}" if context else ""
    base = (
        f"HUMAN AUTHORITY BLOCKED: {action}{detail} is reserved to a human licensed/authorized actor.\n"
        "Quality gates can approve readiness, but they do not authorize filing, service, signature, "
        "payment, charge, or live transmission.\n"
        "Pass --human-authority '<name/role>' plus --role ADMIN, or set GLAW_HUMAN_AUTHORITY_ACTOR "
        "and GLAW_RBAC_ROLE=ADMIN after the human actor has authorized the act."
    )
    return base + (f"\n{rbac_message}" if rbac_message else "")


def require_human_authority(action: str, *, actor: str = "", role: str = "", context: str = "") -> tuple[bool, str]:
    normalized = action.strip().lower()
    if normalized not in HUMAN_ONLY_ACTIONS:
        return True, authority_actor(actor)
    authorized = authority_actor(actor)
    if authorized:
        ok, message, _result = require_permission(
            "human_authority",
            actor=authorized,
            role=role,
            resource=normalized,
            context=context,
        )
        if ok:
            return True, authorized
        return False, human_authority_error(action, context, message)
    ok, message, _result = require_permission(
        "human_authority",
        actor=actor,
        role=role,
        resource=normalized,
        context=context,
    )
    return False, human_authority_error(action, context, message if not ok else "")
