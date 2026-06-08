#!/usr/bin/env python3
"""GLAW book-to-tax (Schedule M-1/M-3) engine — derive the permanent and temporary differences
DIRECTLY from the posted GL, instead of hand-entering them into the tax provision.

Sign convention matches tax_provision.provision():  taxable = pretax + permanent − temporary.
  PERMANENT (never reverse):
    - a partly/non-deductible expense (meals 50 %, penalties 0 %) → ADD BACK the disallowed
      portion → permanent positive (raises taxable income).
    - tax-exempt book income → SUBTRACT it → permanent negative.
  TEMPORARY (reverse → deferred tax):
    - depreciation: tax (MACRS) minus book depreciation. Tax > book → more deduction now →
      taxable lower now → temporary POSITIVE → deferred tax LIABILITY.
    - an accrued-but-unpaid expense: book-deducted, not yet tax-deductible → taxable higher now
      → temporary NEGATIVE → deferred tax ASSET.
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
DEFAULT_RULES = HERE / "tax_rules.default.json"


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def book_to_tax(book: str, rules: dict, *, as_of: str | None = None,
                tax_depreciation: Decimal | None = None) -> dict:
    bal = L.Ledger(book).balances(as_of)
    permanent = Decimal("0")
    temporary = Decimal("0")
    m1 = []

    for rule in rules.get("permanent", []):
        pref = rule["match"]
        matched = {a: b for a, b in bal.items() if a.startswith(pref) and b != 0}
        if not matched:
            continue
        if rule.get("exclude_income"):
            # income account: credit-normal (bal negative). book income = −bal; subtract it.
            inc = -sum(matched.values(), Decimal("0"))           # positive book income
            permanent += -inc
            m1.append({"account": pref, "book": str(_q(inc)), "treatment": "permanent",
                       "difference": str(_q(-inc)), "label": rule["label"]})
        else:
            book_amt = sum(matched.values(), Decimal("0"))       # expense, debit-normal (positive)
            disallowed = _q(book_amt * (Decimal("100") - _dec(rule.get("deductible_pct", 0))) / Decimal("100"))
            permanent += disallowed
            m1.append({"account": pref, "book": str(_q(book_amt)), "treatment": "permanent",
                       "difference": str(disallowed), "label": rule["label"]})

    for rule in rules.get("temporary", []):
        pref = rule["match"]
        matched = {a: b for a, b in bal.items() if a.startswith(pref) and b != 0}
        if not matched:
            continue
        book_amt = sum(matched.values(), Decimal("0"))
        if rule.get("kind") == "depreciation":
            tax_dep = tax_depreciation if tax_depreciation is not None else book_amt
            diff = _q(_dec(tax_dep) - book_amt)                  # tax>book → positive → DTL
            temporary += diff
            m1.append({"account": pref, "book": str(_q(book_amt)), "tax": str(_q(_dec(tax_dep))),
                       "treatment": "temporary", "difference": str(diff), "label": rule["label"]})
        else:                                                    # accrual: book-deducted, not tax → DTA
            diff = _q(-book_amt)
            temporary += diff
            m1.append({"account": pref, "book": str(_q(book_amt)), "treatment": "temporary",
                       "difference": str(diff), "label": rule["label"]})

    return {"book": book, "permanent": _q(permanent), "temporary": _q(temporary), "m1_lines": m1}


def render_text(d: dict) -> str:
    o = ["=" * 64, f"BOOK-TO-TAX (Schedule M-1) — {d['book']}", "-" * 64]
    for ln in d["m1_lines"]:
        tax = f" (tax {ln['tax']})" if ln.get("tax") else ""
        o.append(f"  {ln['label'][:40]:<42}{ln['treatment']:<10}{_dec(ln['difference']):>14,.2f}{tax}")
    o += ["-" * 64,
          f"  net permanent difference {d['permanent']:>30,.2f}",
          f"  net temporary difference {d['temporary']:>30,.2f}",
          "  (taxable income = pretax book + permanent − temporary)", "=" * 64]
    return "\n".join(o)


def load_rules(path: str | None) -> dict:
    if path in (None, "", "default"):
        path = DEFAULT_RULES
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-book-to-tax")
    ap.add_argument("--book", required=True)
    ap.add_argument("--rules", default=None, help="rules JSON (default: built-in tax_rules.default.json)")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--tax-depreciation", default=None, help="total tax/MACRS depreciation for the period")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    td = _dec(a.tax_depreciation) if a.tax_depreciation is not None else None
    d = book_to_tax(a.book, load_rules(a.rules), as_of=a.as_of, tax_depreciation=td)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
