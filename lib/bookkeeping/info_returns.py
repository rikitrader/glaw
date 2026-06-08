#!/usr/bin/env python3
"""GLAW 1099-NEC from the GL — read vendor payments out of the posted ledger and build the
information-return data, instead of a blank scaffold (mirrors what return_map did for income-tax
returns; the payload feeds glaw-irs-file for transmission).

Entries are tagged with a `vendor` (the payee). For each vendor, the engine sums the expense-side
debits (optionally restricted to 1099-able accounts, e.g. contractor / professional fees) and
emits a 1099-NEC (box 1 nonemployee compensation) for any vendor at or above the $600 threshold.
A vendor master (name → TIN/address) fills the recipient detail when supplied.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L          # noqa: E402

_CENT = Decimal("0.01")
THRESHOLD = Decimal("600")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def gather_1099(book: str, *, tax_year: int | None = None, threshold=THRESHOLD,
                as_of: str | None = None, accounts: list | None = None,
                vendor_master: dict | None = None) -> dict:
    thresh = _dec(threshold)
    by_vendor: dict[str, Decimal] = defaultdict(Decimal)
    for e in L.Ledger(book).entries(as_of):
        vendor = e.get("vendor")
        if not vendor:
            continue
        for ln in e["lines"]:
            acct = ln["account"]
            if not acct.startswith("Expenses"):
                continue
            if accounts and not any(acct.startswith(p) for p in accounts):
                continue
            by_vendor[vendor] += _dec(ln["debit"]) - _dec(ln["credit"])   # net expense to the vendor

    master = vendor_master or {}
    recipients, below = [], []
    for vendor, total in sorted(by_vendor.items()):
        total = _q(total)
        if total >= thresh:
            info = master.get(vendor, {})
            recipients.append({"name": vendor, "tin": info.get("tin", "[VERIFY: W-9 TIN]"),
                               "address": info.get("address", "[VERIFY: address from W-9]"),
                               "nonemployee_compensation": str(total)})
        elif total > 0:
            below.append({"vendor": vendor, "total": str(total)})
    return {"form": "1099-NEC", "tax_year": tax_year, "threshold": str(_q(thresh)),
            "recipients": recipients, "below_threshold": below,
            "count": len(recipients),
            "total_reported": str(_q(sum((_dec(r["nonemployee_compensation"]) for r in recipients),
                                         Decimal("0"))))}


def render_text(d: dict) -> str:
    o = ["=" * 60, f"FORM 1099-NEC — vendor payments from the GL (year {d['tax_year']})", "-" * 60,
         f"  threshold ${_dec(d['threshold']):,.0f}; {d['count']} recipient(s) reportable", "-" * 60]
    for r in d["recipients"]:
        o.append(f"  {r['name'][:30]:<32}{_dec(r['nonemployee_compensation']):>14,.2f}   TIN {r['tin']}")
    if d["below_threshold"]:
        o.append(f"  (below ${_dec(d['threshold']):,.0f}, not reportable: "
                 f"{', '.join(b['vendor'] for b in d['below_threshold'])})")
    o += ["-" * 60, f"  total reported {_dec(d['total_reported']):>16,.2f}", "=" * 60]
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-1099")
    ap.add_argument("--book", required=True)
    ap.add_argument("--year", type=int, default=None)
    ap.add_argument("--threshold", default="600")
    ap.add_argument("--accounts", default=None, help="comma-separated account prefixes to include")
    ap.add_argument("--vendor-master", default=None, help="JSON: {vendor: {tin, address}}")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    accounts = a.accounts.split(",") if a.accounts else None
    master = json.loads(Path(a.vendor_master).read_text(encoding="utf-8")) if a.vendor_master else None
    d = gather_1099(a.book, tax_year=a.year, threshold=a.threshold, as_of=a.as_of,
                    accounts=accounts, vendor_master=master)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
