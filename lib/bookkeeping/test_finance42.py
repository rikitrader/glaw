#!/usr/bin/env python3
"""Forensic pipeline: classified CSV → GLAW double-entry GL, balanced + reconciled + idempotent."""
from __future__ import annotations
import csv, os, sys, tempfile
from decimal import Decimal
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _csv(path):
    rows = [
        {"acct": "1000", "stmt": "2024-01", "date": "01/05/24", "section": "DEPOSIT",
         "category": "REVENUE — ACH credit", "amount": "10000", "desc": "client pay", "file": "e1.pdf"},
        {"acct": "1000", "stmt": "2024-01", "date": "01/10/24", "section": "WITHDRAWAL",
         "category": "COGS — Materials", "amount": "-3000", "desc": "supplier", "file": "e1.pdf"},
        {"acct": "1000", "stmt": "2024-01", "date": "01/15/24", "section": "WITHDRAWAL",
         "category": "OpEx — Fuel/Auto", "amount": "-500", "desc": "gas", "file": "e1.pdf"},
        {"acct": "1000", "stmt": "2024-01", "date": "01/20/24", "section": "WITHDRAWAL",
         "category": "OWNER DRAW — Prieto", "amount": "-2000", "desc": "draw", "file": "e1.pdf"},
        {"acct": "1000", "stmt": "2024-01", "date": "01/25/24", "section": "WITHDRAWAL",
         "category": "WIRE/BOOK-OUT (purpose unstated — review)", "amount": "-1000", "desc": "wire", "file": "e1.pdf"},
    ]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


def test_reconstruct_balances_and_maps():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-fp-")
    import importlib, ledger as L, forensic_pipeline as FP
    importlib.reload(L); importlib.reload(FP)
    p = Path(os.environ["GLAW_HOME"]) / "m.csv"; _csv(p)
    d = FP.reconstruct(str(p), book="t")
    assert d["build"]["posted"] == 5 and len(d["build"]["errors"]) == 0
    assert d["trial_balance_balanced"] and d["chain_intact"]
    bal = d["balances"]
    assert bal["Income:Revenue"] == "-10000.00"                 # credit-normal income
    assert bal["Expenses:COGS:Materials"] == "3000.00"
    assert bal["Equity:Owner Draw"] == "2000.00"
    # the review category mapped to an explicit REVIEW account, not guessed
    assert any("REVIEW" in a for a in bal)
    assert not d["build"]["unmapped_categories"]
    print("  ✓ pipeline: 5 txns → balanced double-entry GL, chain intact, review-flagged, all mapped")


def test_idempotent_rerun():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-fp2-")
    import importlib, ledger as L, forensic_pipeline as FP
    importlib.reload(L); importlib.reload(FP)
    p = Path(os.environ["GLAW_HOME"]) / "m.csv"; _csv(p)
    d1 = FP.reconstruct(str(p), book="a")
    d2 = FP.reconstruct(str(p), book="b")                       # separate book, same input
    assert d1["balances"] == d2["balances"] and d1["net_income"] == d2["net_income"]
    print("  ✓ pipeline: re-runnable — identical input yields identical reconstruction")


def test_map_account():
    import forensic_pipeline as FP
    assert FP.map_account("REVENUE — other credit") == ("Income:Revenue", True)
    # financing wires default to revenue (payments for work) unless a loan lender matches
    assert FP.map_account("FINANCING/WIRE-IN (review)")[0].startswith("Income:Revenue:Construction")
    assert FP.map_account("something brand new") == ("Expenses:Uncategorized", False)
    print("  ✓ pipeline: category→CoA map faithful; unknown → Uncategorized (flagged), never guessed")


def test_loan_lender_override():
    """A wire naming a loan lender is booked to that lender's loan liability — inbound = proceeds
    (credit), outbound = repayment (debit) — not revenue/expense."""
    import os, tempfile, csv as _csv
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-loan-")
    import importlib, ledger as L, forensic_pipeline as FP
    importlib.reload(L); importlib.reload(FP)
    p = Path(os.environ["GLAW_HOME"]) / "m.csv"
    rows = [
        {"acct": "1", "stmt": "2024-01", "date": "01/08/24", "section": "DEPOSIT",
         "category": "FINANCING/WIRE-IN (review)", "amount": "100000",
         "desc": "WIRE IN FROM DEALYZE", "file": "e.pdf"},                 # loan proceeds
        {"acct": "1", "stmt": "2024-06", "date": "06/14/24", "section": "WITHDRAWAL",
         "category": "COGS — Materials", "amount": "-30000",
         "desc": "WIRE OUT TO DEALYZE", "file": "e.pdf"},                  # repayment (was mis-COGS)
        {"acct": "1", "stmt": "2024-02", "date": "02/01/24", "section": "DEPOSIT",
         "category": "FINANCING/WIRE-IN (review)", "amount": "5000",
         "desc": "wire from a customer", "file": "e.pdf"},                 # NOT a loan → revenue
    ]
    with open(p, "w", newline="") as fh:
        w = _csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    d = FP.reconstruct(str(p), book="t", loan_lenders=["DEALYZE"])
    assert d["build"]["loan_hits"] == 2                                    # the 2 Dealyze wires
    bal = L.Ledger("t").balances()
    assert bal.get("Liabilities:Loans-Payable:Dealyze") == Decimal("-70000")   # 100k proceeds − 30k repaid
    assert bal.get("Income:Revenue:Construction (wire — payments for work)") == Decimal("-5000")
    assert d["trial_balance_balanced"] and d["chain_intact"]
    print("  ✓ pipeline: Dealyze wires → loan liability (−70k net); non-lender wire stays revenue")


def main() -> int:
    test_reconstruct_balances_and_maps(); test_idempotent_rerun(); test_map_account(); test_loan_lender_override()
    print("OK: forensic reconstruction pipeline passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
