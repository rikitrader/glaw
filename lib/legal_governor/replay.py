"""Reproducible replay manifest; it records references, not hidden chain-of-thought."""
from __future__ import annotations

import json
from pathlib import Path


def write(matter: Path, manifest: dict) -> Path:
    required = ("request_id", "query", "source_hashes", "retrieval_queries", "model_versions", "governor_decision")
    missing = [key for key in required if manifest.get(key) in (None, "", [], {})]
    if missing:
        raise ValueError("replay manifest missing: " + ", ".join(missing))
    path = matter / "workpapers" / "replay-manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path

