#!/usr/bin/env python3
"""Forensic deliverables: posted GL → 8 audit-ready report files. Temp GLAW_HOME."""
from __future__ import annotations
import os, sys, tempfile
from decimal import Decimal
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


UNRESOLVED_PLACEHOLDERS = ("[VERIFY", "[CLIENT", "[DATE", "[TODO", "[TBD")


def test_generates_all_eight():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-deliv-")
    import importlib, ledger as L, forensic_deliverables as FD
    importlib.reload(L); importlib.reload(FD)
    led = L.Ledger("t")
    led.post({"date": "2024-01-05", "lines": [{"account": "Assets:Bank:BofA-1", "debit": 100000},
                                              {"account": "Income:Revenue", "credit": 100000}]})
    led.post({"date": "2024-03-10", "lines": [{"account": "Expenses:COGS:Materials", "debit": 40000},
                                              {"account": "Assets:Bank:BofA-1", "credit": 40000}]})
    out = tempfile.mkdtemp(prefix="glaw-out-")
    res = FD.deliverables("t", out, entity="Test Co", form="1120-S")
    files = set(res["files"])
    for n in ("01_statement_reconstruction.md", "02_chart_of_accounts_trial_balance.md",
              "03_three_statement_and_footnotes.md", "04_credits_report.md", "05_irs_audit_readiness.md",
              "06_irs_forms_package.md", "07_error_resolution_log.md", "08_executive_cfo_ceo.md", "00_INDEX.json"):
        assert n in files, n
        assert (Path(out) / n).exists() and (Path(out) / n).stat().st_size > 0
    for path in Path(out).glob("*.md"):
        text = path.read_text(encoding="utf-8")
        assert not any(marker in text for marker in UNRESOLVED_PLACEHOLDERS), path.name
    assert res["trial_balance_balanced"]
    # gap detection: Jan and Mar present, Feb is a gap
    assert "2024-02" in res["gap_months"]
    print("  ✓ deliverables: all 8 reports + index generated; Feb gap detected; TB balanced")


def test_gap_detection():
    import forensic_deliverables as FD
    assert FD._months_between("2024-01", "2024-04") == ["2024-01", "2024-02", "2024-03", "2024-04"]
    assert FD._months_between("2023-11", "2024-02") == ["2023-11", "2023-12", "2024-01", "2024-02"]
    print("  ✓ deliverables: month-span enumeration spans year boundaries (gap detection)")


def main() -> int:
    test_generates_all_eight(); test_gap_detection()
    print("OK: forensic deliverables passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
