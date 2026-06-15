"""
Case Manager — Persistent case storage, retrieval, and workflow state tracking.

Stores cases at ~/.ftc/cases/<case_number>/ with:
  case.json   — Master case data (same schema as sample_case.json)
  state.json  — Workflow state: current step, completed steps, timestamps
  intake_docs/ — User-provided documents for research
  output/     — Generated documents (complaint, calendar, etc.)

Usage:
  from ftc_engine.case_manager import create_case, open_case, list_cases
"""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


# ── Storage root ────────────────────────────────────────────────────────────

FTC_HOME = Path.home() / ".ftc"
CASES_DIR = FTC_HOME / "cases"


# ── Workflow steps (ordered) ────────────────────────────────────────────────

WORKFLOW_STEPS: list[tuple[str, str]] = [
    ("court", "Court & Jurisdiction"),
    ("plaintiffs", "Plaintiff Information"),
    ("defendants", "Defendant Information"),
    ("facts", "Factual Allegations"),
    ("claims", "Claims Selection"),
    ("relief", "Relief Requested"),
    ("exhaustion", "Administrative Exhaustion"),
    ("limitations", "Statute of Limitations"),
    ("goals", "Case Goals"),
    ("review", "Case Summary Review"),
    ("documents", "Document Selection"),
    ("generate", "Generate Documents"),
]

STEP_KEYS = [s[0] for s in WORKFLOW_STEPS]


# ── Dataclasses ─────────────────────────────────────────────────────────────

@dataclass
class CaseState:
    case_number: str
    case_path: str  # stored as string for JSON serialization
    created: str
    last_modified: str
    current_step: str = "court"
    completed_steps: list[str] = field(default_factory=list)
    pending_steps: list[str] = field(default_factory=lambda: list(STEP_KEYS))
    documents_selected: list[str] = field(default_factory=list)
    output_format: str = "markdown"
    output_location: str = ""  # custom save path; empty = case folder only
    notes: str = ""


@dataclass
class CaseInfo:
    case_number: str
    case_name: str
    status: str  # "intake", "ready", "filed"
    current_step: str
    created: str
    last_modified: str
    path: str


# ── Case path helpers ───────────────────────────────────────────────────────

def _sanitize_case_number(case_number: str) -> str:
    """Sanitize case number for use as folder name (replace : with -)."""
    return case_number.replace(":", "-").replace("/", "-").strip()


def get_case_path(case_number: str) -> Path:
    """Return the folder path for a case."""
    return CASES_DIR / _sanitize_case_number(case_number)


def _extract_case_name(case_data: dict) -> str:
    """Extract 'Plaintiff v. Defendant' from case data."""
    parties = case_data.get("parties", {})
    plaintiffs = parties.get("plaintiffs", [])
    defendants = parties.get("defendants", [])
    p_name = plaintiffs[0]["name"] if plaintiffs else "Unknown"
    d_name = defendants[0]["name"] if defendants else "Unknown"
    return f"{p_name} v. {d_name}"


def _determine_status(state: CaseState) -> str:
    """Determine case status from workflow state."""
    if "generate" in state.completed_steps:
        return "ready"
    return "intake"


# ── Case CRUD ───────────────────────────────────────────────────────────────

