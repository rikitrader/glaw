#!/usr/bin/env python3
"""PR A — ledger-wired tax provision: derive pretax book income from the posted GL and post the
provision JE back. Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _book():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-tax-")
    import importlib
    import ledger as L
    importlib.reload(L)
    led = L.Ledger("co")
    led.post({"date": "2026-01-01", "lines": [{"account": "Assets:Bank:Checking", "debit": 500000},
                                              {"account": "Income:Sales", "credit": 500000}]})
    led.post({"date": "2026-01-02", "lines": [{"account": "Expenses:Salaries", "debit": 200000},
                                              {"account": "Assets:Bank:Checking", "credit": 200000}]})
    return L, led


def test_pretax_from_ledger():
    L, led = _book()
    import tax_provision as TP
    import importlib
    importlib.reload(TP)
    assert TP.pretax_from_ledger("co") == Decimal("300000.00")   # 500k rev − 200k exp
    print("  ✓ tax: pretax book income derived from the posted GL (300,000)")


def test_post_provision_back():
    L, led = _book()
    import tax_provision as TP
    import statements as S
    import importlib
    importlib.reload(TP); importlib.reload(S)
    pretax = TP.pretax_from_ledger("co")
    d = TP.provision(pretax, Decimal("0"), Decimal("30000"), Decimal("21"))
    assert d["taxable_income"] == Decimal("270000.00")           # 300k − 30k temp
    assert d["current_tax"] == Decimal("56700.00") and d["deferred_tax"] == Decimal("6300.00")
    # post the JE back
    L.Ledger("co").post({"date": "2026-12-31", "source": "tax-provision",
                         "memo": "provision", "lines": d["entry"]})
    bal = L.Ledger("co").balances()
    assert bal["Liabilities:Income Tax Payable"] == Decimal("-56700")   # credit-normal
    assert bal["Liabilities:Deferred Tax"] == Decimal("-6300")
    st = S.build(postings=L.Ledger("co").postings())
    assert st["profit_loss"]["net_income"] == Decimal("237000")  # 300k − 63k total provision
    assert st["balance_sheet"]["balances"] and st["trial_balance"]["balanced"]
    # idempotency: pretax re-derives to 300k (the posted tax is added back)
    assert TP.pretax_from_ledger("co") == Decimal("300000.00")
    print("  ✓ tax: provision posted back — BS carries Payable+DTL, P&L after-tax, pretax idempotent")


def main() -> int:
    test_pretax_from_ledger()
    test_post_provision_back()
    print("OK: ledger-wired tax provision (PR A) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
