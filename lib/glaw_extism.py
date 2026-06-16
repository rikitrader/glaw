"""Extism/zeroclaw plugin contract shim over the guarded GLAW host adapter."""
from __future__ import annotations

import json
from typing import Any

from glaw_host import execute, manifest


PLUGIN_NAME = "glaw-extism"
PLUGIN_VERSION = "1.0.0"


def tool_metadata() -> dict:
    host = manifest()
    return {
        "schema_version": 1,
        "plugin": PLUGIN_NAME,
        "version": PLUGIN_VERSION,
        "exports": ["tool_metadata", "execute"],
        "host_contract": "zeroclaw-extism",
        "glaw_version": host["glaw_version"],
        "tool_count": host["tool_count"],
        "tools": [
            {
                "name": row["name"],
                "description": f"Guarded GLAW tool: {row['name']}",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "args": {"type": "array", "items": {"type": "string"}},
                        "matter": {"type": "string"},
                        "role": {"type": "string"},
                        "actor": {"type": "string"},
                        "timeout": {"type": "integer", "minimum": 1, "maximum": 300},
                    },
                    "required": ["args"],
                    "additionalProperties": False,
                },
                "sha256": row["sha256"],
            }
            for row in host["tools"]
        ],
        "permissions": {
            "shell": "denied",
            "network": "host-runtime-controlled",
            "filesystem": "repo-and-GLAW_HOME",
            "hardware": "denied",
            "human_seal": "RBAC ADMIN plus named lawful human actor required",
        },
        "safety_contract": host["safety_contract"],
    }


def execute_plugin(payload: dict[str, Any]) -> dict:
    tool = str(payload.get("tool", ""))
    args = payload.get("args", [])
    matter = str(payload.get("matter", ""))
    role = str(payload.get("role", ""))
    actor = str(payload.get("actor", ""))
    timeout = int(payload.get("timeout", 30) or 30)
    data = execute(tool, args, matter=matter, timeout=timeout, role=role, actor=actor)
    data["plugin"] = PLUGIN_NAME
    data["export"] = "execute"
    return data


def handle_export(export: str, payload: dict | None = None) -> dict:
    if export == "tool_metadata":
        return tool_metadata()
    if export == "execute":
        return execute_plugin(payload or {})
    return {"status": "blocked", "reason": f"unknown Extism export: {export}", "plugin": PLUGIN_NAME}


def dumps(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=False)
