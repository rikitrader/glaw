#!/usr/bin/env python3
"""Forensic adversarial gate: enforcement red-team + chief resolution, executable. Temp GLAW_HOME."""
from __future__ import annotations
import os, sys, tempfile
from decimal import Decimal
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _book():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-adv-")
    import importlib, ledger as L
    importlib.reload(L)
    led = L.Ledger("t")
    led.post({"date": "2024-01-01", "lines": [{"account": "Assets:Bank:B", "debit": 700000},
                                              {"account": "Liabilities:Loans-Payable:X", "credit": 700000}]})
    led.post({"date": "2024-02-01", "lines": [{"account": "Expenses:Operating:Card-POS-Uncategorized", "debit": 100000},
                                              {"account": "Assets:Bank:B", "credit": 100000}]})
    led.post({"date": "2024-03-01", "lines": [{"account": "Equity:Owner Draw", "debit": 50000},
                                              {"account": "Assets:Bank:B", "credit": 50000}]})
    return L


def test_red_team_finds_issues():
    _book()
    import importlib, forensic_adversarial as FA
    importlib.reload(FA)
    F = FA.red_team("t", documented_loan_notes="200000")
    ids = {f["id"] for f in F}
    assert "loan_without_note" in ids and "unsubstantiated_card" in ids and "reasonable_comp" in ids
    print("  ✓ red-team: detects naked loan, §274(d) card spend, reasonable-comp (deterministic)")


def test_chief_gate():
    _book()
    import importlib, forensic_adversarial as FA
    importlib.reload(FA)
    open_d = FA.review("t", documented_loan_notes="200000")
    assert open_d["verdict"] == "NOT AUDIT-READY" and open_d["open_critical_high"] >= 3
    res = {f["id"]: "cleared" for f in FA.red_team("t", documented_loan_notes="200000")}
    cleared = FA.review("t", documented_loan_notes="200000", resolutions=res)
    assert cleared["verdict"] == "AUDIT-READY" and cleared["open_critical_high"] == 0
    print("  ✓ chief gate: NOT AUDIT-READY with open issues → AUDIT-READY only when all cleared")


def test_documented_loan_clears():
    _book()
    import importlib, forensic_adversarial as FA
    importlib.reload(FA)
    F = FA.red_team("t", documented_loan_notes="700000")
    assert "loan_without_note" not in {f["id"] for f in F}
    print("  ✓ red-team: a fully-documented loan raises no naked-loan finding")


def main() -> int:
    test_red_team_finds_issues(); test_chief_gate(); test_documented_loan_clears()
    print("OK: forensic adversarial gate (executable red-team + chief) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
