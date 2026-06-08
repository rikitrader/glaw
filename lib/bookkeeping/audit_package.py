#!/usr/bin/env python3
"""GLAW IRS-exam audit package — the response artifacts for a field examination:
  - a SUBSTANTIATION INDEX pulled from the general ledger: for each account under exam, the actual
    posted entries (date, amount, memo, vendor) that support the deduction, tied to the books;
  - a FORM 4549 compare: the taxpayer's figures vs the agent's proposed adjustments → the disputed
    delta per line, the total adjustment, and the additional tax at the rate;
  - an IDR (Information Document Request) response index: each requested item → provided / where /
    objection, so nothing is missed and nothing is over-produced.
Every substantiation figure traces to a real posted entry — nothing is fabricated.
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


def substantiation_index(book: str, accounts: list[str], *, as_of: str | None = None) -> dict:
    out = {}
    for acct_pref in accounts:
        entries, total = [], Decimal("0")
        for e in L.Ledger(book).entries(as_of):
            for ln in e["lines"]:
                if ln["account"].startswith(acct_pref):
                    amt = _dec(ln["debit"]) - _dec(ln["credit"])
                    total += amt
                    entries.append({"id": e["id"], "date": e["date"], "amount": str(_q(amt)),
                                    "memo": e.get("memo", ""), "vendor": e.get("vendor", ""),
                                    "entry_hash": e.get("entry_hash", "")})
        out[acct_pref] = {"supporting_entries": entries, "count": len(entries),
                          "total_substantiated": str(_q(total))}
    return out


def form4549_compare(as_filed: dict, proposed: dict, *, rate_pct="21") -> dict:
    rate = _dec(rate_pct) / Decimal("100")
    lines, total_adj = [], Decimal("0")
    for line in sorted(set(as_filed) | set(proposed)):
        filed = _dec(as_filed.get(line, 0))
        prop = _dec(proposed.get(line, 0))
        delta = _q(prop - filed)
        total_adj += delta
        lines.append({"line": line, "as_filed": str(_q(filed)), "proposed": str(_q(prop)),
                      "adjustment": str(delta), "disputed": delta != 0})
    additional_tax = _q(total_adj * rate)
    return {"lines": lines, "total_adjustment": str(_q(total_adj)),
            "additional_tax": str(additional_tax), "rate_pct": str(_dec(rate_pct))}


def idr_index(items: list[dict]) -> dict:
    rows = []
    for it in items:
        status = it.get("status", "provided")
        rows.append({"request": it.get("request", "?"), "status": status,
                     "location": it.get("location", ""), "objection": it.get("objection", "")})
    provided = sum(1 for r in rows if r["status"] == "provided")
    return {"items": rows, "total": len(rows), "provided": provided,
            "outstanding": len(rows) - provided}


def render_text(d: dict) -> str:
    o = ["=" * 60, "IRS EXAM — AUDIT RESPONSE PACKAGE", "-" * 60]
    if "substantiation" in d:
        for acct, s in d["substantiation"].items():
            o.append(f"  {acct[:34]:<36}{_dec(s['total_substantiated']):>14,.2f}  "
                     f"({s['count']} entries tied to the GL)")
    if "form4549" in d:
        f = d["form4549"]
        o += ["-" * 60, f"  Form 4549 total adjustment {_dec(f['total_adjustment']):>16,.2f}",
              f"  additional tax @ {f['rate_pct']}%      {_dec(f['additional_tax']):>16,.2f}"]
    if "idr" in d:
        i = d["idr"]
        o += ["-" * 60, f"  IDR: {i['provided']}/{i['total']} provided, {i['outstanding']} outstanding"]
    o.append("=" * 60)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-audit-package")
    ap.add_argument("--book", default=None)
    ap.add_argument("--accounts", default=None, help="comma-separated account prefixes under exam")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--form4549", default=None, help="JSON: {as_filed:{...}, proposed:{...}, rate}")
    ap.add_argument("--idr", default=None, help="JSON list of IDR items")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    out = {}
    if a.book and a.accounts:
        out["substantiation"] = substantiation_index(a.book, a.accounts.split(","), as_of=a.as_of)
    if a.form4549:
        f = json.loads(Path(a.form4549).read_text(encoding="utf-8"))
        out["form4549"] = form4549_compare(f.get("as_filed", {}), f.get("proposed", {}),
                                           rate_pct=f.get("rate", "21"))
    if a.idr:
        out["idr"] = idr_index(json.loads(Path(a.idr).read_text(encoding="utf-8")))
    print(json.dumps(out, indent=2, default=str) if a.format == "json" else render_text(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
