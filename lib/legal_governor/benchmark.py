"""Attorney-reviewed legal benchmark lifecycle.

The benchmark deliberately separates draft records, source packets, attorney
reviews, adjudications, released gold labels, and model runs. This module never
invents legal questions, authorities, reviewer identities, or gold decisions.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DOMAINS = (
    ("delaware-corporate", 1500),
    ("securities-funds", 1200),
    ("contracts", 1000),
    ("employment", 1000),
    ("federal-procedure-evidence", 1000),
    ("tax", 1000),
    ("bankruptcy", 800),
    ("administrative-law", 800),
    ("constitutional-law", 700),
    ("state-choice-of-law", 500),
    ("citation-quotation-holding-traps", 500),
)
TRAPS = (
    "FABRICATED_CASE", "WRONG_HOLDING", "OVERRULED_PRECEDENT",
    "SUPERSEDED_STATUTE", "WRONG_JURISDICTION", "WRONG_DATE",
    "OMITTED_EXCEPTION", "DISSENT_AS_HOLDING", "PARTY_ARGUMENT_AS_HOLDING",
    "FALSE_PREMISE", "ADVERSE_AUTHORITY_OMISSION",
)
DECISIONS = {"PASS", "REVIEW_REQUIRED", "BLOCK"}
MATERIALITY = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
STATUSES = {"DRAFT", "SOURCE_LOADED", "REVIEWED", "ADJUDICATED", "RELEASED"}
SPLITS = {"development", "calibration", "locked-evaluation"}
TOTAL = sum(count for _, count in DOMAINS)
CHALLENGE_TARGET = 0.20


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def row_hash(row: dict) -> str:
    copy = dict(row)
    copy.pop("record_hash", None)
    return digest(copy)


def paths(root: Path) -> dict[str, Path]:
    root.mkdir(parents=True, exist_ok=True)
    return {
        "root": root,
        "manifest": root / "manifest.json",
        "source_packets": root / "source-packets.jsonl",
        "items": root / "items.jsonl",
        "reviews": root / "reviews.jsonl",
        "adjudications": root / "adjudications.jsonl",
        "releases": root / "releases.jsonl",
        "reviewers": root / "reviewers.jsonl",
        "audit": root / "audit.jsonl",
        "runs": root / "runs",
    }


def read_json(path: Path, default):
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{line_no} invalid JSON: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def _refresh_manifest(p: dict[str, Path]) -> None:
    manifest = read_json(p["manifest"], {})
    if not manifest:
        return
    manifest["items_sha256"] = hashlib.sha256(p["items"].read_bytes()).hexdigest()
    manifest["updated_at"] = now()
    p["manifest"].write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def _split(item_number: int) -> str:
    # Deterministic and domain-balanced because item_number is assigned inside
    # each domain before global numbering. Locked rows are never tuned on.
    slot = (item_number - 1) % 10
    return "locked-evaluation" if slot < 2 else ("calibration" if slot == 2 else "development")


def _trap(domain_index: int, local_index: int, count: int) -> list[str]:
    # Exactly 20% of each domain is reserved for typed challenge cases. The
    # question and authority remain blank until sourced material is imported.
    challenge_count = int(round(count * CHALLENGE_TARGET))
    if local_index > challenge_count:
        return []
    return [TRAPS[(domain_index + local_index - 1) % len(TRAPS)]]


def scaffold(root: Path, *, overwrite: bool = False) -> dict:
    p = paths(root)
    if p["items"].exists() and not overwrite:
        raise ValueError("benchmark already exists; use --overwrite only after preserving the existing package")
    rows = []
    global_number = 0
    for domain_index, (domain, count) in enumerate(DOMAINS):
        for local_index in range(1, count + 1):
            global_number += 1
            row = {
                "id": f"BENCH-{global_number:06d}",
                "domain": domain,
                "question": "",
                "jurisdiction": "",
                "gold_decision": None,
                "gold_authorities": [],
                "materiality": "HIGH",
                "reviewer_1": None,
                "reviewer_2": None,
                "adjudicator": None,
                "adjudication_reason": None,
                "trap_types": _trap(domain_index, local_index, count),
                "status": "DRAFT",
                "split": _split(local_index),
                "source_packet_id": None,
                "created_at": now(),
            }
            row["record_hash"] = row_hash(row)
            rows.append(row)
    write_jsonl(p["items"], rows)
    manifest = {
        "schema": "glaw-attorney-benchmark/v1",
        "created_at": now(),
        "total": TOTAL,
        "challenge_target": CHALLENGE_TARGET,
        "domains": [{"id": domain, "count": count} for domain, count in DOMAINS],
        "trap_types": list(TRAPS),
        "splits": {"development": 0.7, "calibration": 0.1, "locked-evaluation": 0.2},
        "gold_policy": "Only released rows with independent attorney review and source-backed authorities enter evaluation.",
        "authority_policy": "No authority, question, or gold decision may be invented by the scaffold.",
        "review_policy": "Two independent named counsel reviews; adjudicator required only for disagreement.",
        "items_sha256": hashlib.sha256(p["items"].read_bytes()).hexdigest(),
    }
    p["manifest"].write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for filename in ("source_packets", "reviews", "adjudications", "releases", "reviewers", "audit"):
        p[filename].touch()
    return manifest


def validate(root: Path, *, require_released: bool = False) -> list[str]:
    p = paths(root)
    failures = []
    manifest = read_json(p["manifest"], {})
    rows = read_jsonl(p["items"])
    source_packet_rows = read_jsonl(p["source_packets"])
    source_packets = {row.get("id"): row for row in source_packet_rows}
    if manifest.get("schema") != "glaw-attorney-benchmark/v1":
        failures.append("benchmark manifest schema is missing or invalid")
    if len(source_packets) != len(source_packet_rows):
        failures.append("source-packets.jsonl contains duplicate packet IDs")
    for packet in source_packet_rows:
        packet_id = str(packet.get("id", ""))
        if not packet_id or not packet.get("authority_ids") or not packet.get("source_url"):
            failures.append(f"source packet {packet_id or '<missing-id>'} lacks identity, authority, or source URL")
        if not str(packet.get("source_url", "")).startswith(("https://", "http://")):
            failures.append(f"source packet {packet_id} has an invalid source URL")
        excerpt = packet.get("source_excerpt")
        excerpt_hash = packet.get("excerpt_sha256")
        if excerpt_hash and (not excerpt or hashlib.sha256(str(excerpt).encode("utf-8")).hexdigest() != excerpt_hash):
            failures.append(f"source packet {packet_id} excerpt hash mismatch")
    if len(rows) != TOTAL:
        failures.append(f"benchmark must contain exactly {TOTAL} rows; found {len(rows)}")
    if rows and manifest.get("items_sha256") != hashlib.sha256(p["items"].read_bytes()).hexdigest():
        failures.append("benchmark manifest items_sha256 is stale")
    ids = [row.get("id") for row in rows]
    if ids != [f"BENCH-{n:06d}" for n in range(1, TOTAL + 1)]:
        failures.append("benchmark IDs are not contiguous BENCH-000001 through BENCH-010000")
    counts = Counter(row.get("domain") for row in rows)
    for domain, expected in DOMAINS:
        if counts[domain] != expected:
            failures.append(f"domain {domain} count {counts[domain]} != {expected}")
    if set(counts) - {domain for domain, _ in DOMAINS}:
        failures.append("benchmark contains an unknown domain")
    seen_hashes = set()
    for row in rows:
        if row_hash(row) != row.get("record_hash"):
            failures.append(f"{row.get('id')} record_hash mismatch")
        if row.get("status") not in STATUSES:
            failures.append(f"{row.get('id')} has invalid status")
        if row.get("split") not in SPLITS:
            failures.append(f"{row.get('id')} has invalid split")
        if row.get("materiality") not in MATERIALITY:
            failures.append(f"{row.get('id')} has invalid materiality")
        traps = row.get("trap_types") or []
        if any(trap not in TRAPS for trap in traps):
            failures.append(f"{row.get('id')} has unknown trap type")
        if row.get("status") in {"SOURCE_LOADED", "REVIEWED", "ADJUDICATED", "RELEASED"}:
            if not str(row.get("question", "")).strip():
                failures.append(f"{row.get('id')} has released workflow status without a sourced question")
            if not row.get("jurisdiction"):
                failures.append(f"{row.get('id')} has released workflow status without jurisdiction")
            if not row.get("gold_authorities"):
                failures.append(f"{row.get('id')} has released workflow status without gold authorities")
            if not row.get("source_packet_id") or row.get("source_packet_id") not in source_packets:
                failures.append(f"{row.get('id')} references a missing source packet")
        question_hash = digest(str(row.get("question", "")).strip().lower()) if row.get("question") else None
        if question_hash and question_hash in seen_hashes:
            failures.append(f"duplicate question content: {row.get('id')}")
        if question_hash:
            seen_hashes.add(question_hash)
        if require_released and row.get("status") != "RELEASED":
            failures.append(f"{row.get('id')} is not released")
    if not any(row.get("trap_types") for row in rows):
        failures.append("benchmark has no typed challenge cases")
    return sorted(set(failures))


def _reviewer_map(p: dict) -> dict[str, dict]:
    return {str(row.get("reviewer_id")): row for row in read_jsonl(p["reviewers"])}


def register_reviewer(root: Path, reviewer: dict) -> dict:
    p = paths(root)
    rid = str(reviewer.get("reviewer_id", "")).strip()
    role = str(reviewer.get("role", "")).strip()
    if not rid or rid.lower() in {"attorney", "reviewer", "counsel", "tbd", "unknown"}:
        raise ValueError("reviewer_id must be a named counsel identifier, not a generic role")
    if role != "attorney":
        raise ValueError("reviewer role must be attorney")
    if not reviewer.get("conflict_attestation"):
        raise ValueError("reviewer conflict_attestation is required")
    current = _reviewer_map(p)
    if rid in current:
        raise ValueError(f"reviewer already registered: {rid}")
    row = dict(reviewer)
    row["registered_at"] = now()
    row["record_hash"] = row_hash(row)
    append_jsonl(p["reviewers"], row)
    return row


def import_items(root: Path, incoming: Iterable[dict]) -> dict:
    p = paths(root)
    rows = read_jsonl(p["items"])
    source_packets = {row.get("id"): row for row in read_jsonl(p["source_packets"])}
    by_id = {row.get("id"): row for row in rows}
    imported = 0
    failures = []
    for row in incoming:
        bid = str(row.get("id", ""))
        if bid not in by_id:
            failures.append(f"unknown benchmark id: {bid}")
            continue
        for key in ("question", "jurisdiction", "gold_authorities", "source_packet_id"):
            if row.get(key) in (None, "", [], {}):
                failures.append(f"{bid}.{key} is required for source import")
        if row.get("source_packet_id") not in source_packets:
            failures.append(f"{bid}.source_packet_id is not present in source-packets.jsonl")
        if not isinstance(row.get("gold_authorities"), list):
            failures.append(f"{bid}.gold_authorities must be a list")
            continue
        packet = source_packets.get(row.get("source_packet_id"), {})
        packet_authorities = set(packet.get("authority_ids", []))
        packet_authorities.update(filter(None, [packet.get("citation"), packet.get("title")]))
        if not set(row.get("gold_authorities", [])).issubset(packet_authorities):
            failures.append(f"{bid}.gold_authorities are not all identified by its source packet")
        target = by_id[bid]
        if target.get("status") == "RELEASED":
            failures.append(f"{bid} is already released and immutable")
            continue
        for key in ("question", "jurisdiction", "gold_authorities", "source_packet_id", "materiality", "trap_types"):
            if key in row:
                target[key] = row[key]
        target["status"] = "SOURCE_LOADED"
        target["record_hash"] = row_hash(target)
        imported += 1
    if failures:
        raise ValueError("; ".join(failures))
    write_jsonl(p["items"], rows)
    _refresh_manifest(p)
    return {"imported": imported, "items_sha256": hashlib.sha256(p["items"].read_bytes()).hexdigest()}


def add_review(root: Path, review: dict) -> dict:
    p = paths(root)
    bid = str(review.get("benchmark_id", ""))
    reviewer_id = str(review.get("reviewer_id", ""))
    item = next((row for row in read_jsonl(p["items"]) if row.get("id") == bid), None)
    if not item:
        raise ValueError(f"unknown benchmark id: {bid}")
    if item.get("status") == "RELEASED":
        raise ValueError("released benchmark rows are immutable")
    if reviewer_id not in _reviewer_map(p):
        raise ValueError(f"reviewer is not registered: {reviewer_id}")
    if review.get("decision") not in DECISIONS:
        raise ValueError("review decision must be PASS, REVIEW_REQUIRED, or BLOCK")
    if review.get("materiality") not in MATERIALITY:
        raise ValueError("review materiality is invalid")
    if not review.get("authorities") or not str(review.get("reasoning_summary", "")).strip():
        raise ValueError("review requires authorities and reasoning_summary")
    current = [row for row in read_jsonl(p["reviews"]) if row.get("benchmark_id") == bid and row.get("reviewer_id") == reviewer_id]
    if current:
        raise ValueError("reviewer may submit only one review per benchmark item")
    row = dict(review)
    row["reviewed_at"] = now()
    row["record_hash"] = row_hash(row)
    append_jsonl(p["reviews"], row)
    return row


def adjudicate(root: Path, decision: dict) -> dict:
    p = paths(root)
    bid = str(decision.get("benchmark_id", ""))
    reviews = [row for row in read_jsonl(p["reviews"]) if row.get("benchmark_id") == bid]
    if len(reviews) < 2 or reviews[0].get("decision") == reviews[1].get("decision"):
        raise ValueError("adjudication is required only when two independent reviews disagree")
    if decision.get("decision") not in DECISIONS or not str(decision.get("adjudication_reason", "")).strip():
        raise ValueError("adjudication requires a valid decision and reason")
    if decision.get("adjudicator") in {row.get("reviewer_id") for row in reviews}:
        raise ValueError("adjudicator must be independent from both reviewers")
    if decision.get("adjudicator") not in _reviewer_map(p):
        raise ValueError("adjudicator is not registered")
    row = dict(decision)
    row["adjudicated_at"] = now()
    row["record_hash"] = row_hash(row)
    append_jsonl(p["adjudications"], row)
    return row


def release(root: Path) -> dict:
    p = paths(root)
    failures = validate(root)
    if failures:
        raise ValueError("benchmark structural validation failed: " + "; ".join(failures[:20]))
    rows = read_jsonl(p["items"])
    reviews = defaultdict(list)
    for row in read_jsonl(p["reviews"]):
        reviews[row.get("benchmark_id")].append(row)
    adjudications = {row.get("benchmark_id"): row for row in read_jsonl(p["adjudications"])}
    released = 0
    for item in rows:
        if item.get("status") == "RELEASED":
            continue
        item_reviews = reviews.get(item.get("id"), [])
        if len(item_reviews) < 2 or item_reviews[0].get("reviewer_id") == item_reviews[1].get("reviewer_id"):
            continue
        decisions = {row.get("decision") for row in item_reviews[:2]}
        final = next(iter(decisions)) if len(decisions) == 1 else adjudications.get(item.get("id"), {}).get("decision")
        if final not in DECISIONS:
            continue
        if len(decisions) > 1 and item.get("id") not in adjudications:
            continue
        item["gold_decision"] = final
        item["reviewer_1"] = item_reviews[0].get("reviewer_id")
        item["reviewer_2"] = item_reviews[1].get("reviewer_id")
        if item.get("id") in adjudications:
            item["adjudicator"] = adjudications[item["id"]].get("adjudicator")
            item["adjudication_reason"] = adjudications[item["id"]].get("adjudication_reason")
        item["status"] = "RELEASED"
        item["record_hash"] = row_hash(item)
        append_jsonl(p["releases"], {"benchmark_id": item["id"], "released_at": now(), "gold_decision": final})
        released += 1
    write_jsonl(p["items"], rows)
    _refresh_manifest(p)
    return {"released": released, "total_released": sum(row.get("status") == "RELEASED" for row in rows)}


def audit(root: Path) -> dict:
    p = paths(root)
    failures = validate(root)
    hashes = {}
    for key in ("manifest", "items", "source_packets", "reviews", "adjudications", "releases", "reviewers"):
        path = p[key]
        hashes[key] = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""
    return {"status": "PASS" if not failures else "BLOCK", "failures": failures, "hashes": hashes}
