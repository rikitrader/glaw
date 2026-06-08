#!/usr/bin/env python3
"""Smoke test for tagged COA + indirect cash flow + tag-aware dashboard.
Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import coa_tags as T          # noqa: E402
import statements as S        # noqa: E402


def test_classify():
    ov = T.load_chart_tags("roofing")
    assert ov, "roofing tags must load"
    assert T.classify("Assets:AR", ov) == {"type": "asset", "current": True, "cashflow": "operating"}
    assert T.classify("Assets:Vehicles", ov)["cashflow"] == "investing"
    assert T.classify("Assets:Vehicles", ov)["current"] is False
    assert T.classify("Liabilities:Loan", ov)["cashflow"] == "financing"
    assert T.classify("Assets:Accumulated Depreciation", ov)["cashflow"] == "operating"
    # defaults (no chart) still classify sensibly
    assert T.classify("Assets:Bank:Checking")["cashflow"] == "cash"
    assert T.classify("Liabilities:AP")["current"] is True
    assert T.classify("Liabilities:Loan Payable")["cashflow"] == "financing"
    print("  ✓ coa-tags: roofing overrides + keyword defaults classify type/current/cashflow")


def test_indirect_cash_flow_reconciles():
    # opening: cash 0; closing reflects: NI 59k, ΔAR +30k (uses cash), depr +1k, buy truck 35k, loan +40k
    classify = lambda a: T.classify(a, T.load_chart_tags("roofing"))   # noqa: E731
    opening = {}
    closing = {
        "Assets:Bank:Checking": Decimal("35000"),         # net cash change
        "Assets:AR": Decimal("30000"),
        "Assets:Vehicles": Decimal("35000"),
        "Assets:Accumulated Depreciation": Decimal("-1000"),
        "Liabilities:Loan": Decimal("-40000"),
        "Income:JobRevenue": Decimal("-80000"),
        "Expenses:Materials": Decimal("20000"),
        "Expenses:Depreciation": Decimal("1000"),
    }
    cf = S.cash_flow_indirect(opening, closing, classify)
    assert cf["net_income"] == Decimal("59000")           # 80k - 20k - 1k
    assert cf["operating"] == Decimal("30000")            # 59k - 30k AR + 1k depr
    assert cf["investing_total"] == Decimal("-35000")
    assert cf["financing_total"] == Decimal("40000")
    assert cf["net_change_in_cash"] == Decimal("35000")
    assert cf["change_in_cash"] == Decimal("35000")
    assert cf["reconciles"] is True
    print("  ✓ indirect cash flow: CFO 30k − CFI 35k + CFF 40k = Δcash 35k, reconciles")


def test_dashboard_tagged():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-tag-")
    import importlib
    import ledger as L
    importlib.reload(L)
    import dashboard as D
    importlib.reload(D)
    L.Ledger("r").post({"date": "2026-06-30", "lines": [
        {"account": "Assets:Bank:Checking", "debit": 50000},
        {"account": "Assets:AR", "debit": 20000},
        {"account": "Assets:Vehicles", "debit": 35000},   # NON-current under tags
        {"account": "Income:JobRevenue", "credit": 95000},
        {"account": "Liabilities:AP", "credit": 10000}]})
    # heuristic would miss nothing here, but tags must EXCLUDE the truck from current assets
    tagged = D.compute("r", chart="roofing")["kpis"]
    # current assets = bank 50k + AR 20k = 70k (truck excluded) / AP 10k = 7.0
    assert tagged["current_ratio"] == Decimal("7.00"), tagged["current_ratio"]
    print("  ✓ dashboard: chart tags give exact current ratio (fixed assets excluded)")


def main() -> int:
    test_classify()
    test_indirect_cash_flow_reconciles()
    test_dashboard_tagged()
    print("OK: tagged COA + indirect cash flow smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
