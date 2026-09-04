#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PYTHONPATH="$ROOT/lib" python3 - "$TMP/legal-10k" <<'PY'
import json
import sys
from pathlib import Path

from legal_governor import benchmark

root = Path(sys.argv[1])
benchmark.scaffold(root)
paths = benchmark.paths(root)
draft_root = root.parent / "draft-only"
benchmark.scaffold(draft_root)
benchmark.register_reviewer(draft_root, {
    "reviewer_id": "DRAFT-COUNSEL",
    "role": "attorney",
    "conflict_attestation": True,
})
try:
    benchmark.add_review(draft_root, {
        "benchmark_id": "BENCH-000001",
        "reviewer_id": "DRAFT-COUNSEL",
        "decision": "PASS",
        "authorities": ["SRC-001"],
        "reasoning_summary": "Not source loaded.",
        "materiality": "HIGH",
        "conflict_attestation": True,
    })
except ValueError as exc:
    assert "source-loaded" in str(exc)
else:
    raise AssertionError("review was accepted for a DRAFT item")
paths["source_packets"].write_text(json.dumps({
    "id": "PACKET-001",
    "authority_ids": ["SRC-001"],
    "source_url": "https://example.test/authority",
}) + "\n", encoding="utf-8")
benchmark.import_items(root, [{
    "id": "BENCH-000001",
    "question": "What is the verified rule?",
    "jurisdiction": "US-DE",
    "gold_authorities": ["SRC-001"],
    "source_packet_id": "PACKET-001",
}])
for rid in ("COUNSEL-001", "COUNSEL-002"):
    benchmark.register_reviewer(root, {
        "reviewer_id": rid,
        "role": "attorney",
        "conflict_attestation": True,
    })

base = {
    "benchmark_id": "BENCH-000001",
    "reviewer_id": "COUNSEL-001",
    "decision": "PASS",
    "authorities": ["SRC-001"],
    "reasoning_summary": "The source packet supports the conclusion.",
    "materiality": "HIGH",
}
try:
    benchmark.add_review(root, {**base, "authorities": ["SRC-UNRELATED"], "conflict_attestation": True})
except ValueError as exc:
    assert "source-backed gold authorities" in str(exc)
else:
    raise AssertionError("out-of-scope authority was accepted")
try:
    benchmark.add_review(root, base)
except ValueError as exc:
    assert "conflict_attestation" in str(exc)
else:
    raise AssertionError("review without conflict attestation was accepted")

benchmark.add_review(root, {**base, "conflict_attestation": True})
benchmark.add_review(root, {**base, "reviewer_id": "COUNSEL-002", "conflict_attestation": True})
assert benchmark.validate(root) == []

rows = benchmark.read_jsonl(paths["reviews"])
rows[0]["reasoning_summary"] = "tampered after signing"
benchmark.write_jsonl(paths["reviews"], rows)
failures = benchmark.validate(root)
assert any("record_hash mismatch" in failure for failure in failures), failures
try:
    benchmark.release(root)
except ValueError as exc:
    assert "record_hash mismatch" in str(exc)
else:
    raise AssertionError("release bypassed tampered review")
print("ALL PASS")
PY
