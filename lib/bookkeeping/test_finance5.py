#!/usr/bin/env python3
"""Smoke test for the Tier 2/3 calculation tools: revrec, fx_reval, inventory,
tax_provision, consolidate, cash_apply, recurring. Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import revrec as RR          # noqa: E402
import fx_reval as FX        # noqa: E402
import inventory as INV      # noqa: E402
import tax_provision as TP   # noqa: E402
import cash_apply as CA      # noqa: E402
import recurring as REC      # noqa: E402


def _je_balances(lines) -> bool:
    d = sum(Decimal(str(l.get("debit", 0))) for l in lines)
    c = sum(Decimal(str(l.get("credit", 0))) for l in lines)
    return d == c


def test_revrec():
    d = RR.schedule(Decimal("12000"), method="ratable", periods=12)
    assert d["total_recognized"] == Decimal("12000.00") and d["ending_deferred"] == Decimal("0.00")
    assert all(_je_balances(r["entry"]) for r in d["schedule"])
    m = RR.schedule(Decimal("100000"), method="milestone", pcts=[Decimal("30"), Decimal("40"), Decimal("30")])
    assert m["total_recognized"] == Decimal("100000.00")
    print("  ✓ revrec: ratable + milestone fully recognize, every entry balances")


def test_fx():
    # ASSET: EUR 100,000 AR booked @1.05, closing @1.10 → +5,000 GAIN (worth more)
    d = FX.revalue([{"account": "Assets:AR:EUR", "currency": "EUR", "foreign_amount": 100000,
                     "booked_rate": "1.05", "closing_rate": "1.10", "monetary": True}])
    assert d["net_fx_gain"] == Decimal("5000.00") and d["result"] == "gain"
    assert _je_balances(d["entry"])
    # LIABILITY: same EUR move on a loan → −5,000 LOSS (you owe more), and the liability is CREDITED
    liab = FX.revalue([{"account": "Liabilities:EUR Loan", "currency": "EUR", "foreign_amount": 100000,
                        "booked_rate": "1.05", "closing_rate": "1.10", "monetary": True}])
    assert liab["net_fx_gain"] == Decimal("-5000.00") and liab["result"] == "loss", liab["net_fx_gain"]
    assert _je_balances(liab["entry"])
    liab_line = next(l for l in liab["entry"] if l["account"] == "Liabilities:EUR Loan")
    assert Decimal(liab_line["credit"]) == Decimal("5000.00")   # liability grows (credit)
    print("  ✓ fx-reval: asset rate-up = +5k gain; liability rate-up = −5k loss (liability credited)")


def test_inventory():
    d = INV.cogs("fifo", [{"units": 100, "unit_cost": 5}, {"units": 50, "unit_cost": 7}], Decimal("120"))
    assert d["cogs"] == Decimal("640.00") and d["ending_inventory"] == Decimal("210.00")
    assert d["cogs"] + d["ending_inventory"] == d["total_cost"]   # conservation
    w = INV.cogs("wac", [{"units": 100, "unit_cost": 5}, {"units": 100, "unit_cost": 7}], Decimal("100"))
    assert w["cogs"] == Decimal("600.00")                        # avg 6.00 × 100
    print("  ✓ inventory: FIFO COGS 640 (conserves), WAC avg-cost 600")


def test_tax_provision():
    d = TP.provision(Decimal("100000"), Decimal("10000"), Decimal("20000"), Decimal("21"))
    assert d["taxable_income"] == Decimal("90000.00")
    assert d["current_tax"] == Decimal("18900.00")
    assert d["deferred_tax"] == Decimal("4200.00") and d["deferred_tax_type"] == "liability"
    assert d["total_provision"] == Decimal("23100.00")
    assert d["effective_rate_pct"] == Decimal("23.10")
    # ETR reconciliation: statutory + permanent effect == total provision
    assert d["statutory_tax"] + d["permanent_tax_effect"] == d["total_provision"]
    assert _je_balances(d["entry"])
    print("  ✓ tax-provision: current 18,900 + deferred 4,200 = 23,100; ETR 23.10% reconciles")


def test_consolidate():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-cons-")
    import importlib
    import ledger as L
    importlib.reload(L)
    import consolidate as CON
    importlib.reload(CON)
    # parent has IC receivable; sub has IC payable — eliminate them
    L.Ledger("parent").post({"date": "2026-01-31", "lines": [
        {"account": "Assets:IC Receivable", "debit": 50000}, {"account": "Income:IC Sales", "credit": 50000}]})
    L.Ledger("sub").post({"date": "2026-01-31", "lines": [
        {"account": "Expenses:IC COGS", "debit": 50000}, {"account": "Liabilities:IC Payable", "credit": 50000}]})
    elim = [{"memo": "eliminate IC", "lines": [
        {"account": "Income:IC Sales", "debit": 50000}, {"account": "Expenses:IC COGS", "credit": 50000},
        {"account": "Liabilities:IC Payable", "debit": 50000}, {"account": "Assets:IC Receivable", "credit": 50000}]}]
    d = CON.consolidate(["parent", "sub"], elim)
    assert d["trial_balance_balanced"]
    # after elimination all four IC accounts net to zero
    cb = {a: Decimal(v) for a, v in d["consolidated_balances"].items()}
    assert cb.get("Assets:IC Receivable", Decimal("0")) == 0
    assert cb.get("Income:IC Sales", Decimal("0")) == 0
    print("  ✓ consolidate: two books combined, intercompany eliminated to 0, TB balances")


def test_cash_apply():
    d = CA.apply_cash(
        [{"id": "INV-1", "party": "Acme", "amount": 1000, "date": "2026-01-05"},
         {"id": "INV-2", "party": "Acme", "amount": 500, "date": "2026-01-20"}],
        [{"party": "Acme", "amount": 1200, "date": "2026-02-01"}])   # pays INV-1 full + 200 of INV-2
    paid = {i["id"]: i for i in d["open_items"]}
    assert paid["INV-1"]["status"] == "paid"
    assert paid["INV-2"]["status"] == "partial" and Decimal(paid["INV-2"]["remaining"]) == Decimal("300")
    assert Decimal(d["total_still_open"]) == Decimal("300")
    print("  ✓ cash-apply: receipt 1,200 clears INV-1, partials INV-2 (300 left)")


def test_recurring():
    e = REC.build_entries([{"name": "rent accrual", "lines": [
        {"account": "Expenses:Rent", "debit": 5000}, {"account": "Liabilities:Accrued Rent", "credit": 5000}]}],
        "2026-01-31")
    assert len(e) == 1 and _je_balances(e[0]["lines"])
    try:
        REC.build_entries([{"name": "bad", "lines": [{"account": "X", "debit": 100}, {"account": "Y", "credit": 90}]}], "2026-01-31")
        raise AssertionError("unbalanced template must be rejected")
    except SystemExit:
        pass
    print("  ✓ recurring: balanced template stamps to a JE, unbalanced rejected")


def test_zero_input_guards():
    import amortize as A, depreciate as DEP
    # invalid periods/payments/life must error gracefully (SystemExit), not crash (ZeroDivisionError)
    for fn in (lambda: RR.ratable(Decimal("100"), 0),
               lambda: A.loan_schedule(Decimal("100"), Decimal("5"), 0),
               lambda: A.prepaid_schedule(Decimal("100"), 0),
               lambda: DEP.straight_line(Decimal("100"), Decimal("0"), 0)):
        try:
            fn(); raise AssertionError("expected a graceful SystemExit for zero periods/life")
        except SystemExit:
            pass
        except ZeroDivisionError:
            raise AssertionError("zero input crashed with ZeroDivisionError instead of a clear error")
    print("  ✓ guards: zero periods/payments/life error gracefully (no ZeroDivisionError)")


def main() -> int:
    test_revrec(); test_fx(); test_inventory(); test_tax_provision()
    test_consolidate(); test_cash_apply(); test_recurring(); test_zero_input_guards()
    print("OK: Tier 2/3 calc tools passed (revrec, fx, inventory, tax-provision, "
          "consolidate, cash-apply, recurring)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
