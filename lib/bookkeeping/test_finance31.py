#!/usr/bin/env python3
"""PR10 — sales & use tax: economic nexus + tax due + GL reconciliation. Temp GLAW_HOME."""
from __future__ import annotations
import os, sys, tempfile
from decimal import Decimal
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def test_nexus_and_tax():
    import sales_use_tax as ST
    states = [{"state": "CA", "sales": 150000, "transactions": 500, "rate": 7.25},
              {"state": "TX", "sales": 50000, "transactions": 250, "rate": 6.25},
              {"state": "FL", "sales": 40000, "transactions": 50, "rate": 6.0}]
    d = ST.nexus_and_tax(states)
    assert d["states"][0]["nexus"] and d["states"][0]["reason"] == "sales≥threshold" and d["states"][0]["tax_due"] == "10875.00"
    assert d["states"][1]["nexus"] and d["states"][1]["reason"] == "transactions≥threshold" and d["states"][1]["tax_due"] == "3125.00"
    assert not d["states"][2]["nexus"] and d["states"][2]["tax_due"] == "0.00"
    assert d["total_tax_due"] == "14000.00"
    print("  ✓ sales/use: CA sales-nexus 10,875, TX txn-nexus 3,125, FL no-nexus 0, total 14,000")


def test_txn_test_disabled():
    import sales_use_tax as ST
    # a state that dropped the transaction test: 250 txns but only 50k sales → no nexus
    d = ST.nexus_and_tax([{"state": "XX", "sales": 50000, "transactions": 250, "rate": 5, "txn_nexus": False}])
    assert not d["states"][0]["nexus"]
    print("  ✓ sales/use: honors states that dropped the 200-transaction test")


def test_gl_reconciliation():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-sut-")
    import importlib, ledger as L, sales_use_tax as ST
    importlib.reload(L); importlib.reload(ST)
    L.Ledger("co").post({"date": "2026-01-01", "lines": [{"account": "Assets:Bank:Checking", "debit": 14000},
                                                        {"account": "Liabilities:Sales Tax Payable", "credit": 14000}]})
    r = ST.reconcile("co", "14000.00")
    assert r["ties_out"] and r["posted_sales_tax_payable"] == "14000.00"
    bad = ST.reconcile("co", "14500.00")
    assert not bad["ties_out"] and bad["difference"] == "500.00"
    print("  ✓ sales/use: computed tax reconciles to the posted Sales Tax Payable (catches a gap)")


def main() -> int:
    test_nexus_and_tax(); test_txn_test_disabled(); test_gl_reconciliation()
    print("OK: sales & use tax (PR10) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
