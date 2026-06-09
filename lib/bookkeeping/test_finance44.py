#!/usr/bin/env python3
"""Forensic monthly/yearly reports + transaction trace. Temp GLAW_HOME."""
from __future__ import annotations
import os, sys, tempfile
from decimal import Decimal
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def test_monthly_yearly_trace():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-rep-")
    import importlib, ledger as L, forensic_reports as FR
    importlib.reload(L); importlib.reload(FR)
    led = L.Ledger("t")
    led.post({"date": "2024-01-05", "source": "e1.pdf", "lines": [{"account": "Assets:Bank:B", "debit": 100000},
                                                                  {"account": "Income:Revenue", "credit": 100000}]})
    led.post({"date": "2024-02-10", "source": "e2.pdf", "lines": [{"account": "Expenses:COGS", "debit": 30000},
                                                                  {"account": "Assets:Bank:B", "credit": 30000}]})
    led.post({"date": "2025-03-01", "source": "e3.pdf", "lines": [{"account": "Income:Revenue", "credit": 50000},
                                                                  {"account": "Assets:Bank:B", "debit": 50000}]})
    out = tempfile.mkdtemp(prefix="glaw-repout-")
    r = FR.reports("t", out, entity="Test Co")
    assert r["months"] == 3 and r["years"] == 2
    assert r["yearly"]["2024"] == "70000.00" and r["yearly"]["2025"] == "50000.00"
    assert r["postings_traced"] == 6
    for n in ("09_monthly_reports.md", "10_yearly_reports.md", "11_transaction_trace.csv", "11_transaction_trace.md"):
        assert (Path(out) / n).exists() and (Path(out) / n).stat().st_size > 0
    # the trace carries the source statement file for every posting (traceable)
    csv_text = (Path(out) / "11_transaction_trace.csv").read_text()
    assert "e1.pdf" in csv_text and "e3.pdf" in csv_text
    print("  ✓ reports: monthly (3) + yearly (2024=70k, 2025=50k) + full trace (6 postings, source-tied)")


def test_empty_ledger():
    """An empty book must produce empty reports, not crash (regression — IndexError on trace[0])."""
    import os, tempfile
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-rep-empty-")
    import importlib, ledger as L, forensic_reports as FR
    importlib.reload(L); importlib.reload(FR)
    out = tempfile.mkdtemp()
    r = FR.reports("emptybook", out)
    assert r["postings_traced"] == 0 and r["months"] == 0 and r["years"] == 0
    from pathlib import Path
    assert (Path(out) / "11_transaction_trace.csv").exists()        # header-only, no crash
    print("  ✓ reports: empty ledger → empty reports + header-only trace CSV (no IndexError)")


def main() -> int:
    test_monthly_yearly_trace(); test_empty_ledger()
    print("OK: forensic monthly/yearly reports + trace passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
