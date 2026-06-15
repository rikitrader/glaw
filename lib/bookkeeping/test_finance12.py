#!/usr/bin/env python3
"""Smoke test for multi-account reconstruction: transfers + continuity + orchestrator.
Temp GLAW_HOME; no network; reconstruct shells out to the source-first glaw-bank-ingest."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _fresh():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-rec-")
    import importlib
    import ledger as L
    importlib.reload(L)
    import transfers as TR
    importlib.reload(TR)
    return L, TR


def test_transfer_reclassification():
    L, TR = _fresh()
    led = L.Ledger("acme")
    # checking: job revenue 10k, transfer out 3k, materials 2k
    led.post({"date": "2026-01-05", "lines": [{"account": "Assets:Bank:Checking", "debit": 10000},
                                              {"account": "Income:JobRevenue", "credit": 10000}]})
    led.post({"date": "2026-01-10", "lines": [{"account": "Expenses:Transfers", "debit": 3000},
                                              {"account": "Assets:Bank:Checking", "credit": 3000}]})
    led.post({"date": "2026-01-20", "lines": [{"account": "Expenses:Materials", "debit": 2000},
                                              {"account": "Assets:Bank:Checking", "credit": 2000}]})
    # savings: transfer in 3k (miscategorized as income)
    led.post({"date": "2026-01-11", "lines": [{"account": "Assets:Bank:Savings", "debit": 3000},
                                              {"account": "Income:Transfers", "credit": 3000}]})
    r = TR.reclassify("acme")
    assert r["reclassified"] == 1, r
    bal = led.balances()
    # the bogus income and expense are netted to zero; gross figures corrected
    assert bal.get("Income:Transfers", Decimal("0")) == 0
    assert bal.get("Expenses:Transfers", Decimal("0")) == 0
    assert bal["Income:JobRevenue"] == Decimal("-10000")      # real revenue intact (credit)
    assert bal["Assets:Bank:Checking"] == Decimal("5000")     # cash unchanged & correct
    assert bal["Assets:Bank:Savings"] == Decimal("3000")
    assert sum(bal.values()) == 0
    assert TR.reclassify("acme")["reclassified"] == 0          # idempotent
    print("  ✓ transfers: 3k Checking→Savings netted (revenue 10k not 13k), cash intact, idempotent")


def test_transfer_false_positive_guard():
    L, TR = _fresh()
    led = L.Ledger("fp")
    # a real rent expense + a real sale, same amount/window, NO transfer evidence — must NOT net
    led.post({"date": "2026-01-05", "lines": [{"account": "Expenses:Rent", "debit": 3000},
                                              {"account": "Assets:Bank:Checking", "credit": 3000}]})
    led.post({"date": "2026-01-06", "lines": [{"account": "Assets:Bank:Savings", "debit": 3000},
                                              {"account": "Income:Sales", "credit": 3000}]})
    r = TR.reclassify("fp")
    assert r["reclassified"] == 0, "unrelated expense+income must NOT be auto-netted as a transfer"
    assert len(r["candidates"]) == 1, "the ambiguous pair must be flagged for review"
    assert led.balances()["Income:Sales"] == Decimal("-3000")   # real income untouched
    print("  ✓ transfers: unrelated expense+income flagged (not netted) — P&L not corrupted")


def test_continuity():
    import continuity as C
    good = [{"account": "Checking", "period_start": "2026-01-01", "period_end": "2026-01-31",
             "opening_balance": "0", "closing_balance": "5000", "balance_status": "verified"},
            {"account": "Checking", "period_start": "2026-02-01", "period_end": "2026-02-28",
             "opening_balance": "5000", "closing_balance": "7000", "balance_status": "verified"}]
    assert C.check(good)["complete"] is True
    # break: Feb opens at 9999, not Jan's 5000 close
    bad = [dict(good[0]), {**good[1], "opening_balance": "9999"}]
    res = C.check(bad)
    assert res["complete"] is False and res["accounts"][0]["breaks"]
    # gap: Jan then April (missing Feb/Mar)
    gap = [good[0], {**good[1], "period_start": "2026-04-01", "period_end": "2026-04-30",
                     "opening_balance": "5000"}]
    assert C.check(gap)["complete"] is False
    print("  ✓ continuity: clean chain complete; balance break + period gap both caught")


def test_reconstruct_orchestrator():
    _fresh()
    import importlib
    import reconstruct as R
    importlib.reload(R)
    d = tempfile.mkdtemp(prefix="glaw-rsrc-")
    Path(d, "checking.csv").write_text(
        "Date,Description,Amount\n2026-01-05,JOB REVENUE,10000\n2026-01-10,XFER TO SAVINGS,-3000\n2026-01-20,MATERIALS,-2000\n")
    Path(d, "savings.csv").write_text("Date,Description,Amount\n2026-01-11,XFER FROM CHECKING,3000\n")
    coa = Path(d, "coa.json"); coa.write_text(
        '{"default":"Expenses:Uncategorized","rules":[{"pattern":"JOB REVENUE","account":"Income:JobRevenue"},'
        '{"pattern":"MATERIALS","account":"Expenses:Materials"},{"pattern":"XFER TO","account":"Expenses:Transfers"},'
        '{"pattern":"XFER FROM","account":"Income:Transfers"}]}')
    manifest = {"book": "acme", "entity": "Acme LLC", "window": 5, "sources": [
        {"path": str(Path(d, "checking.csv")), "account": "Assets:Bank:Checking", "map": str(coa),
         "opening": "0", "closing": "5000"},
        {"path": str(Path(d, "savings.csv")), "account": "Assets:Bank:Savings", "map": str(coa),
         "opening": "0", "closing": "3000"}]}
    res = R.reconstruct(manifest)
    assert res["audit_ready"] is True, res
    assert res["transfers"]["reclassified"] == 1
    assert res["tie_out"]["all_tied"] is True
    assert res["continuity"]["complete"] is True
    print("  ✓ reconstruct: 2 accounts → continuity ✓ + transfer netted + tie-out ✓ + gate ✓ = AUDIT-READY")


def main() -> int:
    test_transfer_reclassification()
    test_transfer_false_positive_guard()
    test_continuity()
    test_reconstruct_orchestrator()
    print("OK: multi-account reconstruction smoke passed (transfers + continuity + orchestrator)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
