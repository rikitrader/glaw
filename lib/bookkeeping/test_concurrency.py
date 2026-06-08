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


def test_read_survives_torn_inflight_append():
    """A read (balances/entries) racing a post() in another process can see a torn trailing line
    (in-flight append). It must SURVIVE (skip the incomplete last line), still flag real mid-file
    corruption, and pick up the entry once it commits."""
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-torn-")
    import importlib
    import ledger as L
    importlib.reload(L)
    led = L.Ledger("t")
    for _ in range(3):
        led.post({"date": "2026-01-01", "lines": [{"account": "Assets:Bank:Checking", "debit": 10},
                                                  {"account": "Income:Sales", "credit": 10}]})
    # torn trailing line (no newline) — an append mid-flight
    with led.path.open("a") as fh:
        fh.write('{"id":4,"date":"2026-01-02","memo":"par')
    led._entries_cache = None
    assert led.balances()["Assets:Bank:Checking"] == Decimal("30"), "read must survive a torn line"
    assert len(led.entries()) == 3
    # commit the append → the 4th entry is now folded in
    with led.path.open("a") as fh:
        fh.write('t","lines":[{"account":"Assets:Bank:Checking","debit":"5","credit":"0"},'
                 '{"account":"Income:Sales","debit":"0","credit":"5"}]}\n')
    led._entries_cache = None
    assert led.balances()["Assets:Bank:Checking"] == Decimal("35")
    # a MID-FILE corrupt line is still flagged (not silently swallowed)
    lines = led.path.read_text().splitlines(); lines[1] = "{garbage"
    led.path.write_text("\n".join(lines) + "\n"); led._entries_cache = None
    try:
        led.entries()
        raise AssertionError("mid-file corruption must be flagged")
    except L.LedgerError:
        pass
    print("  ✓ concurrency: read survives a torn in-flight append; mid-file corruption still flagged")


def main() -> int:
    test_threaded_posts_are_serialized()
    test_read_survives_torn_inflight_append()
    print("OK: ledger concurrency (flock + torn-line) test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
