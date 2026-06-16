"""Headless orchestrator report for spawned/autonomous GLAW hosts."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def home() -> Path:
    return Path(os.environ.get("GLAW_HOME", str(Path.home() / ".glaw")))


def active_slug() -> str:
    p = home() / ".active"
    return p.read_text(encoding="utf-8").strip() if p.exists() else ""


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"event": "invalid_jsonl", "raw": line})
    return rows


def run_tool(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        [str(BIN / args[0]), *args[1:]],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return proc.returncode, proc.stdout.strip()


def gate_status(slug: str) -> list[dict]:
    rows = []
    for stage in ("strategy", "file", "matter-retro"):
        rc, output = run_tool(["glaw-gate", "check", stage, slug])
        rows.append({
            "stage": stage,
            "status": "pass" if rc == 0 else "blocked",
            "returncode": rc,
            "summary": output.splitlines()[0] if output else "",
        })
    return rows


def latest_decisions(matter: Path, limit: int = 5) -> list[dict]:
    rows = read_jsonl(matter / "decisions.jsonl")
    return rows[-limit:]


def shipped_artifacts(matter: Path) -> list[dict]:
    artifacts = []
    for name in (
        "final_packet.json",
        "final_packet.md",
        "accounting_control.json",
        "groundedness.json",
        "citation_corpus.jsonl",
        "citations.jsonl",
        "council.jsonl",
        "adversarial.jsonl",
        "red_flags.jsonl",
    ):
        path = matter / name
        if path.exists():
            artifacts.append({"path": name, "bytes": path.stat().st_size})
    return artifacts


def final_packet_summary(matter: Path) -> dict:
    packet = read_json(matter / "final_packet.json", {})
    if not packet:
        return {
            "present": False,
            "status": "missing",
            "compliance_manifest": [],
            "government_adversary_manifest": [],
            "compliance_failures": [],
            "government_adversary_failures": [],
        }
    compliance = packet.get("compliance_manifest") or []
    government = packet.get("government_adversary_manifest") or []
    return {
        "present": True,
        "status": packet.get("status", "unknown"),
        "workflow_profile": packet.get("workflow_profile", ""),
        "generated_at": packet.get("generated_at", ""),
        "gates": packet.get("gates", {}),
        "compliance_manifest": compliance,
        "government_adversary_manifest": government,
        "compliance_failures": [
            item for item in compliance if item.get("status") != "pass"
        ],
        "government_adversary_failures": [
            item for item in government if item.get("status") != "pass"
        ],
    }


def report(goal: str, slug: str = "") -> dict:
    matter_slug = slug or active_slug()
    if not matter_slug:
        return {
            "schema_version": 1,
            "status": "blocked",
            "generated_at": now(),
            "goal": goal,
            "matter": "",
            "reason": "no active matter",
            "next_owner": "orchestrator",
            "next_command": "bin/glaw matter new \"<matter name>\"",
            "authority": "report-only; no filing/signing/service/payment/charge/live transmission",
        }
    matter = home() / "matters" / matter_slug
    if not matter.is_dir():
        return {
            "schema_version": 1,
            "status": "blocked",
            "generated_at": now(),
            "goal": goal,
            "matter": matter_slug,
            "reason": "active matter directory missing",
            "next_owner": "orchestrator",
            "next_command": "bin/glaw matter use <valid-slug>",
            "authority": "report-only; no filing/signing/service/payment/charge/live transmission",
        }

    loop_rc, loop_out = run_tool(["glaw-loop", "status", "--matter", matter_slug, "--json"])
    try:
        loop = json.loads(loop_out)
    except json.JSONDecodeError:
        loop = {"quality_state": "blocked", "reason": loop_out or "glaw-loop did not return JSON", "returncode": loop_rc}

    intake = read_json(matter / "intake.json", {})
    timeline = read_jsonl(matter / "timeline.jsonl")
    gates = gate_status(matter_slug)
    open_gates = [row for row in gates if row["status"] != "pass"]
    packet_summary = final_packet_summary(matter)
    return {
        "schema_version": 1,
        "status": "pass" if not open_gates and loop.get("quality_state") in {"ready_for_next_stage", "ready_for_closeout"} else "blocked",
        "generated_at": now(),
        "goal": goal,
        "matter": matter_slug,
        "stage": (matter / ".stage").read_text(encoding="utf-8").strip() if (matter / ".stage").exists() else "intake",
        "workflow_track": intake.get("universal", {}).get("workflow_track") or intake.get("workflow_track") or "unset",
        "loop": loop,
        "next_owner": loop.get("owner", ""),
        "next_gate": loop.get("next_gate", ""),
        "next_command": loop.get("next_command", ""),
        "open_gates": open_gates,
        "gate_status": gates,
        "final_packet": packet_summary,
        "compliance_manifest": packet_summary["compliance_manifest"],
        "government_adversary_manifest": packet_summary["government_adversary_manifest"],
        "compliance_failures": packet_summary["compliance_failures"],
        "government_adversary_failures": packet_summary["government_adversary_failures"],
        "decisions": latest_decisions(matter),
        "shipped_artifacts": shipped_artifacts(matter),
        "timeline_events": len(timeline),
        "authority": "report-only; no filing/signing/service/payment/charge/live transmission",
    }
