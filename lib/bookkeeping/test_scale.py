#!/usr/bin/env python3
"""Scale test: a larger book stays correct with the entries() parse-memo and O(1) seen_hashes
dedup. Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def test_500_entry_book_correct():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-scale-")
    import importlib
    import ledger as L
    importlib.reload(L)
    led = L.Ledger("big")
    N = 500
    for i in range(1, N + 1):
        mm = (i % 12) + 1
        led.post({"date": f"2026-{mm:02d}-01", "memo": f"e{i}",
                  "lines": [{"account": "Assets:Bank:Checking", "debit": 10},
                            {"account": "Income:Sales", "credit": 10}]})
    entries = led.entries()
    assert len(entries) == N
    bal = led.balances()
    assert bal["Assets:Bank:Checking"] == Decimal("5000") and sum(bal.values()) == 0
    # as-of filtering works off the same memo (Jan only = months==1 → i%12==0 → i in 12,24,...)
    jan = led.entries("2026-01-31")
    assert all(e["date"].startswith("2026-01") for e in jan) and len(jan) > 0
    # the chain holds across 500 entries
    assert L.verify_integrity(entries) == []
    # repeated queries are consistent (memo returns the same data)
    assert led.balances() == bal and led.entries() == entries
    print(f"  ✓ scale: {N}-entry book balances (5,000), as-of filters, chain intact over 500")


def test_o1_dedup_idempotent():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-dedup-")
    import importlib
    import ledger as L
    importlib.reload(L)
    led = L.Ledger("d")
    rows = [{"booking_date": "2026-01-05", "amount": "500", "category": "Income:Sales",
             "transaction_hash": f"h{i}", "description": "x"} for i in range(200)]
    r1 = led.import_bank(rows)
    assert r1["posted"] == 200
    r2 = led.import_bank(rows)                  # re-import → all dedup via O(1) dict membership
    assert r2["posted"] == 0 and r2["skipped_duplicates"] == 200
    # meta stores seen_hashes as a dict (O(1))
    assert isinstance(led._meta()["seen_hashes"], dict)
    print("  ✓ scale: O(1) dedup — 200 rows post once, re-import skips all 200 (seen_hashes is a dict)")


def main() -> int:
    test_500_entry_book_correct()
    test_o1_dedup_idempotent()
    print("OK: ledger scale (memo + O(1) dedup) test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
