#!/usr/bin/env python3
"""Smoke test for the Phase 2/3 finance tools: depreciate, aging, cashflow13,
budget, monitor. Deterministic, no network."""
from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import depreciate as DEP   # noqa: E402
import aging as AG         # noqa: E402
import cashflow13 as CF    # noqa: E402
import budget as BUD       # noqa: E402
import monitor as MON      # noqa: E402


def _rows(triples):
    return [{"booking_date": d, "description": desc, "normalized_description": desc.upper(),
             "counterparty": desc.upper(), "amount": str(amt), "currency": "USD",
             "category": cat, "transaction_hash": f"{d}-{amt}-{i}"}
            for i, (d, desc, amt, cat) in enumerate(triples)]


def test_depreciate():
    # MACRS tables self-check ran at import; verify 5-year matches IRS Pub 946 exactly
    d = DEP.schedule(Decimal("50000"), method="macrs", life_years=5)
    deps = [r["depreciation"] for r in d["schedule"]]
    assert deps == [Decimal(x) for x in ["10000.00", "16000.00", "9600.00", "5760.00",
                                         "5760.00", "2880.00"]], deps
    assert d["total_depreciated"] == Decimal("50000.00")
    # §179 25k + 60% bonus on 100k → basis 30k, total fully depreciated
    d2 = DEP.schedule(Decimal("100000"), method="macrs", life_years=7,
                      section_179=Decimal("25000"), bonus_pct=Decimal("60"))
    assert d2["section_179"] == Decimal("25000.00") and d2["bonus"] == Decimal("45000.00")
    assert d2["depreciable_basis"] == Decimal("30000.00")
    assert d2["total_depreciated"] == Decimal("100000.00")
    # straight-line trues up
    sl = DEP.schedule(Decimal("12000"), method="straight-line", life_years=5, salvage=Decimal("2000"))
    assert sl["total_depreciated"] == Decimal("10000.00"), sl["total_depreciated"]
    print("  ✓ depreciate: MACRS 5-yr = IRS table, §179+bonus, straight-line true-up")


def test_aging():
    items = [{"party": "ABC", "amount": 7800, "date": "2026-01-05"},
             {"party": "ABC", "amount": 4200, "date": "2025-11-10"},
             {"party": "Beacon", "amount": 3000, "date": "2025-10-01"}]
    a = AG.age(items, date(2026, 2, 1))
    assert a["by_bucket"]["Current (0-30)"] == Decimal("7800")
    assert a["by_bucket"]["61-90"] == Decimal("4200")
    assert a["by_bucket"]["90+"] == Decimal("3000")
    assert a["total"] == Decimal("15000") and a["overdue"] == Decimal("7200")
    print("  ✓ aging: buckets + overdue correct")


def test_cashflow():
    p = CF.project(Decimal("20000"), [{"week": 1, "amount": -30000}, {"week": 2, "amount": 40000}],
                   minimum=Decimal("5000"))
    assert p["rows"][0]["ending_cash"] == Decimal("-10000")
    assert p["trough"] == Decimal("-10000") and p["breach_weeks"] == [1] and not p["solvent"]
    print("  ✓ cashflow-13w: running balance, trough, breach week")


def test_budget():
    rows = _rows([("2026-01-28", "REVENUE", "42000.00", "Income:Consulting"),
                  ("2026-01-22", "LEGAL", "-8400.00", "Expenses:Legal")])
    v = BUD.variance({"Income:Consulting": 50000, "Expenses:Legal": 5000}, rows,
                     threshold_pct=Decimal("10"))
    assert v["breaches"] == 2 and not v["on_budget"]
    legal = next(l for l in v["lines"] if l["account"] == "Expenses:Legal")
    assert legal["variance"] == Decimal("3400") and legal["breach"]
    print("  ✓ budget: income shortfall + expense overrun both breach")


def test_monitor():
    rows = _rows([("2026-01-05", "ACME", "-5000.00", "Expenses:X"),
                  ("2026-01-19", "ACME", "-5000.00", "Expenses:X"),     # dup payment
                  ("2026-01-10", "WKND", "-1234.00", "Expenses:X"),     # Saturday
                  ("2026-01-15", "BIGCO", "-25000.00", "Expenses:X")])  # lone large
    s = MON.scan(rows)
    reasons = {f["reason"] for f in s["flags"]}
    assert "duplicate-payment" in reasons
    assert "weekend-entry" in reasons
    assert "lone-large-payment" in reasons
    assert "round-dollar" in reasons
    assert not s["clean"]
    print("  ✓ monitor: flags duplicate / weekend / lone-large / round-dollar")


def main() -> int:
    test_depreciate()
    test_aging()
    test_cashflow()
    test_budget()
    test_monitor()
    print("OK: phase 2/3 finance tools smoke passed (depreciate + aging + cashflow + budget + monitor)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