def create_case(case_number: str) -> CaseState:
    """Create a new case folder and initialize state."""
    case_path = get_case_path(case_number)
    case_path.mkdir(parents=True, exist_ok=True)
    (case_path / "intake_docs").mkdir(exist_ok=True)
    (case_path / "output").mkdir(exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    state = CaseState(
        case_number=case_number,
        case_path=str(case_path),
        created=now,
        last_modified=now,
    )

    # Initialize empty case data
    empty_case: dict = {
        "court": {},
        "parties": {"plaintiffs": [], "defendants": []},
        "facts": [],
        "claims_requested": [],
        "relief_requested": [],
        "exhaustion": {},
        "limitations": {"key_dates": {}},
        "goals": {},
    }

    save_state(state)
    save_case_data(case_number, empty_case)
    return state


def open_case(case_number: str) -> tuple[CaseState, dict]:
    """Open an existing case. Returns (state, case_data)."""
    case_path = get_case_path(case_number)
    state_file = case_path / "state.json"
    case_file = case_path / "case.json"

    if not state_file.exists():
        raise FileNotFoundError(f"Case not found: {case_number}")

    state_data = json.loads(state_file.read_text())
    state = CaseState(**state_data)

    case_data = json.loads(case_file.read_text()) if case_file.exists() else {}
    return state, case_data


def list_cases() -> list[CaseInfo]:
    """List all saved cases."""
    if not CASES_DIR.exists():
        return []

    cases: list[CaseInfo] = []
    for folder in sorted(CASES_DIR.iterdir()):
        if not folder.is_dir():
            continue
        state_file = folder / "state.json"
        case_file = folder / "case.json"
        if not state_file.exists():
            continue

        state_data = json.loads(state_file.read_text())
        state = CaseState(**state_data)
        case_data = json.loads(case_file.read_text()) if case_file.exists() else {}
        case_name = _extract_case_name(case_data)

        cases.append(CaseInfo(
            case_number=state.case_number,
            case_name=case_name,
            status=_determine_status(state),
            current_step=state.current_step,
            created=state.created,
            last_modified=state.last_modified,
            path=str(folder),
        ))
    return cases


def delete_case(case_number: str) -> bool:
    """Delete a case folder entirely."""
    case_path = get_case_path(case_number)
    if case_path.exists():
        shutil.rmtree(case_path)
        return True
    return False


# ── State management ────────────────────────────────────────────────────────

def save_state(state: CaseState) -> None:
    """Save workflow state to disk."""
    state.last_modified = datetime.now().strftime("%Y-%m-%d %H:%M")
    case_path = Path(state.case_path)
    case_path.mkdir(parents=True, exist_ok=True)
    (case_path / "state.json").write_text(
        json.dumps(asdict(state), indent=2) + "\n"
    )


def save_case_data(case_number: str, case_data: dict) -> Path:
    """Save case data JSON to disk."""
    case_path = get_case_path(case_number)
    case_path.mkdir(parents=True, exist_ok=True)
    out = case_path / "case.json"
    out.write_text(json.dumps(case_data, indent=2) + "\n")
    return out


def load_case_data(case_number: str) -> dict:
    """Load case data from disk."""
    case_path = get_case_path(case_number)
    case_file = case_path / "case.json"
    if not case_file.exists():
        return {}
    return json.loads(case_file.read_text())


def advance_step(state: CaseState, step: str) -> CaseState:
    """Mark a step as completed and advance to the next pending step."""
    if step not in STEP_KEYS:
        raise ValueError(f"Unknown step: {step}")

    if step not in state.completed_steps:
        state.completed_steps.append(step)
    if step in state.pending_steps:
        state.pending_steps.remove(step)

    # Advance current_step to next pending
    for key in STEP_KEYS:
        if key not in state.completed_steps:
            state.current_step = key
            break
    else:
        state.current_step = "done"

    save_state(state)
    return state


# ── Workflow map ────────────────────────────────────────────────────────────

def get_workflow_map(state: CaseState) -> str:
    """Return a formatted workflow progress map."""
    lines: list[str] = []
    sep = "\u2550" * 66  # ═
    lines.append(f"  {sep}")
    lines.append(f"    CASE WORKFLOW — {state.case_number}")
    lines.append(f"  {sep}")

    for i, (key, label) in enumerate(WORKFLOW_STEPS, 1):
        if key in state.completed_steps:
            marker = "[X]"
            suffix = ""
        elif key == state.current_step:
            marker = "[>>]"
            suffix = "  <-- YOU ARE HERE"
        else:
            marker = "[ ]"
            suffix = ""
        lines.append(f"    {marker} {i:2d}. {label}{suffix}")

    completed = len(state.completed_steps)
    total = len(WORKFLOW_STEPS)
    lines.append("")
    lines.append(f"    Progress: {completed}/{total} steps completed")
    lines.append(f"    Last saved: {state.last_modified}")
    lines.append(f"  {sep}")
    return "\n".join(lines)


# ── Document intake ─────────────────────────────────────────────────────────

def import_documents(case_number: str, source_path: str) -> list[str]:
    """Import documents from a user-provided path into the case intake folder.

    Security: source path is resolved to its real path (rejecting symlinks that
    escape), and each copied file's destination is validated to stay under the
    case intake folder to block traversal via `../` in filenames.
    """
    source = Path(source_path).resolve(strict=False)
    if not source.exists():
        raise FileNotFoundError(f"Source not found: {source_path}")

    target = (get_case_path(case_number) / "intake_docs").resolve()
    target.mkdir(parents=True, exist_ok=True)

    def _safe_dest(dest: Path) -> Path:
        resolved = dest.resolve()
        if target not in resolved.parents and resolved != target:
            raise ValueError(f"Refusing to write outside intake dir: {dest}")
        return resolved

    imported: list[str] = []
    if source.is_file():
        dest = _safe_dest(target / source.name)
        shutil.copy2(source, dest)
        imported.append(source.name)
    elif source.is_dir():
        for f in source.rglob("*"):
            # Skip symlinks to avoid escaping source sandbox
            if f.is_symlink() or not f.is_file() or f.name.startswith("."):
                continue
            rel = f.relative_to(source)
            dest = _safe_dest(target / rel)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            imported.append(str(rel))

    return imported


def list_intake_docs(case_number: str) -> list[str]:
    """List all documents in the case intake folder."""
    intake = get_case_path(case_number) / "intake_docs"
    if not intake.exists():
        return []
    return [str(f.relative_to(intake)) for f in intake.rglob("*") if f.is_file()]


# ── Output management ───────────────────────────────────────────────────────

def get_output_path(case_number: str, doc_type: str, party_name: str = "") -> Path:
    """Get the output path for a generated document.

    Naming convention: <doc_type>_<party_name>.md with spaces as underscores.
    """
    out_dir = get_case_path(case_number) / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_type = doc_type.replace(" ", "_").replace("/", "_")
    if party_name:
        safe_party = party_name.replace(" ", "_").replace(",", "")
        filename = f"{safe_type}_{safe_party}"
    else:
        filename = safe_type
    return out_dir / filename


def list_outputs(case_number: str) -> list[str]:
    """List all generated output files for a case."""
    out_dir = get_case_path(case_number) / "output"
    if not out_dir.exists():
        return []
    return [str(f.relative_to(out_dir)) for f in out_dir.rglob("*") if f.is_file()]
