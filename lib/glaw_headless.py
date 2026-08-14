"""Headless orchestrator report for spawned/autonomous GLAW hosts."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from glaw_compliance import compliance_action_plan, compliance_failures
from glaw_premium_scope import premium_lane_requirement

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
    for path in sorted((matter / "workpapers").glob("premium-lane-*.json")):
        artifacts.append({"path": str(path.relative_to(matter)), "bytes": path.stat().st_size})
    for path in sorted((matter / "drafts").glob("premium-lane-*/*.md")):
        artifacts.append({"path": str(path.relative_to(matter)), "bytes": path.stat().st_size})
    return artifacts


def premium_lane_status(matter: Path) -> dict:
    requirement = premium_lane_requirement(read_json(matter / "intake.json", {}))
    rc, output = run_tool(["glaw-premium-lanes", "status", "--matter-slug", matter.name, "--json"])
    try:
        report = json.loads(output)
    except json.JSONDecodeError:
        return {
            "present": False,
            "status": "fail",
            "lane_count": 0,
            "lanes": [],
            "failures": [{"id": "premium_lane_status", "detail": output or "glaw-premium-lanes did not return JSON"}],
            "action_plan": [{
                "id": "premium_lane_status",
                "owner": "glaw-premium-lanes",
                "next_command": f"bin/glaw-premium-lanes status --matter-slug {matter.name} --json",
                "required_fix": "repair the premium lane matter-wide status command before relying on headless readiness",
            }],
            "returncode": rc,
            "authority": "report-only premium lane status; readiness still requires final-packet and Chief/Council gates",
        }
    lanes = report.get("lanes") if isinstance(report.get("lanes"), list) else []
    if not lanes and not requirement.get("required"):
        return {
            "present": False,
            "status": "not_required",
            "lane_count": 0,
            "lanes": [],
            "failures": [],
            "action_plan": [],
            "requirement": requirement,
            "returncode": rc,
            "authority": "report-only premium lane status; no premium lane required by intake metadata",
        }
    if not lanes and requirement.get("required"):
        required_lanes = list(requirement.get("required_lanes") or [])
        return {
            "present": False,
            "status": "fail",
            "lane_count": 0,
            "lanes": [],
            "failures": [
                {"id": "premium_lane_missing", "detail": f"required premium lane packet missing: {lane_id}", "lane_id": lane_id}
                for lane_id in required_lanes
            ],
            "action_plan": [
                {
                    "id": "premium_lane_missing",
                    "lane_id": lane_id,
                    "owner": "glaw-premium-lanes",
                    "missing": ["premium_lane_missing"],
                    "next_command": f"bin/glaw-premium-lanes attach {lane_id} --matter-slug {matter.name}",
                    "required_fix": "attach the required premium lane packet for this matter scope before final-packet or file-gate reliance",
                }
                for lane_id in required_lanes
            ],
            "requirement": requirement,
            "returncode": rc,
            "authority": "report-only premium lane status; readiness still requires final-packet and Chief/Council gates",
        }
    lane_missing: dict[str, list[str]] = {}
    for row in lanes:
        if not isinstance(row, dict):
            continue
        packet = row.get("packet")
        lane_id = str(row.get("lane_id") or "")
        lane_failures = row.get("failures") if isinstance(row.get("failures"), list) else []
        lane_missing[lane_id] = [item.get("id", "premium_lane_packet") for item in lane_failures if isinstance(item, dict)]
        if isinstance(packet, str):
            try:
                packet_path = Path(packet).resolve()
                row["artifact"] = str(packet_path.relative_to(matter.resolve()))
            except ValueError:
                packet_path = Path(packet)
                row["artifact"] = packet
            packet_data = read_json(packet_path, {})
            if isinstance(packet_data, dict):
                row.setdefault("completed_at", packet_data.get("completed_at", ""))
                row.setdefault("completed_by", packet_data.get("completed_by", ""))
    action_plan = report.get("action_plan", [])
    if not isinstance(action_plan, list):
        action_plan = []
    normalized_plan = []
    for item in action_plan:
        if not isinstance(item, dict):
            continue
        row = dict(item)
        row["owner"] = "glaw-premium-lanes"
        lane_id = str(row.get("lane_id") or "")
        row.setdefault("missing", lane_missing.get(lane_id, [str(row.get("id", "premium_lane_packet"))]))
        normalized_plan.append(row)
    return {
        "present": bool(lanes),
        "status": report.get("status", "fail"),
        "lane_count": report.get("lane_count", len(lanes)),
        "lanes": lanes,
        "failures": report.get("failures", []),
        "action_plan": normalized_plan,
        "requirement": requirement,
        "returncode": rc,
        "authority": "report-only premium lane status; readiness still requires final-packet and Chief/Council gates",
    }


def final_packet_summary(matter: Path) -> dict:
    packet = read_json(matter / "final_packet.json", {})
    if not packet:
        return {
            "present": False,
            "status": "missing",
            "compliance_manifest": [],
            "government_adversary_manifest": [],
            "accounting_control_manifest": {},
            "compliance_failures": [],
            "compliance_action_plan": [],
            "government_adversary_failures": [],
            "accounting_control_failures": [],
        }
    compliance = packet.get("compliance_manifest") or []
    government = packet.get("government_adversary_manifest") or []
    accounting_control = packet.get("accounting_control_manifest") or {}
    accounting_failures = []
    if accounting_control and accounting_control.get("status") not in {"pass", "not_required"}:
        accounting_failures.append(accounting_control)
    return {
        "present": True,
        "status": packet.get("status", "unknown"),
        "workflow_profile": packet.get("workflow_profile", ""),
        "generated_at": packet.get("generated_at", ""),
        "gates": packet.get("gates", {}),
        "compliance_manifest": compliance,
        "government_adversary_manifest": government,
        "accounting_control_manifest": accounting_control,
        "compliance_failures": compliance_failures(compliance),
        "compliance_action_plan": compliance_action_plan(compliance),
        "government_adversary_failures": [
            item for item in government if item.get("status") != "pass"
        ],
        "accounting_control_failures": accounting_failures,
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
    premium_lanes = premium_lane_status(matter)
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
        "premium_lanes": premium_lanes,
        "premium_lane_requirement": premium_lanes.get("requirement", {}),
        "premium_lane_failures": premium_lanes["failures"],
        "premium_lane_action_plan": premium_lanes["action_plan"],
        "compliance_manifest": packet_summary["compliance_manifest"],
        "government_adversary_manifest": packet_summary["government_adversary_manifest"],
        "accounting_control_manifest": packet_summary["accounting_control_manifest"],
        "compliance_failures": packet_summary["compliance_failures"],
        "compliance_action_plan": packet_summary["compliance_action_plan"],
        "government_adversary_failures": packet_summary["government_adversary_failures"],
        "accounting_control_failures": packet_summary["accounting_control_failures"],
        "decisions": latest_decisions(matter),
        "shipped_artifacts": shipped_artifacts(matter),
        "timeline_events": len(timeline),
        "authority": "report-only; no filing/signing/service/payment/charge/live transmission",
    }
