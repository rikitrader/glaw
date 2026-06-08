#!/usr/bin/env python3
"""Smoke test for the reconstruction-hardening fixes: opening balances, the false
audit-ready kill, multi-currency detection, and credit-card sign handling.
Temp GLAW_HOME; no network (reconstruct shells out to runner.py via sys.executable)."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _fresh():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-h-")
    import importlib
    import ledger as L
    importlib.reload(L)
    import reconstruct as R
    importlib.reload(R)
    return L, R


def _coa(d):
    p = Path(d, "coa.json")
    p.write_text('{"default":"Income:Misc","rules":[{"pattern":"DEPOSIT","account":"Income:Sales"},'
                 '{"pattern":"FUEL","account":"Expenses:Fuel"},{"pattern":"PAYMENT","account":"Expenses:Misc"}]}')
    return str(p)


def test_opening_balance_ties():
    L, R = _fresh()
    d = tempfile.mkdtemp(prefix="ob-")
    Path(d, "chk.csv").write_text("Date,Description,Amount\n2026-01-15,DEPOSIT,10000\n")
    m = {"book": "ob", "entity": "Ongoing Co", "sources": [
        {"path": str(Path(d, "chk.csv")), "account": "Assets:Bank:Checking", "map": _coa(d),
         "opening": "50000", "closing": "60000"}]}
    res = R.reconstruct(m)
    bal = L.Ledger("ob").balances()
    assert bal["Assets:Bank:Checking"] == Decimal("60000")          # opening 50k + 10k deposit
    assert bal["Equity:Opening Balance Equity"] == Decimal("-50000")  # the opening entry (credit)
    assert res["tie_out"]["all_tied"] and res["audit_ready"]
    assert res["golden_rule"]["all_verified"]
    print("  ✓ opening balance: posts 50k via Opening Balance Equity, GL ties to 60k, AUDIT-READY")


def test_false_audit_ready_is_dead():
    L, R = _fresh()
    d = tempfile.mkdtemp(prefix="fa-")
    Path(d, "chk.csv").write_text("Date,Description,Amount\n2026-01-15,DEPOSIT,10000\n")
    # NO opening/closing → engine returns no closing → tie-out has nothing to tie
    m = {"book": "fa", "entity": "X", "sources": [
        {"path": str(Path(d, "chk.csv")), "account": "Assets:Bank:Checking", "map": _coa(d)}]}
    res = R.reconstruct(m)
    assert res["audit_ready"] is False, "no closing balance MUST NOT be audit-ready"
    assert res["tie_out"]["all_tied"] is False
    assert res["tie_out"]["accounts"][0]["statement_closing"] is None
    print("  ✓ false-audit-ready killed: account with no statement closing → NOT audit-ready")


def test_multi_currency_flagged():
    L, _ = _fresh()
    import importlib
    import books_doctor as BD
    importlib.reload(BD)
    led = L.Ledger("mc")
    led.post({"date": "2026-01-05", "currency": "USD",
              "lines": [{"account": "Assets:Bank:Checking", "debit": 100}, {"account": "Income:Sales", "credit": 100}]})
    led.post({"date": "2026-01-06", "currency": "EUR",
              "lines": [{"account": "Assets:Bank:EUR", "debit": 100}, {"account": "Income:Sales", "credit": 100}]})
    BD.FAIL = 0; BD.WARN = 0
    rc = BD.run_ledger("mc")
    assert rc == 1 and BD.FAIL >= 1, "a book mixing USD+EUR must FAIL books-doctor"
    print("  ✓ multi-currency: USD+EUR book fails the gate (revalue to one reporting currency first)")


def test_credit_card_liability_sign():
    L, R = _fresh()
    d = tempfile.mkdtemp(prefix="cc-")
    # charges-NEGATIVE convention (common): a $200 fuel charge → liability up by 200
    Path(d, "amex.csv").write_text("Date,Description,Amount\n2026-01-10,FUEL,-200\n")
    m = {"book": "cc", "entity": "X", "sources": [
        {"path": str(Path(d, "amex.csv")), "account": "Liabilities:CreditCard:Amex", "map": _coa(d),
         "type": "liability", "opening": "0", "closing": "-200"}]}
    R.reconstruct(m)
    bal = L.Ledger("cc").balances()
    # liability is credit-normal → a $200 charge makes the signed balance −200 (owed)
    assert bal["Liabilities:CreditCard:Amex"] == Decimal("-200"), bal.get("Liabilities:CreditCard:Amex")
    assert bal["Expenses:Fuel"] == Decimal("200")                  # expense recognized
    # invert flips a charges-POSITIVE statement to the same result
    L2, R2 = _fresh()
    Path(d, "amex2.csv").write_text("Date,Description,Amount\n2026-01-10,FUEL,200\n")  # charge shown positive
    m2 = {"book": "cc2", "entity": "X", "sources": [
        {"path": str(Path(d, "amex2.csv")), "account": "Liabilities:CreditCard:Amex", "map": _coa(d),
         "type": "liability", "invert": True, "opening": "0", "closing": "-200"}]}
    R2.reconstruct(m2)
    assert L2.Ledger("cc2").balances()["Expenses:Fuel"] == Decimal("200")
    print("  ✓ credit-card: charge increases the liability; --invert normalizes a charges-positive statement")


def main() -> int:
    test_opening_balance_ties()
    test_false_audit_ready_is_dead()
    test_multi_currency_flagged()
    test_credit_card_liability_sign()
    print("OK: reconstruction-hardening smoke passed (opening + false-audit-ready + currency + card)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
