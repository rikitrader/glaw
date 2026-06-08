#!/usr/bin/env python3
"""Smoke test for the GLAW finance tools: statements, books_doctor, bank_rec.

Deterministic, no network. Verifies the accounting identities that make the books
bulletproof:  debits == credits,  Assets == Liabilities + Equity + Net Income,
cash flow nets to the cash change, the control gate fails an out-of-balance set,
and reconciliation surfaces book-only / bank-only items.
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import statements as S          # noqa: E402
import books_doctor as BD       # noqa: E402
import bank_rec as BR           # noqa: E402


def _rows(triples):
    # triples: (date, description, amount, category)
    return [{"booking_date": d, "description": desc, "normalized_description": desc.upper(),
             "amount": str(amt), "currency": "USD", "category": cat,
             "transaction_hash": f"{d}-{amt}-{i}", "source_method": "deterministic"}
            for i, (d, desc, amt, cat) in enumerate(triples)]


def test_statements():
    rows = _rows([
        ("2026-01-04", "LP CAPITAL CALL", "500000.00", "Equity:LP:Contributions"),
        ("2026-01-15", "ROOFCO ACQUISITION", "-150000.00", "Assets:Investments:Portfolio"),
        ("2026-01-22", "LEGAL FEES", "-8400.00", "Expenses:Professional:Legal"),
        ("2026-01-28", "CONSULTING REVENUE", "42000.00", "Income:Consulting"),
    ])
    s = S.build(rows)
    assert s["trial_balance"]["balanced"], "trial balance must balance (debits==credits)"
    assert s["balance_sheet"]["balances"], "Assets must == Liabilities + Equity + NI"
    # net income = 42,000 revenue - 8,400 expense = 33,600
    assert s["profit_loss"]["net_income"] == Decimal("33600.00"), s["profit_loss"]["net_income"]
    # cash flow nets to the ending bank balance (500000-150000-8400+42000 = 383,600)
    assert s["cash_flow"]["net_change_in_cash"] == Decimal("383600.00"), s["cash_flow"]
    # classification: bank = assets, no unclassified
    assert not s["unclassified_accounts"], s["unclassified_accounts"]
    # CF by activity ties: op + inv + fin == net change
    cf = s["cash_flow"]
    assert cf["operating"] + cf["investing"] + cf["financing"] == cf["net_change_in_cash"]
    print("  ✓ statements: TB balanced, BS balances, NI=33,600, CF ties")


def test_books_doctor_pass_and_fail():
    good = {"rows": _rows([
        ("2026-01-04", "CAPITAL CALL", "500000.00", "Equity:LP:Contributions"),
        ("2026-01-22", "LEGAL FEES", "-8400.00", "Expenses:Professional:Legal"),
    ]), "audit": [{"source": "x", "balance_status": "verified"}]}
    BD.FAIL = 0; BD.WARN = 0
    assert BD.run(good) == 0, "clean books must be BULLETPROOF (exit 0)"

    # discrepancy in the Golden Rule must fail the gate
    bad = dict(good); bad = {"rows": good["rows"],
                             "audit": [{"source": "x", "balance_status": "discrepancy"}]}
    BD.FAIL = 0; BD.WARN = 0
    assert BD.run(bad) == 1, "a balance discrepancy must FAIL the gate (exit 1)"

    # a bare-bucket category nests under Expenses: (still classified) → gate still passes
    bare = {"rows": _rows([("2026-01-04", "MYSTERY", "100.00", "Widgets:Blue")]),
            "audit": [{"source": "x", "balance_status": "verified"}]}
    assert S._resolve_contra("Widgets:Blue") == "Expenses:Widgets:Blue"
    BD.FAIL = 0; BD.WARN = 0
    assert BD.run(bare) == 0, "bare bucket nests under Expenses, books stay classified"
    print("  ✓ books-doctor: passes clean books, fails discrepancy, classifies bare buckets")


def test_bank_rec():
    books = _rows([
        ("2026-01-04", "CAPITAL CALL", "500000.00", "Equity"),
        ("2026-01-22", "LEGAL", "-8400.00", "Expenses:Legal"),
        ("2026-01-30", "CHECK 1042", "-1000.00", "Expenses:Vendor"),   # outstanding
    ])
    bank = _rows([
        ("2026-01-05", "CAPITAL CALL WIRE", "500000.00", None),         # cleared +1 day
        ("2026-01-22", "LEGAL", "-8400.00", None),
        ("2026-01-31", "SERVICE FEE", "-25.00", None),                  # bank-only
    ])
    rc = BR.reconcile(books, bank, window_days=5)
    assert rc["matched"] == 2, rc["matched"]
    assert len(rc["book_only"]) == 1 and rc["book_only"][0]["description"] == "CHECK 1042"
    assert len(rc["bank_only"]) == 1 and rc["bank_only"][0]["description"] == "SERVICE FEE"
    assert rc["unreconciled_difference"] == Decimal("-975.00"), rc["unreconciled_difference"]
    assert rc["reconciled"] is False
    # identical sets reconcile to zero
    rc2 = BR.reconcile(books, books, window_days=0)
    assert rc2["unreconciled_difference"] == 0 and not rc2["book_only"] and not rc2["bank_only"]
    print("  ✓ bank-rec: matches cleared items, surfaces book-only + bank-only, diff=-975")


def main() -> int:
    test_statements()
    test_books_doctor_pass_and_fail()
    test_bank_rec()
    print("OK: finance tools smoke passed (statements + books-doctor + bank-rec)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
