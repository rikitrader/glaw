#!/usr/bin/env python3
"""Smoke test for the multi-currency GL (per-currency balances + current-rate translation).
Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _fresh():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-mc-")
    import importlib
    import ledger as L
    importlib.reload(L)
    import multicurrency as MC
    importlib.reload(MC)
    return L, MC


def test_per_currency_and_translation():
    L, MC = _fresh()
    led = L.Ledger("g")
    led.post({"date": "2026-01-05", "currency": "USD",
              "lines": [{"account": "Assets:Bank:USD", "debit": 10000},
                        {"account": "Income:Sales", "credit": 10000}]})
    led.post({"date": "2026-01-10", "currency": "EUR",
              "lines": [{"account": "Assets:Bank:EUR", "debit": 5000},
                        {"account": "Income:Sales", "credit": 5000}]})
    by = MC.balances_by_currency("g")
    assert set(by) == {"USD", "EUR"}
    assert by["EUR"]["Assets:Bank:EUR"] == Decimal("5000")

    rates = {"EUR": {"closing": "1.10", "average": "1.08", "historical": "1.05"}}
    tr = MC.translate(by, rates, reporting="USD")
    # EUR bank at closing 1.10 = 5,500 ; EUR income at average 1.08 = 5,400
    assert tr["balances"]["Assets:Bank:EUR"] == Decimal("5500.00")
    assert tr["balances"]["Income:Sales"] == Decimal("-15400.00")    # -10000 USD + -5400 EUR
    # mixed rates → CTA plug of -100 makes it balance
    assert tr["cta"] == Decimal("-100.00")
    assert tr["balanced"] is True
    assert tr["rates_complete"] is True and tr["missing_rates"] == []
    assert sum(tr["balances"].values()) == 0
    # a MISSING rate must be flagged, never silently defaulted to 1.0
    bad = MC.translate(by, {}, reporting="USD")
    assert bad["rates_complete"] is False and bad["missing_rates"] == ["EUR"]
    print("  ✓ multi-currency: EUR bank@closing 5,500, CTA −100 balances; missing rate flagged (not silent)")


def test_report_statements_in_reporting_currency():
    L, MC = _fresh()
    led = L.Ledger("g")
    led.post({"date": "2026-01-05", "currency": "EUR",
              "lines": [{"account": "Assets:Bank:EUR", "debit": 1000},
                        {"account": "Income:Sales", "credit": 1000}]})
    r = MC.report("g", reporting="USD", rates={"EUR": {"closing": "1.10", "average": "1.10"}})
    assert r["trial_balance_balanced"], "translated single-currency statements must balance"
    assert r["currencies"] == ["EUR"]
    # single rate (closing==average) → no CTA
    assert Decimal(r["cta"]) == 0
    print("  ✓ multi-currency: report renders balanced single-currency statements (no CTA when one rate)")


def main() -> int:
    test_per_currency_and_translation()
    test_report_statements_in_reporting_currency()
    print("OK: multi-currency GL smoke passed (per-currency balances + current-rate translation + CTA)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
