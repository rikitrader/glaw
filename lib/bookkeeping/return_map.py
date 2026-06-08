#!/usr/bin/env python3
"""GLAW income-tax return-line mapping — populate the principal lines of a business income-tax
return (1120 / 1120-S / 1065 / Schedule C) DIRECTLY from the posted trial balance + the
book-to-tax (M-1) differences, instead of a blank scaffold.

The income/deduction lines are book-basis (as on the financial statements); Schedule M-1 then
reconciles book income to taxable income via the permanent/temporary differences. By
construction book pretax here == tax_provision.pretax_from_ledger (all income − all deductions,
excluding non-deductible income tax), so the return ties to the statements and the provision.

(Distinct from glaw-irs-file, which transmits INFORMATION returns — 1099 / W-2 / 941.)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L          # noqa: E402

# 1120-style deduction lines (the canonical reference; 1120-S/1065 share the structure).
_DED_LINES = [
    ("Expenses:Officer", "12", "Compensation of officers"),
    ("Expenses:Salaries", "13", "Salaries and wages"),
    ("Expenses:Wages", "13", "Salaries and wages"),
    ("Expenses:Repairs", "14", "Repairs and maintenance"),
    ("Expenses:Bad Debt", "15", "Bad debts"),
    ("Expenses:Rent", "16", "Rents"),
    ("Expenses:Taxes", "17", "Taxes and licenses"),
    ("Expenses:Interest", "18", "Interest"),
    ("Expenses:Depreciation", "20", "Depreciation"),
    ("Expenses:Advertising", "22", "Advertising"),
    ("Expenses:Benefits", "24", "Employee benefit programs"),
    ("Expenses:Employee Benefit", "24", "Employee benefit programs"),
]
_FINAL = {"1120": "Taxable income", "1120-S": "Ordinary business income",
          "1065": "Ordinary business income", "schedule-c": "Net profit"}


def _ded_line(acct: str):
    for pref, line, label in _DED_LINES:
        if acct.startswith(pref):
            return line, label
    return "26", "Other deductions"


def map_return(book: str, form: str = "1120", *, m1: dict | None = None,
               as_of: str | None = None, nol_carryforwards: list | None = None,
               k1_owners: list | None = None, k1_separately_stated: dict | None = None) -> dict:
    bal = L.Ledger(book).balances(as_of)
    gross_receipts = Decimal("0")
    other_income = Decimal("0")
    cogs = Decimal("0")
    ded: dict = defaultdict(Decimal)
    for a, b in bal.items():
        if b == 0:
            continue
        root = a.split(":", 1)[0]
        if root in ("Income", "Revenue"):
            amt = -b                                            # credit-normal → positive income
            if a.startswith(("Income:Sales", "Income:Revenue", "Revenue")):
                gross_receipts += amt
            else:
                other_income += amt
        elif root == "Expenses":
            if a.startswith(("Expenses:COGS", "Expenses:Cost")):
                cogs += b
            elif a.startswith(("Expenses:Income Tax", "Expenses:Federal Income Tax")):
                continue                                        # federal income tax is non-deductible
            else:
                ded[_ded_line(a)] += b
    gross_profit = gross_receipts - cogs
    total_income = gross_profit + other_income
    total_deductions = sum(ded.values(), Decimal("0"))
    book_pretax = total_income - total_deductions
    perm = Decimal(str(m1["permanent"])) if m1 else Decimal("0")
    temp = Decimal(str(m1["temporary"])) if m1 else Decimal("0")
    taxable = book_pretax + perm - temp

    lines = [{"line": "1a", "label": "Gross receipts", "amount": str(gross_receipts)},
             {"line": "2", "label": "Cost of goods sold", "amount": str(cogs)},
             {"line": "3", "label": "Gross profit", "amount": str(gross_profit)},
             {"line": "10", "label": "Other income", "amount": str(other_income)},
             {"line": "11", "label": "Total income", "amount": str(total_income)}]
    for (line, label), amt in sorted(ded.items(), key=lambda kv: kv[0][0]):
        lines.append({"line": line, "label": label, "amount": str(amt)})
    lines += [{"line": "27", "label": "Total deductions", "amount": str(total_deductions)},
              {"line": "28", "label": "Book income (Schedule M-1 line 1)", "amount": str(book_pretax)}]
    if m1:
        lines += [{"line": "M-1", "label": "+ permanent differences", "amount": str(perm)},
                  {"line": "M-1", "label": "− temporary differences", "amount": str(-temp)}]
    taxable_before_nol = taxable
    nol_deduction = Decimal("0")
    nol_result = None
    if nol_carryforwards is not None:
        import nol as NOL
        nol_result = NOL.apply_nol(taxable, nol_carryforwards)
        nol_deduction = Decimal(nol_result["nol_deduction"])
        taxable = Decimal(nol_result["taxable_income_after_nol"])
        lines.append({"line": "29a", "label": "Taxable income before NOL", "amount": str(taxable_before_nol)})
        lines.append({"line": "29c", "label": "NOL deduction", "amount": str(nol_deduction)})
    lines.append({"line": "30", "label": _FINAL.get(form, "Taxable income"), "amount": str(taxable)})
    out = {"form": form, "book": book, "book_pretax": str(book_pretax),
           "permanent": str(perm), "temporary": str(temp),
           "taxable_income_before_nol": str(taxable_before_nol),
           "nol_deduction": str(nol_deduction), "taxable_income": str(taxable), "lines": lines}
    if nol_result:
        out["nol_remaining_carryforward"] = nol_result["remaining_carryforward"]
    if k1_owners and form in ("1065", "1120-S"):
        import k1 as K1
        out["k1"] = K1.allocate(taxable, k1_owners, form=form,
                                separately_stated=k1_separately_stated)
    return out


def render_text(d: dict) -> str:
    o = ["=" * 60, f"FORM {d['form'].upper()} — return lines from the GL  (book {d['book']})", "-" * 60]
    for ln in d["lines"]:
        o.append(f"  {ln['line']:>4}  {ln['label'][:38]:<40}{Decimal(ln['amount']):>14,.2f}")
    o.append("=" * 60)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-return-map")
    ap.add_argument("--book", required=True)
    ap.add_argument("--form", default="1120", choices=list(_FINAL))
    ap.add_argument("--rules", default=None, help="apply book-to-tax M-1 rules (default: built-in)")
    ap.add_argument("--tax-depreciation", default=None)
    ap.add_argument("--nol", default=None, help="NOL carryforwards JSON: [{year, amount, pre_tcja?}]")
    ap.add_argument("--k1-owners", default=None, help="(1065/1120-S) owners JSON [{owner, pct}] → K-1s")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    m1 = None
    if a.rules is not None:
        import book_to_tax as BT
        td = Decimal(a.tax_depreciation) if a.tax_depreciation is not None else None
        m1 = BT.book_to_tax(a.book, BT.load_rules(a.rules), as_of=a.as_of, tax_depreciation=td)
    nol_cf = json.loads(Path(a.nol).read_text(encoding="utf-8")) if a.nol else None
    owners = json.loads(Path(a.k1_owners).read_text(encoding="utf-8")) if a.k1_owners else None
    d = map_return(a.book, a.form, m1=m1, as_of=a.as_of, nol_carryforwards=nol_cf, k1_owners=owners)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
