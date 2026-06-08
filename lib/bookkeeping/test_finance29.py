#!/usr/bin/env python3
"""PR8 — 1099-NEC from the GL (vendor payments ≥ $600). Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _book():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-1099-")
    import importlib
    import ledger as L
    importlib.reload(L)
    led = L.Ledger("co")
    led.post({"date": "2026-03-01", "vendor": "Acme Consulting",
              "lines": [{"account": "Expenses:Contractor", "debit": 500},
                        {"account": "Assets:Bank:Checking", "credit": 500}]})
    led.post({"date": "2026-06-01", "vendor": "Acme Consulting",
              "lines": [{"account": "Expenses:Contractor", "debit": 300},
                        {"account": "Assets:Bank:Checking", "credit": 300}]})
    led.post({"date": "2026-07-01", "vendor": "Bob Smith",
              "lines": [{"account": "Expenses:Contractor", "debit": 400},
                        {"account": "Assets:Bank:Checking", "credit": 400}]})
    led.post({"date": "2026-08-01",   # no vendor tag → not a 1099
              "lines": [{"account": "Expenses:Rent", "debit": 2000},
                        {"account": "Assets:Bank:Checking", "credit": 2000}]})
    return L


def test_threshold_and_aggregation():
    _book()
    import info_returns as IR
    import importlib
    importlib.reload(IR)
    d = IR.gather_1099("co", tax_year=2026)
    assert d["count"] == 1
    assert d["recipients"][0]["name"] == "Acme Consulting"
    assert d["recipients"][0]["nonemployee_compensation"] == "800.00"   # 500 + 300 aggregated
    assert d["below_threshold"][0]["vendor"] == "Bob Smith" and d["below_threshold"][0]["total"] == "400.00"
    assert d["total_reported"] == "800.00"
    print("  ✓ 1099: payments aggregate per vendor; ≥$600 reported, <$600 tracked, untagged ignored")


def test_account_filter_and_master():
    _book()
    import info_returns as IR
    import importlib
    importlib.reload(IR)
    # vendor master fills TIN; account filter restricts to contractor payments
    d = IR.gather_1099("co", tax_year=2026, accounts=["Expenses:Contractor"],
                       vendor_master={"Acme Consulting": {"tin": "12-3456789", "address": "1 Main St"}})
    assert d["recipients"][0]["tin"] == "12-3456789"
    print("  ✓ 1099: account-prefix filter + vendor master (TIN/address) applied")


def main() -> int:
    test_threshold_and_aggregation()
    test_account_filter_and_master()
    print("OK: 1099-NEC from the GL (PR8) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
