#!/usr/bin/env python3
"""Persistent balance-index tests: the index-backed balances() must PROVABLY equal the full
recompute — within a process, across a fresh (cold-cache, cross-process) instance, and after
incremental appends. Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _full_recompute(led):
    """Ground truth: sum every posting line directly from the file (no index)."""
    import json
    bal = {}
    for line in led.path.read_text().splitlines():
        if not line.strip():
            continue
        for ln in json.loads(line)["lines"]:
            bal[ln["account"]] = bal.get(ln["account"], Decimal("0")) + Decimal(ln["debit"]) - Decimal(ln["credit"])
    return {a: b for a, b in bal.items()}


def test_index_equals_full_recompute():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-idx-")
    import importlib
    import ledger as L
    importlib.reload(L)
    led = L.Ledger("b")
    for i in range(1, 51):
        led.post({"date": "2026-01-01", "memo": f"e{i}",
                  "lines": [{"account": "Assets:Bank:Checking", "debit": 7},
                            {"account": f"Income:Cust{i % 5}", "credit": 7}]})
    # 1) index-backed balances == full recompute
    assert led.balances() == _full_recompute(led)
    assert led.index_path.exists(), "the persistent index file must be written"
    # 2) incremental: more posts → index catches up via the byte offset, still equal
    for i in range(51, 101):
        led.post({"date": "2026-02-01", "memo": f"e{i}",
                  "lines": [{"account": "Expenses:Ops", "debit": 3},
                            {"account": "Assets:Bank:Checking", "credit": 3}]})
    assert led.balances() == _full_recompute(led)
    # 3) CROSS-PROCESS: a brand-new Ledger instance (cold per-instance cache) reads the persisted
    #    index + the delta and gets the same answer
    cold = L.Ledger("b")
    assert cold.balances() == _full_recompute(led)
    assert cold.balances()["Assets:Bank:Checking"] == Decimal("200")   # 50×7 − 50×3
    print("  ✓ index: balances == full recompute (within-process, incremental, cross-process cold)")


def test_index_self_heals_on_shrink():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-idx2-")
    import importlib
    import ledger as L
    importlib.reload(L)
    led = L.Ledger("b")
    for i in range(1, 11):
        led.post({"date": "2026-01-01", "lines": [{"account": "Assets:Bank:Checking", "debit": 10},
                                                  {"account": "Income:Sales", "credit": 10}]})
    led.balances()                                       # builds the index through EOF
    # rewrite the file shorter (e.g. a rebuild) — the index's offset now exceeds the file size
    lines = led.path.read_text().splitlines()[:4]
    led.path.write_text("\n".join(lines) + "\n")
    led._entries_cache = None
    fresh = L.Ledger("b")                                # cold instance
    assert fresh.balances() == _full_recompute(fresh), "index must rebuild when the file shrinks"
    assert fresh.balances()["Assets:Bank:Checking"] == Decimal("40")   # 4 entries × 10
    print("  ✓ index: self-heals (rebuilds) when the ledger file shrinks under the indexed offset")


def main() -> int:
    test_index_equals_full_recompute()
    test_index_self_heals_on_shrink()
    print("OK: persistent balance-index tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
