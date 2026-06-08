#!/usr/bin/env python3
"""GLAW tax-provision tie-out — the assurance check that the tax numbers in the books are right.

Two checks:
  1. INTERNAL CONSISTENCY (no inputs): the posted income-tax expense equals the income-tax
     payable + the deferred-tax movement it created (Expenses:Income Tax == Income Tax Payable +
     Deferred Tax liability − Deferred Tax asset). Verifiable from the GL alone.
  2. RECOMPUTE (with the rate/rules): recompute the ASC-740 provision from the posted P&L and the
     book-to-tax M-1, and assert it ties to the posted income-tax expense; and, given a deferred
     basis schedule, that the balance-sheet deferred tax ties to the roll-forward closing balance.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L          # noqa: E402

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def internal_consistency(book: str, as_of: str | None = None) -> dict:
    bal = L.Ledger(book).balances(as_of)
    expense = bal.get("Expenses:Income Tax", Decimal("0"))               # debit-normal
    payable = -bal.get("Liabilities:Income Tax Payable", Decimal("0"))   # credit-normal → positive
    def_liab = -bal.get("Liabilities:Deferred Tax", Decimal("0"))
    def_asset = bal.get("Assets:Deferred Tax", Decimal("0"))
    expected_expense = _q(payable + def_liab - def_asset)
    return {"income_tax_expense": str(_q(expense)), "income_tax_payable": str(_q(payable)),
            "deferred_tax_liability": str(_q(def_liab)), "deferred_tax_asset": str(_q(def_asset)),
            "expense_should_equal": str(expected_expense),
            "consistent": _q(expense) == expected_expense, "has_tax": expense != 0 or payable != 0}


def recompute(book: str, rate, *, rules: str | None = None, assets=None, year=None,
              deferred_schedule=None, prior_dtl="0", as_of: str | None = None) -> dict:
    import tax_provision as TP
    pretax = TP.pretax_from_ledger(book, as_of)
    permanent, temporary = Decimal("0"), Decimal("0")
    if rules is not None:
        import book_to_tax as BT
        import depreciation as DEP
        td = DEP.tax_depreciation_for_year(assets, year) if (assets and year is not None) else None
        m1 = BT.book_to_tax(book, BT.load_rules(rules), as_of=as_of, tax_depreciation=td)
        permanent, temporary = m1["permanent"], m1["temporary"]
    prov = TP.provision(pretax, permanent, temporary, _dec(rate))
    bal = L.Ledger(book).balances(as_of)
    posted_expense = _q(bal.get("Expenses:Income Tax", Decimal("0")))
    out = {"recomputed_total_provision": str(prov["total_provision"]),
           "posted_income_tax_expense": str(posted_expense),
           "provision_ties": _q(_dec(prov["total_provision"])) == posted_expense,
           "internal": internal_consistency(book, as_of)}
    if deferred_schedule is not None:
        import deferred_tax as DT
        roll = DT.deferred_rollforward(deferred_schedule, rate, prior=prior_dtl)
        posted_def = _q(-bal.get("Liabilities:Deferred Tax", Decimal("0"))
                        + bal.get("Assets:Deferred Tax", Decimal("0")) * Decimal("-1"))
        out["deferred_rollforward_closing"] = roll["closing_balance"]
        out["posted_deferred_tax"] = str(posted_def)
        out["deferred_ties"] = _q(_dec(roll["closing_balance"])) == posted_def
    return out


def render_text(d: dict) -> str:
    o = ["=" * 56, "TAX PROVISION TIE-OUT", "-" * 56,
         f"  recomputed provision     {_dec(d['recomputed_total_provision']):>16,.2f}",
         f"  posted income-tax expense{_dec(d['posted_income_tax_expense']):>16,.2f}",
         f"  provision ties: {'✓' if d['provision_ties'] else '✗'}"]
    if "deferred_ties" in d:
        o += [f"  deferred roll-forward     {_dec(d['deferred_rollforward_closing']):>16,.2f}",
              f"  posted deferred tax       {_dec(d['posted_deferred_tax']):>16,.2f}",
              f"  deferred ties: {'✓' if d['deferred_ties'] else '✗'}"]
    ic = d["internal"]
    o += ["-" * 56, f"  internal consistency (expense == payable + deferred): "
          f"{'✓' if ic['consistent'] else '✗'}", "=" * 56]
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-tax-tieout")
    ap.add_argument("--book", required=True)
    ap.add_argument("--rate", default=None, help="statutory rate %% (omit → internal-consistency only)")
    ap.add_argument("--rules", default=None)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    if a.rate is None:
        d = internal_consistency(a.book, a.as_of)
        print(json.dumps(d, indent=2, default=str) if a.format == "json"
              else f"internal consistency (expense == payable + deferred): "
                   f"{'✓ ties' if d['consistent'] else '✗ MISMATCH'}")
        return 0 if d["consistent"] else 1
    d = recompute(a.book, a.rate, rules=a.rules, as_of=a.as_of)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0 if d["provision_ties"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
