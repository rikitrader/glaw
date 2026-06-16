"""Oversight Board state, kill-switch, and audit ledger."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from glaw_rbac import require_permission


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def home() -> Path:
    return Path(os.environ.get("GLAW_HOME", str(Path.home() / ".glaw")))


def oversight_dir() -> Path:
    path = home() / "oversight"
    path.mkdir(parents=True, exist_ok=True)
    return path


def state_path() -> Path:
    return oversight_dir() / "state.json"


def ledger_path() -> Path:
    return oversight_dir() / "oversight.jsonl"


def read_state() -> dict[str, Any]:
    path = state_path()
    if not path.exists():
        return {
            "halted": False,
            "halted_at": "",
            "halted_by": "",
            "halt_reason": "",
            "resumed_at": "",
            "resumed_by": "",
            "resume_reason": "",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "halted": True,
            "halted_at": now(),
            "halted_by": "system",
            "halt_reason": "oversight state file is invalid JSON; fail closed",
            "state_error": "invalid_json",
        }
    if not isinstance(data, dict):
        data = {}
    data.setdefault("halted", False)
    data.setdefault("halted_at", "")
    data.setdefault("halted_by", "")
    data.setdefault("halt_reason", "")
    return data


def write_state(data: dict[str, Any]) -> None:
    path = state_path()
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def append_ledger(row: dict[str, Any]) -> None:
    row = {"ts": now(), **row}
    with ledger_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=False) + "\n")


def tail_ledger(limit: int = 20) -> list[dict[str, Any]]:
    path = ledger_path()
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"event": "invalid_jsonl", "raw": line[:160]})
    return rows[-limit:] if limit > 0 else rows


def require_oversight_admin(actor: str, role: str, action: str) -> tuple[bool, str]:
    ok, message, _result = require_permission(
        "human_authority",
        actor=actor,
        role=role,
        resource=f"oversight:{action}",
        context="GLAW Oversight Board",
    )
    return ok, message


def halt(actor: str, reason: str) -> dict[str, Any]:
    if not actor.strip():
        raise ValueError("--by is required for kill-switch halt")
    if not reason.strip():
        raise ValueError("--reason is required for kill-switch halt")
    data = read_state()
    data.update({
        "halted": True,
        "halted_at": now(),
        "halted_by": actor.strip(),
        "halt_reason": reason.strip(),
    })
    write_state(data)
    append_ledger({
        "event": "kill_switch_halted",
        "actor": actor.strip(),
        "reason": reason.strip(),
    })
    return data


def resume(actor: str, role: str, reason: str) -> tuple[bool, dict[str, Any]]:
    ok, message = require_oversight_admin(actor, role, "resume")
    if not ok:
        append_ledger({
            "event": "resume_blocked",
            "actor": actor.strip(),
            "role": role.strip(),
            "reason": message,
        })
        return False, {"status": "blocked", "reason": message}
    if not reason.strip():
        return False, {"status": "blocked", "reason": "--reason is required for resume"}
    data = read_state()
    data.update({
        "halted": False,
        "resumed_at": now(),
        "resumed_by": actor.strip(),
        "resume_reason": reason.strip(),
    })
    write_state(data)
    append_ledger({
        "event": "kill_switch_resumed",
        "actor": actor.strip(),
        "role": role.strip(),
        "reason": reason.strip(),
    })
    return True, data


def escalate(*, matter: str, reason: str, source: str = "", owner: str = "human-oversight-board") -> dict[str, Any]:
    if not matter.strip():
        raise ValueError("--matter is required for oversight escalation")
    if not reason.strip():
        raise ValueError("--reason is required for oversight escalation")
    row = {
        "event": "oversight_escalation",
        "matter": matter.strip(),
        "owner": owner.strip() or "human-oversight-board",
        "reason": reason.strip(),
        "source": source.strip(),
        "status": "open",
    }
    append_ledger(row)
    return row


def decision(*, matter: str, decision_text: str, actor: str, role: str, reason: str, source: str = "") -> tuple[bool, dict[str, Any]]:
    if decision_text not in {"approve", "fix", "deny", "halt"}:
        return False, {"status": "blocked", "reason": "decision must be approve|fix|deny|halt"}
    ok, message = require_oversight_admin(actor, role, f"decision:{decision_text}")
    if not ok:
        append_ledger({
            "event": "oversight_decision_blocked",
            "matter": matter.strip(),
            "decision": decision_text,
            "actor": actor.strip(),
            "role": role.strip(),
            "reason": message,
        })
        return False, {"status": "blocked", "reason": message}
    if not matter.strip():
        return False, {"status": "blocked", "reason": "--matter is required"}
    if not reason.strip():
        return False, {"status": "blocked", "reason": "--reason is required"}
    row = {
        "event": "oversight_decision",
        "matter": matter.strip(),
        "decision": decision_text,
        "actor": actor.strip(),
        "role": role.strip(),
        "reason": reason.strip(),
        "source": source.strip(),
        "status": "recorded",
    }
    append_ledger(row)
    if decision_text == "halt":
        halt(actor, reason)
    return True, row


def status(limit: int = 20) -> dict[str, Any]:
    state = read_state()
    return {
        "status": "halted" if state.get("halted") else "active",
        "state": state,
        "ledger_path": str(ledger_path()),
        "recent": tail_ledger(limit),
    }
