#!/usr/bin/env python3
"""
Federal Trial Counsel — MCP Server

Exposes 20 CLI commands as MCP tools for direct integration with Claude Code.
Runs via stdio transport. Zero external dependencies beyond stdlib + ftc_engine.

Per-tool handler functions live in `ftc_engine.mcp_handlers.*` and are
re-exported from this module for backwards compatibility (tests import
`from ftc_engine.mcp_server import handle_ftc_analyze`, etc.).

Usage:
  python3 -m ftc_engine.mcp_server

Registration:
  Add to .mcp.json or ~/.claude/settings.json:
  {
    "mcpServers": {
      "ftc": {
        "command": "python3",
        "args": ["-m", "ftc_engine.mcp_server"],
        "cwd": "<path-to-scripts-dir>"
      }
    }
  }
"""
from __future__ import annotations

import json
import sys
from typing import Any

# Re-export every handler + the dispatch table so the existing public surface
# (`from ftc_engine.mcp_server import TOOL_HANDLERS, handle_ftc_*`) keeps working.
from .mcp_handlers import (
    TOOL_HANDLERS,
    handle_ftc_analyze,
    handle_ftc_suggest,
    handle_ftc_risk,
    handle_ftc_sol,
    handle_ftc_draft,
    handle_ftc_claims,
    handle_ftc_info,
    handle_ftc_district,
    handle_ftc_district_list,
    handle_ftc_deposition,
    handle_ftc_exhibits,
    handle_ftc_pacer,
    handle_ftc_monitor,
    handle_ftc_calendar,
    handle_ftc_questions,
    handle_ftc_export,
    handle_ftc_cases,
    handle_ftc_analyze_docs,
    handle_ftc_doctor,
    handle_ftc_template_list,
)


# ── MCP Protocol Helpers ──────────────────────────────────────────────────────

def _send(msg: dict) -> None:
    """Send a JSON-RPC message over stdout."""
    payload = json.dumps(msg)
    header = f"Content-Length: {len(payload.encode())}\r\n\r\n"
    sys.stdout.write(header)
    sys.stdout.write(payload)
    sys.stdout.flush()


def _ok(req_id: Any, result: dict) -> None:
    _send({"jsonrpc": "2.0", "id": req_id, "result": result})


def _error(req_id: Any, code: int, message: str) -> None:
    _send({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})


def _read_message() -> dict | None:
    """Read a JSON-RPC message from stdin (Content-Length framing)."""
    headers = {}
    while True:
        line = sys.stdin.readline()
        if not line:
            return None
        line = line.strip()
        if line == "":
            break
        if ":" in line:
            key, val = line.split(":", 1)
            headers[key.strip().lower()] = val.strip()

    length = int(headers.get("content-length", 0))
    if length == 0:
        return None

    body = sys.stdin.read(length)
    return json.loads(body)


