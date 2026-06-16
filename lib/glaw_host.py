"""Host adapter primitives for embedding GLAW in autonomous runtimes."""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from glaw_rbac import require_permission


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def glaw_home() -> Path:
    return Path(os.environ.get("GLAW_HOME", str(Path.home() / ".glaw")))


def active_matter() -> str:
    p = glaw_home() / ".active"
    return p.read_text(encoding="utf-8").strip() if p.exists() else ""


def version() -> str:
    p = ROOT / "VERSION"
    return p.read_text(encoding="utf-8").strip() if p.exists() else "unknown"


def _tool_path(tool: str) -> Path:
    name = Path(tool).name
    return BIN / name


def is_allowed_tool(tool: str) -> bool:
    name = Path(tool).name
    if name != tool or "/" in tool or tool.startswith("."):
        return False
    if not (name == "glaw" or name.startswith("glaw-")):
        return False
    path = _tool_path(name)
    return path.is_file() and os.access(path, os.X_OK)


def list_tools() -> list[dict]:
    rows = []
    for path in sorted(BIN.iterdir()):
        if not path.is_file() or not os.access(path, os.X_OK):
            continue
        if not (path.name == "glaw" or path.name.startswith("glaw-")):
            continue
        rows.append({
            "name": path.name,
            "path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    return rows


def manifest() -> dict:
    tools = list_tools()
    return {
        "schema_version": 1,
        "name": "glaw-host-adapter",
        "glaw_version": version(),
        "generated_at": now(),
        "root": str(ROOT),
        "active_matter": active_matter(),
        "tool_count": len(tools),
        "tools": tools,
        "safety_contract": {
            "source_only": True,
            "no_shell_interpolation": True,
            "argv_array_required": True,
            "pre_call_guard": "glaw-conscience check-call",
            "post_response_guard": "glaw-conscience check-response",
            "human_seal_ring": "R4_HUMAN_SEAL",
            "human_seal_role": "ADMIN",
            "reserved_human_acts": ["file", "serve", "sign", "transmit", "charge", "pay", "submit-live"],
            "binding_actions": "prepare-only unless a lawful human actor with RBAC ADMIN authorizes the act",
        },
    }


def _command_string(tool: str, args: list[str]) -> str:
    return shlex.join([str(_tool_path(tool)), *[str(a) for a in args]])


def _run_guard(*args: str) -> tuple[int, str]:
    proc = subprocess.run(
        [str(BIN / "glaw-conscience"), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return proc.returncode, proc.stdout.strip()


def _parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"status": "fail", "raw": text}


def _rbac_operation(tool: str, args: list[str]) -> str:
    lowered = [str(arg).lower() for arg in args]
    if tool == "glaw" and lowered == ["version"]:
        return "read"
    if lowered and lowered[0] in {"status", "list", "roles", "manifest"}:
        return "read"
    if tool in {"glaw-irs-file", "glaw-authority"} and ("--live" in lowered or "submit-live" in lowered):
        return "human_authority"
    if tool == "glaw-chief-decision" and "--signoff" in lowered:
        return "human_authority"
    return "write"


def execute(tool: str, args: list[str], *, matter: str = "", timeout: int = 30, role: str = "", actor: str = "") -> dict:
    if not is_allowed_tool(tool):
        return {
            "status": "blocked",
            "reason": "tool is not a whitelisted executable GLAW tool",
            "tool": tool,
            "args": args,
        }
    if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
        return {
            "status": "blocked",
            "reason": "args must be a JSON array of strings",
            "tool": tool,
            "args": args,
        }

    command = _command_string(tool, args)
    operation = _rbac_operation(tool, args)
    rbac_ok, rbac_message, rbac = require_permission(
        operation,
        role=role,
        actor=actor,
        resource=command,
        context=f"glaw-host execute {tool}",
    )
    if not rbac_ok:
        return {
            "status": "blocked",
            "phase": "rbac",
            "tool": tool,
            "args": args,
            "rbac": rbac,
            "reason": rbac_message,
        }
    pre_rc, pre_out = _run_guard("check-call", "--command", command, "--matter", matter, "--json")
    pre_guard = _parse_json(pre_out)
    if pre_rc != 0 or pre_guard.get("status") != "pass":
        return {
            "status": "blocked",
            "phase": "pre-call",
            "tool": tool,
            "args": args,
            "pre_guard": pre_guard,
        }

    try:
        proc = subprocess.run(
            [str(_tool_path(tool)), *args],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=max(1, timeout),
            check=False,
        )
        stdout = proc.stdout
        rc = proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        rc = 124

    post_rc, post_out = _run_guard("check-response", "--text", stdout, "--matter", matter, "--json")
    post_guard = _parse_json(post_out)
    status = "pass" if rc == 0 and post_rc == 0 and post_guard.get("status") == "pass" else "fail"
    return {
        "status": status,
        "tool": tool,
        "args": args,
        "returncode": rc,
        "stdout": stdout,
        "rbac": rbac,
        "pre_guard": pre_guard,
        "post_guard": post_guard,
    }
