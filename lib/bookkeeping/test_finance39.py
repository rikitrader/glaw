#!/usr/bin/env python3
"""W1 — IRS audit package: GL substantiation index + Form 4549 compare + IDR index. Temp GLAW_HOME."""
from __future__ import annotations
import os, sys, tempfile
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _book():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-audit-")
    import importlib, ledger as L
    importlib.reload(L)
    led = L.Ledger("co")
    led.post({"date": "2026-01-01", "lines": [{"account": "Assets:Bank:Checking", "debit": 100000},
                                              {"account": "Income:Sales", "credit": 100000}]})
    for date, acct, amt in [("2026-03-01", "Expenses:Meals", 8000), ("2026-04-01", "Expenses:Travel", 12000),
                            ("2026-05-01", "Expenses:Meals", 4000)]:
        led.post({"date": date, "lines": [{"account": acct, "debit": amt},
                                          {"account": "Assets:Bank:Checking", "credit": amt}]})
    return L


def test_substantiation_tied_to_gl():
    _book()
    import audit_package as AP
    import importlib
    importlib.reload(AP)
    s = AP.substantiation_index("co", ["Expenses:Meals", "Expenses:Travel"])
    assert s["Expenses:Meals"]["total_substantiated"] == "12000.00" and s["Expenses:Meals"]["count"] == 2
    assert s["Expenses:Travel"]["total_substantiated"] == "12000.00"
    # each supporting entry carries the tamper-evident hash → it ties to the books, not fabricated
    assert all(e["entry_hash"] for e in s["Expenses:Meals"]["supporting_entries"])
    print("  ✓ audit: substantiation index pulled from the GL, every entry tied by its hash")


def test_form4549_compare():
    import audit_package as AP
    f = AP.form4549_compare({"Taxable income": 100000}, {"Taxable income": 106000}, rate_pct="21")
    assert f["total_adjustment"] == "6000.00" and f["additional_tax"] == "1260.00"
    assert f["lines"][0]["disputed"]
    print("  ✓ audit: Form 4549 compare → adjustment 6,000, additional tax 1,260 @21%")


def test_idr_index():
    import audit_package as AP
    i = AP.idr_index([{"request": "Meals receipts", "status": "provided", "location": "Tab 3"},
                      {"request": "Mileage log", "status": "outstanding"}])
    assert i["provided"] == 1 and i["outstanding"] == 1
    print("  ✓ audit: IDR index tracks provided vs outstanding requests")


def main() -> int:
    test_substantiation_tied_to_gl(); test_form4549_compare(); test_idr_index()
    print("OK: IRS audit package (W1) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