# ── Tool Definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "ftc_analyze",
        "description": "Full case analysis: jurisdiction, claim suggestions, risk scoring, SOL check, and optional complaint draft. Returns structured JSON report.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_data": {"type": "object", "description": "Case JSON data (see sample_case.json for schema)"},
                "output_dir": {"type": "string", "description": "Optional output directory for draft files"},
            },
            "required": ["case_data"],
        },
    },
    {
        "name": "ftc_suggest",
        "description": "Auto-suggest federal claims based on case facts. Returns ranked claim suggestions with match scores and showstoppers.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_data": {"type": "object", "description": "Case JSON data"},
                "max_results": {"type": "integer", "description": "Max suggestions to return (default: 10)", "default": 10},
            },
            "required": ["case_data"],
        },
    },
    {
        "name": "ftc_risk",
        "description": "MTD (Motion to Dismiss) risk scoring for specific claims. Returns 0-100 risk score with vulnerability analysis.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_data": {"type": "object", "description": "Case JSON data"},
                "claims": {"type": "array", "items": {"type": "string"}, "description": "Claim keys to score"},
            },
            "required": ["case_data", "claims"],
        },
    },
    {
        "name": "ftc_sol",
        "description": "Statute of limitations calculator. Returns deadline, days remaining, and status (safe/urgent/expired) for each claim.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "claims": {"type": "array", "items": {"type": "string"}, "description": "Claim keys"},
                "injury_date": {"type": "string", "description": "Date of injury (YYYY-MM-DD)"},
            },
            "required": ["claims", "injury_date"],
        },
    },
    {
        "name": "ftc_draft",
        "description": "Generate a federal complaint skeleton from case data. Returns formatted markdown complaint text.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_data": {"type": "object", "description": "Case JSON data"},
            },
            "required": ["case_data"],
        },
    },
    {
        "name": "ftc_claims",
        "description": "List all 45 available federal causes of action with metadata (category, heightened pleading, exhaustion, immunities).",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "ftc_info",
        "description": "Show detailed metadata for a specific federal claim: source, SOL, defenses, viability warnings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "claim_key": {"type": "string", "description": "Claim key (e.g., '1983_fourth_excessive_force')"},
            },
            "required": ["claim_key"],
        },
    },
    {
        "name": "ftc_district",
        "description": "Get information about a federal district court: judges, divisions, local rules, page limits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "District code (e.g., 'mdfl', 'sdny', 'ndcal')"},
            },
            "required": ["code"],
        },
    },
    {
        "name": "ftc_district_list",
        "description": "List all 94 federal district courts with codes and names.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "ftc_deposition",
        "description": "Generate deposition question outline for a witness. Returns categorized questions by claim element.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_data": {"type": "object", "description": "Case JSON data"},
                "witness_name": {"type": "string", "description": "Name of the deponent"},
                "exam_type": {"type": "string", "enum": ["direct", "cross"], "default": "cross"},
                "claim_keys": {"type": "array", "items": {"type": "string"}, "description": "Optional claim keys to focus on"},
                "max_questions": {"type": "integer", "default": 50},
            },
            "required": ["case_data", "witness_name"],
        },
    },
    {
        "name": "ftc_exhibits",
        "description": "Generate exhibit index with authentication checklist. Returns formatted exhibit table.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_data": {"type": "object", "description": "Case JSON data"},
                "numbering": {"type": "string", "enum": ["alpha", "numeric", "bates"], "default": "alpha"},
                "prefix": {"type": "string", "description": "Bates prefix (e.g., 'SMITH')"},
            },
            "required": ["case_data"],
        },
    },
    {
        "name": "ftc_pacer",
        "description": "Generate PACER/ECF filing package: JS-44 Civil Cover Sheet, summonses, corporate disclosure statements.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_data": {"type": "object", "description": "Case JSON data"},
                "component": {"type": "string", "enum": ["all", "js44", "summons", "disclosure"], "default": "all"},
            },
            "required": ["case_data"],
        },
    },
    {
        "name": "ftc_monitor",
        "description": "Rule 11 duty monitor — checks claim viability against current case law. Returns compliance report with critical flags.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_data": {"type": "object", "description": "Case JSON data"},
                "claim_keys": {"type": "array", "items": {"type": "string"}, "description": "Claims to check (auto-detects if omitted)"},
                "mode": {"type": "string", "enum": ["offline", "online"], "default": "offline"},
            },
            "required": ["case_data"],
        },
    },
    {
        "name": "ftc_calendar",
        "description": "Generate case filing calendar with FRCP deadlines. Returns milestone table with dates and document requirements.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_data": {"type": "object", "description": "Case JSON data"},
                "filing_date": {"type": "string", "description": "Filing date YYYY-MM-DD (default: today)"},
                "district_code": {"type": "string", "description": "District code for local timing rules"},
            },
            "required": ["case_data"],
        },
    },
    {
        "name": "ftc_questions",
        "description": "Generate post-analysis verification questions: pre-filing, strategic follow-ups, client communication, procedural next steps.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_data": {"type": "object", "description": "Case JSON data"},
                "doc_type": {"type": "string", "description": "Document type context (analyze, draft, export)", "default": "analyze"},
                "verbose": {"type": "boolean", "default": False},
            },
            "required": ["case_data"],
        },
    },
    {
        "name": "ftc_export",
        "description": "Export document to court-formatted .docx (Times New Roman 12pt, double-spaced, 1\" margins). Supports draft complaints, templates, and plain text.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_data": {"type": "object", "description": "Case JSON data (for draft/template)"},
                "mode": {"type": "string", "enum": ["draft", "template", "list_templates"], "default": "draft"},
                "template_name": {"type": "string", "description": "Template path (e.g., 'motions/motion_to_dismiss')"},
                "output_path": {"type": "string", "description": "Output .docx file path"},
            },
            "required": [],
        },
    },
    {
        "name": "ftc_cases",
        "description": "List all saved cases with their status and current workflow step.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "ftc_analyze_docs",
        "description": "Analyze intake documents for a case using the 5-layer document analysis pipeline (extraction, classification, entity extraction, analysis, routing).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_number": {"type": "string", "description": "Case number to analyze documents for"},
            },
            "required": ["case_number"],
        },
    },
    {
        "name": "ftc_doctor",
        "description": "Run diagnostic health check on the FTC engine installation.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "ftc_template_list",
        "description": "List all 42 court-ready templates organized by category (pleadings, motions, discovery, orders, appellate).",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


# ── MCP Protocol Handlers ────────────────────────────────────────────────────

def handle_initialize(req_id: Any, params: dict) -> None:
    _ok(req_id, {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {"listChanged": False}},
        "serverInfo": {"name": "ftc-engine", "version": "1.0.0"},
    })


def handle_tools_list(req_id: Any, params: dict) -> None:
    _ok(req_id, {"tools": TOOLS})


def handle_tools_call(req_id: Any, params: dict) -> None:
    tool_name = params.get("name", "")
    arguments = params.get("arguments", {})

    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        _ok(req_id, {"content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}], "isError": True})
        return

    try:
        result = handler(arguments)
        text = json.dumps(result, indent=2, default=str)
        _ok(req_id, {"content": [{"type": "text", "text": text}]})
    except Exception as e:
        _ok(req_id, {"content": [{"type": "text", "text": f"Error in {tool_name}: {e}"}], "isError": True})


# ── Main Loop ─────────────────────────────────────────────────────────────────

def main() -> None:
    """Run the MCP server over stdio."""
    while True:
        msg = _read_message()
        if msg is None:
            break

        method = msg.get("method", "")
        req_id = msg.get("id")
        params = msg.get("params", {})

        if method == "initialize":
            handle_initialize(req_id, params)
        elif method == "notifications/initialized":
            pass  # No response needed for notifications
        elif method == "tools/list":
            handle_tools_list(req_id, params)
        elif method == "tools/call":
            handle_tools_call(req_id, params)
        elif method == "shutdown":
            if req_id is not None:
                _ok(req_id, {})
            break
        elif req_id is not None:
            _error(req_id, -32601, f"Method not found: {method}")


if __name__ == "__main__":
    main()
