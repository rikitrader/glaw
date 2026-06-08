#!/usr/bin/env python3
"""PR2 — NOL carryforward engine + return-map wiring. Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import nol as NOL   # noqa: E402


def test_80pct_limit():
    d = NOL.apply_nol(100000, [{"year": 2024, "amount": 90000}])
    assert d["post_tcja_cap"] == "80000.00"
    assert d["nol_deduction"] == "80000.00" and d["taxable_income_after_nol"] == "20000.00"
    assert d["remaining_carryforward"][0]["amount"] == "10000.00"
    print("  ✓ NOL: post-TCJA NOL capped at 80% of taxable income, remainder carries forward")


def test_pre_tcja_uncapped():
    d = NOL.apply_nol(100000, [{"year": 2016, "amount": 90000, "pre_tcja": True}])
    assert d["nol_deduction"] == "90000.00" and d["taxable_income_after_nol"] == "10000.00"
    print("  ✓ NOL: pre-TCJA NOLs are not subject to the 80% cap")


def test_current_year_loss_carries():
    d = NOL.apply_nol(-50000, [], current_year=2026)
    assert d["nol_deduction"] == "0.00" and d["remaining_carryforward"][0]["amount"] == "50000.00"
    print("  ✓ NOL: a current-year loss becomes a carryforward (no deduction)")


def test_fifo_order():
    d = NOL.apply_nol(100000, [{"year": 2022, "amount": 30000}, {"year": 2023, "amount": 60000}])
    # cap 80k: use 2022's 30k fully, then 50k of 2023 → 2023 has 10k left
    used = {u["year"]: u["used"] for u in d["used"]}
    assert used[2022] == "30000.00" and used[2023] == "50000.00"
    assert d["remaining_carryforward"][0]["year"] == 2023 and d["remaining_carryforward"][0]["amount"] == "10000.00"
    print("  ✓ NOL: oldest losses used first (FIFO), within the 80% cap")


def test_wired_into_return_map():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-nol-")
    import importlib
    import ledger as L
    import return_map as RM
    importlib.reload(L); importlib.reload(RM)
    L.Ledger("co").post({"date": "2026-01-01", "lines": [{"account": "Assets:Bank:Checking", "debit": 100000},
                                                        {"account": "Income:Sales", "credit": 100000}]})
    d = RM.map_return("co", "1120", nol_carryforwards=[{"year": 2024, "amount": 90000}])
    assert Decimal(d["taxable_income_before_nol"]) == Decimal("100000")
    assert Decimal(d["nol_deduction"]) == Decimal("80000")
    assert Decimal(d["taxable_income"]) == Decimal("20000")
    print("  ✓ NOL: return-map applies it (line 29 NOL → line 30 taxable income after NOL)")


def main() -> int:
    test_80pct_limit()
    test_pre_tcja_uncapped()
    test_current_year_loss_carries()
    test_fifo_order()
    test_wired_into_return_map()
    print("OK: NOL carryforward engine (PR2) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
