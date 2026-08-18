"""Immutable source provenance and source-universe validation."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


AUTHORITY_ORDER = {
    "constitution": 1, "statute": 2, "regulation": 3, "official_opinion": 4,
    "court_rule": 5, "agency_decision": 6, "official_docket": 7,
    "authenticated_filing": 8, "government_guidance": 9, "legal_database": 10,
    "treatise": 11, "commentary": 12,
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def validate_source(row: dict, matter: Path) -> list[str]:
    failures = []
    required = ("id", "jurisdiction", "authority_type", "title", "raw_text_hash", "text", "retrieved_at", "provider", "version")
    for key in required:
        if row.get(key) in (None, "", [], {}):
            failures.append(f"source.{key} is missing")
    authority_type = str(row.get("authority_type", ""))
    if authority_type not in AUTHORITY_ORDER:
        failures.append(f"source.authority_type is not recognized: {authority_type}")
    text = str(row.get("text", ""))
    if text and sha256_text(text) != row.get("raw_text_hash"):
        failures.append("source.raw_text_hash mismatch")
    source_path = row.get("raw_source_path")
    if source_path:
        path = (matter / str(source_path)).resolve()
        try:
            path.relative_to(matter.resolve())
        except ValueError:
            failures.append("source.raw_source_path escapes matter")
        else:
            if not path.is_file():
                failures.append("source.raw_source_path is missing")
            elif sha256_bytes(path.read_bytes()) != row.get("raw_file_hash"):
                failures.append("source.raw_file_hash mismatch")
    return failures


def ingest(matter: Path, request: dict) -> dict:
    """Create a source-universe row without overwriting source text."""
    text = str(request.get("text", ""))
    if not text:
        raise ValueError("source text is required; no synthetic source may be created")
    row = dict(request)
    row.setdefault("id", f"SRC-{sha256_text(text)[:16]}")
    row.setdefault("retrieved_at", now())
    row.setdefault("version", "1")
    row.setdefault("raw_text_hash", sha256_text(text))
    row["raw_text_hash"] = sha256_text(text)
    failures = validate_source(row, matter)
    if failures:
        raise ValueError("; ".join(failures))
    path = matter / "workpapers" / "source-universe.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.exists() else []
    if any(item.get("id") == row["id"] and item.get("raw_text_hash") != row["raw_text_hash"] for item in existing):
        raise ValueError("source id already exists with different immutable content")
    if not any(item.get("id") == row["id"] and item.get("raw_text_hash") == row["raw_text_hash"] for item in existing):
        path.open("a", encoding="utf-8").write(json.dumps(row, sort_keys=True) + "\n")
    return row


def load(matter: Path) -> list[dict]:
    path = matter / "workpapers" / "source-universe.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

