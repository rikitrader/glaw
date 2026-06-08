#!/usr/bin/env python3
"""PR D — income-tax return-line mapping: populate 1120/1120-S/1065/Sch C lines from the posted
GL + M-1, tying to the statements and the provision. Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _book():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-ret-")
    import importlib
    import ledger as L
    importlib.reload(L)
    led = L.Ledger("co")
    posts = [("Assets:Bank:Checking", 500000, "Income:Sales"),
             ("Expenses:COGS", 120000, "Assets:Bank:Checking"),
             ("Expenses:Salaries", 200000, "Assets:Bank:Checking"),
             ("Expenses:Meals", 20000, "Assets:Bank:Checking"),
             ("Expenses:Penalties", 5000, "Assets:Bank:Checking"),
             ("Expenses:Depreciation", 40000, "Assets:Accum-Deprec")]
    for dr, amt, cr in posts:
        led.post({"date": "2026-06-01", "lines": [{"account": dr, "debit": amt},
                                                  {"account": cr, "credit": amt}]})
    return L


def test_1120_lines_and_tie_out():
    L = _book()
    import return_map as RM
    import book_to_tax as BT
    import tax_provision as TP
    import importlib
    for m in (RM, BT, TP):
        importlib.reload(m)
    m1 = BT.book_to_tax("co", BT.load_rules("default"), tax_depreciation=Decimal("70000"))
    d = RM.map_return("co", "1120", m1=m1)
    line = {l["label"]: Decimal(l["amount"]) for l in d["lines"]}
    assert line["Gross profit"] == Decimal("380000")             # 500k − 120k COGS
    assert line["Salaries and wages"] == Decimal("200000")
    assert line["Depreciation"] == Decimal("40000")
    assert line["Other deductions"] == Decimal("25000")          # meals 20k + penalties 5k
    assert Decimal(d["book_pretax"]) == Decimal("115000")
    assert Decimal(d["taxable_income"]) == Decimal("100000")     # 115k + 15k perm − 30k temp
    # ties to the provision: same pretax + same taxable income off the same GL
    assert TP.pretax_from_ledger("co") == Decimal(d["book_pretax"])
    prov = TP.provision(TP.pretax_from_ledger("co"), m1["permanent"], m1["temporary"], Decimal("21"))
    assert prov["taxable_income"] == Decimal(d["taxable_income"])
    print("  ✓ return-map: 1120 lines off the GL; book 115k + M-1 → taxable 100k; ties to the provision")


def test_passthrough_label():
    L = _book()
    import return_map as RM
    import importlib
    importlib.reload(RM)
    d = RM.map_return("co", "1065")
    assert d["lines"][-1]["label"] == "Ordinary business income"   # 1065/1120-S final line label
    print("  ✓ return-map: 1065/1120-S final line labelled 'Ordinary business income'")


def main() -> int:
    test_1120_lines_and_tie_out()
    test_passthrough_label()
    print("OK: income-tax return-line mapping (PR D) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
