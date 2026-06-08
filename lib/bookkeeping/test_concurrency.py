#!/usr/bin/env python3
"""Concurrency test for the ledger: the flock around post() must keep concurrent posters from
racing on next_id / the chain head. Threads share a process here (covers the in-process race);
the file lock additionally serializes separate processes (cron + manual). Temp GLAW_HOME."""
from __future__ import annotations

import os
import sys
import tempfile
import threading
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def test_threaded_posts_are_serialized():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-conc-")
    import importlib
    import ledger as L
    importlib.reload(L)
    N, T = 25, 4                                  # 4 threads × 25 posts = 100 entries
    errors = []

    def worker():
        led = L.Ledger("c")                       # each thread its own Ledger instance / fd
        for _ in range(N):
            try:
                led.post({"date": "2026-01-01", "memo": "x",
                          "lines": [{"account": "Assets:Bank:Checking", "debit": 1},
                                    {"account": "Income:Sales", "credit": 1}]})
            except Exception as e:                # pragma: no cover
                errors.append(repr(e))

    threads = [threading.Thread(target=worker) for _ in range(T)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, errors
    led = L.Ledger("c")
    entries = led.entries()
    ids = [e["id"] for e in entries]
    assert len(entries) == N * T, f"lost/extra entries: {len(entries)} != {N*T}"
    assert len(set(ids)) == len(ids), "duplicate ids — the lock failed to serialize"
    assert sorted(ids) == list(range(1, N * T + 1)), "ids not contiguous 1..100"
    # the chain is intact and the book balances despite concurrent posting
    assert L.verify_integrity(entries) == [], "concurrent posting must not corrupt the chain"
    bal = led.balances()
    assert bal["Assets:Bank:Checking"] == Decimal("100") and sum(bal.values()) == 0
    print(f"  ✓ concurrency: {T} threads × {N} posts → 100 unique contiguous ids, chain intact, balanced")


def main() -> int:
    test_threaded_posts_are_serialized()
    print("OK: ledger concurrency (flock) test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
