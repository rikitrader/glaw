#!/usr/bin/env python3
"""Smoke test for multi-entity NCI + equity-method consolidation. Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _fresh():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-nci-")
    import importlib
    import ledger as L
    importlib.reload(L)
    import consolidate as CON
    importlib.reload(CON)
    return L, CON


def test_nci_full_consolidation():
    L, CON = _fresh()
    L.Ledger("parent").post({"date": "2026-01-01", "lines": [
        {"account": "Assets:Bank:Checking", "debit": 50000}, {"account": "Equity:Capital", "credit": 50000}]})
    sub = L.Ledger("sub")
    sub.post({"date": "2026-01-01", "lines": [
        {"account": "Assets:Bank:Checking", "debit": 10000}, {"account": "Equity:Capital", "credit": 10000}]})
    sub.post({"date": "2026-06-01", "lines": [
        {"account": "Assets:Bank:Checking", "debit": 5000}, {"account": "Income:Sales", "credit": 5000}]})
    # parent owns 80% → 20% of the sub's net equity (10k capital + 5k NI = 15k) = 3,000 NCI
    d = CON.consolidate(["parent", "sub"], None, ownership={"sub": Decimal("0.8")})
    assert d["trial_balance_balanced"] and d["balance_sheet_balances"]
    assert len(d["nci"]) == 1 and Decimal(d["nci"][0]["nci_share"]) == Decimal("3000.00")
    cb = {a: Decimal(v) for a, v in d["consolidated_balances"].items()}
    assert cb["Equity:Non-Controlling Interest"] == Decimal("-3000.00")   # credit-normal NCI line
    # total assets unchanged (full consolidation); equity just split into controlling + NCI
    assert cb["Assets:Bank:Checking"] == Decimal("65000")
    # wholly-owned needs no NCI
    d2 = CON.consolidate(["parent", "sub"], None, ownership={"sub": Decimal("1.0")})
    assert not d2["nci"]
    print("  ✓ NCI: 80%-owned sub → 20% NCI 3,000 on its own equity line; TB/BS balance; 100% → no NCI")


def test_equity_method_rollforward():
    _fresh()
    import consolidate as CON
    # 30% investee: cost 100k, cumulative NI 40k, dividends 10k → 100k + 12k − 3k = 109k
    d = CON.equity_method(Decimal("100000"), Decimal("0.30"), Decimal("40000"), Decimal("10000"))
    assert d["equity_method_income"] == Decimal("12000.00")
    assert d["dividends_received"] == Decimal("3000.00")
    assert d["ending_investment"] == Decimal("109000.00")
    assert d["suspended_losses"] == Decimal("0.00")
    # both entries balance
    for e in d["entries"]:
        dr = sum(Decimal(l["debit"]) for l in e["lines"]); cr = sum(Decimal(l["credit"]) for l in e["lines"])
        assert dr == cr
    # ASC 323: a loss cannot take the investment below zero — it floors at 0 and suspends the excess
    loss = CON.equity_method(Decimal("100000"), Decimal("0.30"), Decimal("-500000"), Decimal("0"))
    assert loss["ending_investment"] == Decimal("0.00")
    assert loss["suspended_losses"] == Decimal("50000.00")
    assert loss["equity_method_income"] == Decimal("-100000.00")   # recognized only to a zero balance
    assert any("Loss" in l["account"] for l in loss["entries"][0]["lines"])
    print("  ✓ equity-method: 109k investment; a big loss floors at 0 + suspends 50k (ASC 323)")


def main() -> int:
    test_nci_full_consolidation()
    test_equity_method_rollforward()
    print("OK: multi-entity NCI + equity-method smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
