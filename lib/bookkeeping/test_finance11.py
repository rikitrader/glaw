#!/usr/bin/env python3
"""Smoke test for the HTML financial-report export. Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def test_export_html():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-exp-")
    import importlib
    import ledger as L
    importlib.reload(L)
    import export_report as X
    importlib.reload(X)
    L.Ledger("r").post({"date": "2026-06-10", "memo": "seed", "lines": [
        {"account": "Assets:Bank:Checking", "debit": 50000},
        {"account": "Assets:AR", "debit": 20000},
        {"account": "Expenses:Materials", "debit": 30000},
        {"account": "Income:JobRevenue", "credit": 95000},
        {"account": "Liabilities:AP", "credit": 5000}]})
    doc = X.generate_html("r", period="2026-06", entity="Acme Roofing LLC", chart="roofing")
    assert doc.startswith("<!doctype html>")
    assert "Acme Roofing LLC" in doc
    for section in ("Financial statements", "Statement of cash flows",
                    "Key performance indicators", "Management discussion"):
        assert section in doc, f"missing section: {section}"
    assert "95,000.00" in doc                     # revenue figure rendered
    assert "65,000.00" in doc                     # net income (95k - 30k) rendered
    assert "Not legal, tax, or accounting advice" in doc   # UPL footer
    assert doc.count("<script") == 0              # self-contained, no scripts
    print("  ✓ export: branded HTML with statements + cash flow + KPIs + MD&A, real figures, UPL footer")


def test_gsheet_guarded():
    import export_report as X
    # Source-only mode writes a local CSV instead of requiring Google credentials.
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-gsheet-")
    msg = X.push_gsheet("nonexistent-book", "x")
    out = Path(msg)
    assert out.name == "x.trial_balance.csv"
    assert out.exists()
    assert out.read_text(encoding="utf-8").startswith("Account,Debit,Credit")
    print("  ✓ export: gsheet alias writes local CSV without Google credentials")


def main() -> int:
    test_export_html()
    test_gsheet_guarded()
    print("OK: financial-report export smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
