"""Source-only MCP-style JSON-RPC bridge over glaw-host."""
from __future__ import annotations

import json
from typing import Any

from glaw_host import execute, manifest


PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "glaw-mcp", "version": "1.0.0"}


def text_content(data: Any) -> list[dict]:
    return [{"type": "text", "text": json.dumps(data, indent=2, sort_keys=False)}]


def tool_defs() -> list[dict]:
    return [
        {
            "name": "glaw_manifest",
            "description": "Return the GLAW host manifest, tool inventory, hashes, and safety contract.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "glaw_status",
            "description": "Return current GLAW embedding status and active matter.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "glaw_execute",
            "description": "Execute a whitelisted GLAW tool through argv-only glaw-host with RBAC plus pre/post conscience guards.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tool": {"type": "string"},
                    "args": {"type": "array", "items": {"type": "string"}},
                    "matter": {"type": "string"},
                    "role": {"type": "string"},
                    "actor": {"type": "string"},
                    "timeout": {"type": "integer", "minimum": 1, "maximum": 300},
                },
                "required": ["tool", "args"],
                "additionalProperties": False,
            },
        },
    ]


def call_tool(name: str, arguments: dict | None = None) -> dict:
    args = arguments or {}
    if name == "glaw_manifest":
        return {"content": text_content(manifest()), "isError": False}
    if name == "glaw_status":
        data = {
            "schema_version": 1,
            "status": "ready",
            "active_matter": manifest().get("active_matter", ""),
            "safety_contract": manifest()["safety_contract"],
        }
        return {"content": text_content(data), "isError": False}
    if name == "glaw_execute":
        data = execute(
            str(args.get("tool", "")),
            args.get("args", []),
            matter=str(args.get("matter", "")),
            timeout=int(args.get("timeout", 30) or 30),
            role=str(args.get("role", "")),
            actor=str(args.get("actor", "")),
        )
        return {"content": text_content(data), "isError": data.get("status") != "pass"}
    return {
        "content": text_content({"status": "blocked", "reason": f"unknown GLAW MCP tool: {name}"}),
        "isError": True,
    }


def success(message_id: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def error(message_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": message}}


def handle_message(message: dict) -> dict | None:
    message_id = message.get("id")
    method = message.get("method", "")
    params = message.get("params") or {}
    if message_id is None and method.startswith("notifications/"):
        return None
    if method == "initialize":
        return success(message_id, {
            "protocolVersion": params.get("protocolVersion") or PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        })
    if method == "tools/list":
        return success(message_id, {"tools": tool_defs()})
    if method == "tools/call":
        return success(message_id, call_tool(str(params.get("name", "")), params.get("arguments") or {}))
    if method == "ping":
        return success(message_id, {})
    return error(message_id, -32601, f"method not found: {method}")
