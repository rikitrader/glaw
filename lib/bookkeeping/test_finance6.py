#!/usr/bin/env python3
"""Smoke test for the management dashboard KPI tool. Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def test_dashboard():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-dash-")
    import importlib
    import ledger as L
    importlib.reload(L)
    import dashboard as D
    importlib.reload(D)
    # sales 100k, COGS 40k, opex 30k → GP 60k (60%), NI 30k (30%); AR 20k, AP 10k, inv 15k, cash 50k
    L.Ledger("co").post({"date": "2026-06-30", "memo": "seed", "lines": [
        {"account": "Assets:Bank:Checking", "debit": 50000},
        {"account": "Assets:AR", "debit": 20000},
        {"account": "Assets:Inventory", "debit": 15000},
        {"account": "Expenses:COGS", "debit": 40000},
        {"account": "Expenses:Opex", "debit": 30000},
        {"account": "Income:Sales", "credit": 100000},
        {"account": "Liabilities:AP", "credit": 10000},
        {"account": "Equity:Contributions", "credit": 45000},
    ]})
    k = D.compute("co")["kpis"]
    assert k["gross_margin"] == Decimal("60.00"), k["gross_margin"]
    assert k["net_margin_pct"] == Decimal("30.00"), k["net_margin_pct"]
    assert k["current_ratio"] == Decimal("8.50"), k["current_ratio"]      # 85k / 10k
    assert k["quick_ratio"] == Decimal("7.00"), k["quick_ratio"]          # 70k / 10k
    assert k["working_capital"] == Decimal("75000.00")
    assert k["dso_days"] == Decimal("73.00"), k["dso_days"]               # 20k/100k*365
    assert k["dpo_days"] == Decimal("91.25"), k["dpo_days"]               # 10k/40k*365
    assert k["debt_to_equity"] == Decimal("0.13"), k["debt_to_equity"]    # 10k / 75k (equity incl NI)
    assert k["cash"] == Decimal("50000.00")
    print("  ✓ dashboard: GM 60% / NM 30% / current 8.5 / quick 7.0 / DSO 73 / DPO 91.25 / D:E 0.13")


def main() -> int:
    test_dashboard()
    print("OK: dashboard KPI smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
