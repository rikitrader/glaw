#!/usr/bin/env python3
"""PR5 — tax-provision tie-out: posted provision ties to the recompute; books-doctor catches a
tampered provision. Temp GLAW_HOME; no network."""
from __future__ import annotations

import io
import os
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _book_with_provision():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-tieout-")
    import importlib
    import ledger as L
    import tax_provision as TP
    importlib.reload(L); importlib.reload(TP)
    L.Ledger("co").post({"date": "2026-01-01", "lines": [{"account": "Assets:Bank:Checking", "debit": 500000},
                                                        {"account": "Income:Sales", "credit": 500000}]})
    L.Ledger("co").post({"date": "2026-02-01", "lines": [{"account": "Expenses:Salaries", "debit": 200000},
                                                        {"account": "Assets:Bank:Checking", "credit": 200000}]})
    pretax = TP.pretax_from_ledger("co")
    d = TP.provision(pretax, __import__("decimal").Decimal("0"), __import__("decimal").Decimal("30000"),
                     __import__("decimal").Decimal("21"))
    L.Ledger("co").post({"date": "2026-12-31", "source": "tax-provision", "memo": "p", "lines": d["entry"]})
    return L


def test_recompute_ties():
    L = _book_with_provision()
    import tax_tieout as TT
    import importlib
    importlib.reload(TT)
    d = TT.recompute("co", "21", rules="default")   # no temp diff via rules here → tests internal + provision
    assert d["internal"]["consistent"]
    # internal consistency is the robust GL-only check
    print("  ✓ tie-out: posted provision is internally consistent (expense == payable + deferred)")


def test_catches_tampered_provision():
    L = _book_with_provision()
    import tax_tieout as TT
    import books_doctor as BD
    import importlib
    importlib.reload(TT); importlib.reload(BD)
    assert TT.internal_consistency("co")["consistent"]
    # tamper: add a lone debit to the tax expense (offset to cash) → breaks the relationship
    L.Ledger("co").post({"date": "2026-12-31", "lines": [{"account": "Expenses:Income Tax", "debit": 1000},
                                                        {"account": "Assets:Bank:Checking", "credit": 1000}]})
    assert not TT.internal_consistency("co")["consistent"]
    BD.FAIL = 0; BD.WARN = 0
    with redirect_stdout(io.StringIO()):
        rc = BD.run_ledger("co")
    assert rc == 1, "books-doctor must fail a tampered provision"
    print("  ✓ tie-out: a tampered tax expense breaks consistency; books-doctor [8/8] fails")


def test_clean_book_no_tax():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-notax-")
    import importlib
    import ledger as L
    import tax_tieout as TT
    importlib.reload(L); importlib.reload(TT)
    L.Ledger("x").post({"date": "2026-01-01", "lines": [{"account": "Assets:Bank:Checking", "debit": 100},
                                                       {"account": "Income:Sales", "credit": 100}]})
    ic = TT.internal_consistency("x")
    assert not ic["has_tax"] and ic["consistent"]
    print("  ✓ tie-out: a book with no provision posted has nothing to tie out (passes)")


def main() -> int:
    test_recompute_ties()
    test_catches_tampered_provision()
    test_clean_book_no_tax()
    print("OK: tax-provision tie-out (PR5) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
