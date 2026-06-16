"""Deterministic groundedness scoring for citation propositions.

This is not semantic proof. It is an auditable floor: a verified proposition must
show lexical grounding in the captured source segment and support summary before
the citation gate can clear.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from glaw_authority_sources import approved_authority_url


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "is", "it", "must", "of", "or", "that", "the", "this", "to", "with",
}
MIN_ENTITY_GROUNDING = 0.50
MIN_RELATION_PRESERVATION = 0.35
APPROVED_CORPUS_TRUST = {"authoritative", "authenticated-copy"}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def token_set(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}", str(value).lower())
        if token not in STOPWORDS
    }


def row_hash(row: dict) -> str:
    payload = dict(row)
    payload.pop("row_hash", None)
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def latest_by_id(rows: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in rows:
        out[str(row.get("id", ""))] = row
    return out


def score_row(citation: dict, corpus: dict) -> dict:
    proposition_tokens = token_set(citation.get("proposition", ""))
    support_tokens = token_set(citation.get("support_summary", ""))
    segment = str(corpus.get("segment", ""))
    segment_tokens = token_set(segment)

    grounded_tokens = sorted(proposition_tokens & segment_tokens)
    support_grounded_tokens = sorted(support_tokens & segment_tokens)
    entity_score = len(grounded_tokens) / max(1, len(proposition_tokens))
    relation_score = len(support_grounded_tokens) / max(1, len(support_tokens))
    missing_tokens = sorted(proposition_tokens - segment_tokens)
    status = (
        "pass"
        if entity_score >= MIN_ENTITY_GROUNDING and relation_score >= MIN_RELATION_PRESERVATION
        else "fail"
    )
    return {
        "citation_id": citation.get("id", ""),
        "corpus_id": citation.get("corpus_id", ""),
        "status": status,
        "method": "deterministic_lexical_floor_not_semantic_proof",
        "entity_grounding": round(entity_score, 4),
        "relation_preservation": round(relation_score, 4),
        "thresholds": {
            "entity_grounding": MIN_ENTITY_GROUNDING,
            "relation_preservation": MIN_RELATION_PRESERVATION,
        },
        "grounded_tokens": grounded_tokens,
        "support_grounded_tokens": support_grounded_tokens,
        "missing_proposition_tokens": missing_tokens,
        "citation_row_hash": row_hash(citation),
        "source_sha256": corpus.get("source_sha256", ""),
        "segment_sha256": corpus.get("segment_sha256", ""),
    }


def audit_matter(matter_dir: Path) -> dict:
    citations = latest_by_id(read_jsonl(matter_dir / "citations.jsonl"))
    corpus = latest_by_id(read_jsonl(matter_dir / "citation_corpus.jsonl"))
    rows = []
    failures = []
    for citation in citations.values():
        if citation.get("status") != "verified":
            continue
        corpus_id = str(citation.get("corpus_id", ""))
        corpus_row = corpus.get(corpus_id)
        if not corpus_row:
            failures.append(f"{citation.get('id')}: missing corpus {corpus_id}")
            continue
        if corpus_row.get("trust_level") not in APPROVED_CORPUS_TRUST:
            failures.append(
                f"{citation.get('id')}: corpus {corpus_id} is not authoritative "
                f"(trust={corpus_row.get('trust_level', 'untrusted')})"
            )
            continue
        if not approved_authority_url(str(corpus_row.get("source_url", ""))):
            failures.append(f"{citation.get('id')}: corpus {corpus_id} source domain is not approved")
            continue
        scored = score_row(citation, corpus_row)
        rows.append(scored)
        if scored["status"] != "pass":
            failures.append(
                f"{citation.get('id')}: groundedness below threshold "
                f"(entity={scored['entity_grounding']}, relation={scored['relation_preservation']})"
            )
    return {
        "status": "pass" if rows and not failures else "fail",
        "rows": rows,
        "failures": failures,
    }
