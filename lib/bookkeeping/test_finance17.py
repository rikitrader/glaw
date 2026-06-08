#!/usr/bin/env python3
"""Smoke test for true multi-currency conversion with realized FX (glaw-fx-convert).
Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import fx_convert as FX   # noqa: E402


def _balances(lines_entry):
    dr = sum(Decimal(l["debit"]) for l in lines_entry["lines"])
    cr = sum(Decimal(l["credit"]) for l in lines_entry["lines"])
    return dr, cr


def test_realized_gain():
    # EUR 100,000 carried @1.05 (USD 105k) converted @1.10 (USD 110k) → +5,000 realized gain
    d = FX.convert(from_account="Assets:Bank:EUR", from_amount=Decimal("100000"),
                   from_currency="EUR", carrying_rate=Decimal("1.05"),
                   to_account="Assets:Bank:USD", conversion_rate=Decimal("1.10"))
    assert d["carrying_value"] == Decimal("105000.00")
    assert d["proceeds"] == Decimal("110000.00")
    assert d["realized_fx"] == Decimal("5000.00") and d["result"] == "gain"
    dr, cr = _balances(d["entry"])
    assert dr == cr == Decimal("110000.00"), (dr, cr)              # balances in reporting
    eur = next(l for l in d["entry"]["lines"] if l["account"] == "Assets:Bank:EUR")
    assert eur["fx_amount"] == "100000.00" and Decimal(eur["credit"]) == Decimal("105000.00")
    print("  ✓ fx-convert: gain — carry 105k, proceeds 110k, realized +5k; entry balances in reporting")


def test_realized_loss():
    # convert @1.02 (below the 1.05 carrying rate) → loss
    d = FX.convert(from_account="Assets:Bank:EUR", from_amount=Decimal("100000"),
                   from_currency="EUR", carrying_rate=Decimal("1.05"),
                   to_account="Assets:Bank:USD", conversion_rate=Decimal("1.02"))
    assert d["realized_fx"] == Decimal("-3000.00") and d["result"] == "loss"
    assert any(l["account"] == "Expenses:Realized FX Loss" and Decimal(l["debit"]) == Decimal("3000.00")
               for l in d["entry"]["lines"])
    dr, cr = _balances(d["entry"])
    assert dr == cr == Decimal("105000.00")                       # balances in reporting
    print("  ✓ fx-convert: loss — convert @1.02 below carry 1.05 → −3k realized loss; entry balances")


def test_posts_and_tracks_per_currency():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-fxc-")
    import importlib
    import ledger as L
    importlib.reload(L)
    import multicurrency as MC
    importlib.reload(MC)
    d = FX.convert(from_account="Assets:Bank:EUR", from_amount=Decimal("100000"),
                   from_currency="EUR", carrying_rate=Decimal("1.05"),
                   to_account="Assets:Bank:USD", conversion_rate=Decimal("1.10"), date="2026-03-15")
    L.Ledger("co").post(d["entry"])
    bal = L.Ledger("co").balances()
    assert bal["Income:Realized FX Gain"] == Decimal("-5000")     # reporting (credit-normal gain)
    assert bal["Assets:Bank:EUR"] == Decimal("-105000")           # reporting carrying value removed
    by = MC.balances_by_currency("co")
    assert by["EUR"]["Assets:Bank:EUR"] == Decimal("-100000")     # FOREIGN amount tracked via fx_amount
    assert by["USD"]["Assets:Bank:USD"] == Decimal("110000")
    print("  ✓ fx-convert: posts a balanced entry; reporting removes carrying, per-currency tracks EUR")


def main() -> int:
    test_realized_gain()
    test_realized_loss()
    test_posts_and_tracks_per_currency()
    print("OK: true multi-currency conversion (realized FX) smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
