"""Claude/Codex independent-analysis parity binding."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


AGENTS = {"claude", "codex"}


def record(matter: Path, agent: str, context_sha256: str, analysis_path: Path, status: str) -> dict:
    agent = agent.lower().strip()
    if agent not in AGENTS:
        raise ValueError("agent must be claude or codex")
    if not analysis_path.is_file():
        raise ValueError("analysis file is missing")
    row = {
        "schema": "glaw-agent-analysis/v1",
        "agent": agent,
        "context_sha256": context_sha256,
        "analysis_path": str(analysis_path),
        "analysis_sha256": hashlib.sha256(analysis_path.read_bytes()).hexdigest(),
        "status": status,
        "recorded_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    path = matter / "workpapers" / f"{agent}-analysis.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return row


def verify(matter: Path) -> dict:
    rows = []
    failures = []
    for agent in sorted(AGENTS):
        path = matter / "workpapers" / f"{agent}-analysis.json"
        if not path.is_file():
            failures.append(f"{agent} analysis record is missing")
            continue
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            failures.append(f"{agent} analysis record is invalid JSON")
            continue
        source = Path(str(row.get("analysis_path", "")))
        if not source.is_file():
            failures.append(f"{agent} analysis source is missing")
        elif hashlib.sha256(source.read_bytes()).hexdigest() != row.get("analysis_sha256"):
            failures.append(f"{agent} analysis source hash mismatch")
        if row.get("status") not in {"complete", "pass"}:
            failures.append(f"{agent} analysis is not complete")
        rows.append(row)
    contexts = {row.get("context_sha256") for row in rows}
    if len(contexts) != 1:
        failures.append("Claude and Codex are not bound to the same RAG context digest")
    return {"status": "PASS" if not failures else "BLOCK", "context_sha256": next(iter(contexts), ""), "agents": rows, "failures": failures}
