#!/usr/bin/env python3
"""Smoke test for the GLAW accounting glossary (stdlib only — no venv needed)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import glossary as G   # noqa: E402


def main() -> int:
    idx = G.build_index()
    assert len(idx) >= 80, f"expected a substantive glossary, got {len(idx)} terms"
    for term in ("accrual basis", "double-entry", "depreciation", "matching principle",
                 "dso", "materiality", "retained earnings", "nexus"):
        assert G.lookup(term), f"missing core term: {term}"
    assert any("depreciation" in v["term"].lower() for v in G.search("depreciation"))
    print(f"OK: glossary smoke passed ({len(idx)} terms indexed, core terms resolve)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
