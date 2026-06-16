"""Role/ring authorization with SOC2-mapped audit rows for GLAW."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


ROLES = {
    "READER": {"level": 10, "operations": {"read"}, "description": "read matter state and reports"},
    "AUDITOR": {"level": 15, "operations": {"read", "audit"}, "description": "read and inspect audit evidence"},
    "WRITER": {"level": 20, "operations": {"read", "write"}, "description": "write workpapers and draft outputs"},
    "ADMIN": {"level": 30, "operations": {"read", "write", "audit", "admin", "human_authority"}, "description": "administer gates and human-seal acts"},
}

OPERATION_POLICY = {
    "read": {"roles": {"READER", "AUDITOR", "WRITER", "ADMIN"}, "ring": "R0_READ", "soc2": ("CC6.1", "CC6.6")},
    "audit": {"roles": {"AUDITOR", "ADMIN"}, "ring": "R1_AUDIT", "soc2": ("CC7.2", "CC7.4")},
    "write": {"roles": {"WRITER", "ADMIN"}, "ring": "R2_WORKPAPER", "soc2": ("CC6.2", "CC8.1")},
    "admin": {"roles": {"ADMIN"}, "ring": "R3_ADMIN", "soc2": ("CC6.3", "CC6.8")},
    "human_authority": {"roles": {"ADMIN"}, "ring": "R4_HUMAN_SEAL", "soc2": ("CC6.3", "CC7.2", "CC8.1")},
}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def glaw_home() -> Path:
    return Path(os.environ.get("GLAW_HOME", str(Path.home() / ".glaw")))


def normalize_role(role: str = "") -> str:
    resolved = (role or os.environ.get("GLAW_RBAC_ROLE", "")).strip().upper()
    return resolved


def actor_name(actor: str = "") -> str:
    return (actor or os.environ.get("GLAW_ACTOR", "") or os.environ.get("USER", "unknown-actor")).strip() or "unknown-actor"


def audit_path() -> Path:
    return glaw_home() / "audit" / "rbac.jsonl"


def _last_hash(path: Path) -> str:
    if not path.exists():
        return ""
    last = ""
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                last = line
    if not last:
        return ""
    try:
        return str(json.loads(last).get("row_hash", ""))
    except json.JSONDecodeError:
        return hashlib.sha256(last.encode("utf-8")).hexdigest()


def _row_hash(row: dict) -> str:
    payload = {k: v for k, v in row.items() if k != "row_hash"}
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def append_audit(row: dict) -> dict:
    path = audit_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    stamped = dict(row)
    stamped.setdefault("ts", now())
    stamped["previous_hash"] = _last_hash(path)
    stamped["row_hash"] = _row_hash(stamped)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(stamped, sort_keys=True) + "\n")
    return stamped


def check_permission(
    operation: str,
    *,
    role: str = "",
    actor: str = "",
    resource: str = "",
    context: str = "",
    audit: bool = True,
) -> tuple[bool, dict]:
    op = operation.strip().lower()
    policy = OPERATION_POLICY.get(op)
    resolved_role = normalize_role(role)
    resolved_actor = actor_name(actor)
    if not policy:
        result = {
            "status": "fail",
            "reason": f"unsupported operation: {operation}",
            "operation": op,
            "role": resolved_role,
            "actor": resolved_actor,
            "resource": resource,
            "context": context,
            "ring": "UNKNOWN",
            "soc2_controls": [],
        }
    elif resolved_role not in ROLES:
        result = {
            "status": "fail",
            "reason": "missing or unsupported RBAC role",
            "operation": op,
            "role": resolved_role,
            "actor": resolved_actor,
            "resource": resource,
            "context": context,
            "ring": policy["ring"],
            "soc2_controls": list(policy["soc2"]),
            "allowed_roles": sorted(policy["roles"]),
        }
    elif resolved_role not in policy["roles"]:
        result = {
            "status": "fail",
            "reason": f"role {resolved_role} is not authorized for {op}",
            "operation": op,
            "role": resolved_role,
            "actor": resolved_actor,
            "resource": resource,
            "context": context,
            "ring": policy["ring"],
            "soc2_controls": list(policy["soc2"]),
            "allowed_roles": sorted(policy["roles"]),
        }
    else:
        result = {
            "status": "pass",
            "reason": "authorized",
            "operation": op,
            "role": resolved_role,
            "actor": resolved_actor,
            "resource": resource,
            "context": context,
            "ring": policy["ring"],
            "soc2_controls": list(policy["soc2"]),
            "allowed_roles": sorted(policy["roles"]),
        }
    if audit:
        result["audit"] = append_audit(result)
    return result["status"] == "pass", result


def require_permission(operation: str, **kwargs) -> tuple[bool, str, dict]:
    ok, result = check_permission(operation, **kwargs)
    if ok:
        return True, f"{result['actor']} ({result['role']}, {result['ring']})", result
    allowed = ", ".join(result.get("allowed_roles", [])) or "none"
    message = (
        f"RBAC BLOCKED: {result.get('reason', 'not authorized')}.\n"
        f"Operation: {result.get('operation')}  Ring: {result.get('ring')}  SOC2: "
        f"{', '.join(result.get('soc2_controls', [])) or 'n/a'}\n"
        f"Actor: {result.get('actor')}  Role: {result.get('role') or '(unset)'}  Allowed: {allowed}"
    )
    return False, message, result
