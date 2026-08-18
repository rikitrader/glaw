"""Source-locked, hash-addressed RAG context builder.

This is retrieval packaging, not semantic truth. Every context item must point to
an existing hashed citation-corpus row or the build fails.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def _hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build(matter: Path, request: dict) -> dict:
    corpus_path = matter / "citation_corpus.jsonl"
    citations_path = matter / "citations.jsonl"
    if not corpus_path.is_file():
        raise ValueError("citation corpus is missing")
    corpus = {}
    for line in corpus_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            corpus[str(row.get("id"))] = row
    verified = {}
    if citations_path.is_file():
        for line in citations_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("status") == "verified":
                    verified[str(row.get("id"))] = row
    requested = request.get("corpus_ids")
    if not isinstance(requested, list) or not requested:
        raise ValueError("RAG request must identify corpus_ids explicitly")
    sources = []
    failures = []
    for corpus_id in requested:
        cid = str(corpus_id)
        row = corpus.get(cid)
        if not row:
            failures.append(f"RAG corpus id missing: {cid}")
            continue
        if row.get("trust_level") not in {"authoritative", "authenticated-copy"}:
            failures.append(f"RAG source is not authoritative: {cid}")
        source_path = matter / str(row.get("source_path", ""))
        if not source_path.is_file():
            failures.append(f"RAG source file missing: {cid}")
            continue
        text = source_path.read_text(encoding="utf-8", errors="replace")
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != row.get("source_sha256"):
            failures.append(f"RAG source hash mismatch: {cid}")
        citation_rows = [item for item in verified.values() if str(item.get("corpus_id")) == cid]
        if not citation_rows:
            failures.append(f"RAG source has no verified citation binding: {cid}")
        sources.append({
            "corpus_id": cid,
            "source_url": row.get("source_url"),
            "source_sha256": row.get("source_sha256"),
            "segment": row.get("segment"),
            "segment_sha256": row.get("segment_sha256"),
            "verified_citation_ids": sorted(str(item.get("id")) for item in citation_rows),
        })
    if failures:
        raise ValueError("; ".join(failures))
    context = {
        "schema": "glaw-rag-context/v1",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "question": request.get("question", ""),
        "jurisdiction": request.get("jurisdiction", ""),
        "supporting_propositions": request.get("supporting_propositions", []),
        "adverse_propositions": request.get("adverse_propositions", []),
        "sources": sources,
        "provenance_rule": "Only verified authoritative/authenticated corpus rows may enter this context.",
    }
    context["context_sha256"] = _hash(context)
    path = matter / "workpapers" / "rag-context.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(context, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return context


def verify(matter: Path) -> dict:
    path = matter / "workpapers" / "rag-context.json"
    if not path.is_file():
        return {"status": "BLOCK", "failures": ["RAG context is missing"]}
    try:
        context = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"status": "BLOCK", "failures": ["RAG context is invalid JSON"]}
    expected = context.get("context_sha256")
    copy = dict(context)
    copy.pop("context_sha256", None)
    failures = []
    if expected != _hash(copy):
        failures.append("RAG context digest mismatch")
    if not context.get("question"):
        failures.append("RAG context question is missing")
    if not context.get("sources"):
        failures.append("RAG context sources are missing")
    return {"status": "PASS" if not failures else "BLOCK", "context_sha256": expected, "failures": failures}
