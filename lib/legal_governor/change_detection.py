"""Source-change detection that marks dependent workpapers stale."""
from __future__ import annotations

from legal_governor.provenance import sha256_text


def detect(previous: list[dict], current: list[dict]) -> dict:
    old = {str(row.get("id")): row.get("raw_text_hash") for row in previous}
    new = {str(row.get("id")): row.get("raw_text_hash") for row in current}
    changed = sorted(key for key in set(old) | set(new) if old.get(key) != new.get(key))
    return {"changed_source_ids": changed, "revalidation_required": bool(changed), "fingerprint": sha256_text(str(sorted(new.items())))}

