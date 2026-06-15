"""Shared helpers for ftc_engine CLI command handlers."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _load_case(path: str) -> dict:
    """Load and schema-check a case JSON file.

    Validation is intentionally minimal — structural only. Claim-specific
    checks run later in the pipeline with domain-aware diagnostics.
    """
    try:
        data = json.loads(Path(path).read_text())
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    errors = _validate_case_shape(data)
    if errors:
        print(f"Error: Case file has invalid shape ({path}):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    return data


def _validate_case_shape(data) -> list[str]:
    """Return a list of human-readable shape errors for the case input."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root must be an object"]
    if "parties" in data and not isinstance(data["parties"], dict):
        errors.append("'parties' must be an object with 'plaintiffs' and 'defendants'")
    else:
        parties = data.get("parties", {}) or {}
        for side in ("plaintiffs", "defendants"):
            v = parties.get(side, [])
            if v and not isinstance(v, list):
                errors.append(f"'parties.{side}' must be an array")
    if "facts" in data and not isinstance(data["facts"], list):
        errors.append("'facts' must be an array")
    if "claims_requested" in data and not isinstance(data["claims_requested"], list):
        errors.append("'claims_requested' must be an array of claim keys")
    if "relief_requested" in data and not isinstance(data["relief_requested"], list):
        errors.append("'relief_requested' must be an array")
    if "court" in data and not isinstance(data["court"], dict):
        errors.append("'court' must be an object")
    return errors


def _risk_bar(score: int) -> str:
    """Generate ASCII risk bar."""
    score = max(0, min(100, score))
    filled = score // 5
    empty = 20 - filled
    return f"[{'#' * filled}{'.' * empty}]"
