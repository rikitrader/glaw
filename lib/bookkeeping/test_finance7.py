#!/usr/bin/env python3
"""Smoke test for the scheduled close runner (glaw-close-run). Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _fresh():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-close-")
    import importlib
    import ledger as L
    importlib.reload(L)
    import close_run as CR
    importlib.reload(CR)
    return L, CR


def test_clean_close_passes_and_writes_package():
    L, CR = _fresh()
    led = L.Ledger("acme")
    led.post({"date": "2026-06-10", "lines": [{"account": "Assets:Bank:Checking", "debit": 100000},
                                              {"account": "Income:Sales", "credit": 60000},
                                              {"account": "Equity:Contributions", "credit": 40000}]})
    led.post({"date": "2026-06-20", "lines": [{"account": "Expenses:Rent", "debit": 5000},
                                              {"account": "Assets:Bank:Checking", "credit": 5000}]})
    out = tempfile.mkdtemp(prefix="glaw-pkg-")
    res = CR.run_close("acme", period="2026-06", out_dir=out, lock=True, entity="Acme LP")
    assert res["gate_passed"] is True
    assert res["net_income"] == "55000"
    assert res["locked_through"] == "2026-06-30"
    pkg = Path(res["package_dir"])
    for f in ("statements.txt", "comparative.txt", "dashboard.txt", "narrative.md",
              "books-doctor.txt", "summary.json"):
        assert (pkg / f).exists(), f"missing artifact {f}"
    # locking actually took: a back-dated post is now rejected
    try:
        led.post({"date": "2026-06-15", "lines": [{"account": "Assets:Bank:Checking", "debit": 1},
                                                  {"account": "Income:Sales", "credit": 1}]})
        raise AssertionError("post into locked period must be rejected after close --lock")
    except L.LedgerError:
        pass
    print("  ✓ close-run: clean book → CLOSE PASSED, full package written, period locked")


def test_broken_books_fail_close():
    L, CR = _fresh()
    # a payment with no deposit drives cash negative → books-doctor [cash] fails
    L.Ledger("bad").post({"date": "2026-06-20", "lines": [{"account": "Expenses:Rent", "debit": 5000},
                                                          {"account": "Assets:Bank:Checking", "credit": 5000}]})
    res = CR.run_close("bad", period="2026-06", lock=True)
    assert res["gate_passed"] is False, "negative cash must fail the close gate"
    assert res["locked_through"] is None, "must NOT lock when the gate fails"
    print("  ✓ close-run: negative-cash book → CLOSE FAILED, period left unlocked")


def main() -> int:
    test_clean_close_passes_and_writes_package()
    test_broken_books_fail_close()
    print("OK: scheduled close smoke passed (clean → pass+lock, broken → fail+unlocked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
