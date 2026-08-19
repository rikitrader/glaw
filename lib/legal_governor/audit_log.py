"""Append-only hash-chained Governor audit records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def append(path: Path, event: dict) -> dict:
    previous = ""
    if path.exists():
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if lines:
            previous = json.loads(lines[-1]).get("record_hash", "")
    record = dict(event)
    record["previous_hash"] = previous
    raw = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    record["record_hash"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def verify(path: Path) -> list[str]:
    failures = []
    previous = ""
    if not path.exists():
        return ["Governor audit log is missing"]
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            failures.append(f"audit line {index} is invalid JSON")
            continue
        expected = row.get("record_hash")
        if row.get("previous_hash", "") != previous:
            failures.append(f"audit line {index} previous_hash mismatch")
        copy = dict(row)
        copy.pop("record_hash", None)
        raw = json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        if expected != hashlib.sha256(raw.encode("utf-8")).hexdigest():
            failures.append(f"audit line {index} record_hash mismatch")
        previous = expected or ""
    return failures
