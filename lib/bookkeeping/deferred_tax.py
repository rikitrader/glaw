#!/usr/bin/env python3
"""GLAW deferred-tax roll-forward — track book vs tax basis per asset across periods and COMPUTE
the deferred tax balance + the period movement, instead of estimating the temporary difference.

For each item, the temporary difference = book basis − tax basis. Book > tax basis (e.g. MACRS
depreciated faster, so the tax basis is lower) → future taxable income on recovery → a deferred
tax LIABILITY now. Book < tax basis → a deferred tax ASSET. The cumulative temp difference × the
rate = the closing DTL/DTA balance; the change from the prior balance = this period's deferred
tax expense (the `deferred` leg of the provision JE).

Feeds tax_provision: the period temporary difference = cumulative_temp_diff(now) − prior_temp_diff.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _rate(v) -> Decimal:
    r = _dec(v)
    return r / Decimal("100") if r > 1 else r        # accept 21 or 0.21


def deferred_rollforward(items: list[dict], rate, *, prior: Decimal | str = "0") -> dict:
    r = _rate(rate)
    by_asset = []
    cum = Decimal("0")
    for it in items:
        temp = _q(_dec(it["book_basis"]) - _dec(it["tax_basis"]))
        cum += temp
        dt = _q(temp * r)
        by_asset.append({"asset": it.get("asset", "?"),
                         "book_basis": str(_q(_dec(it["book_basis"]))),
                         "tax_basis": str(_q(_dec(it["tax_basis"]))),
                         "temp_diff": str(temp), "deferred_tax": str(dt),
                         "type": "DTL" if temp > 0 else ("DTA" if temp < 0 else "none")})
    closing = _q(cum * r)
    opening = _q(_dec(prior))
    movement = _q(closing - opening)
    # period temporary difference (feeds tax_provision --temporary): movement ÷ rate
    period_temp = _q(movement / r) if r else Decimal("0")
    return {"rate_pct": _q(r * 100), "opening_balance": opening, "closing_balance": closing,
            "movement": movement, "cumulative_temp_diff": _q(cum),
            "period_temporary_diff": period_temp,
            "type": "DTL" if closing > 0 else ("DTA" if closing < 0 else "none"),
            "by_asset": by_asset}


def render_text(d: dict) -> str:
    o = ["=" * 64, "DEFERRED TAX ROLL-FORWARD", "-" * 64,
         f"  {'asset':<22}{'book':>12}{'tax':>12}{'temp diff':>14}  type"]
    for a in d["by_asset"]:
        o.append(f"  {a['asset'][:20]:<22}{_dec(a['book_basis']):>12,.0f}{_dec(a['tax_basis']):>12,.0f}"
                 f"{_dec(a['temp_diff']):>14,.2f}  {a['type']}")
    o += ["-" * 64,
          f"  cumulative temp difference {d['cumulative_temp_diff']:>26,.2f}",
          f"  opening deferred-tax balance{d['opening_balance']:>25,.2f}",
          f"  closing deferred-tax balance ({d['type']}){_dec(d['closing_balance']):>18,.2f}",
          f"  period movement (deferred tax expense){_dec(d['movement']):>17,.2f}",
          f"  → provision --temporary {d['period_temporary_diff']:>29,.2f}", "=" * 64]
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-deferred-tax")
    ap.add_argument("items", help="JSON file/'-' : [{asset, book_basis, tax_basis}, ...]")
    ap.add_argument("--rate", required=True, help="tax rate (21 or 0.21)")
    ap.add_argument("--prior", default="0", help="opening deferred-tax balance (prior period closing)")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.items == "-" else Path(a.items).read_text(encoding="utf-8")
    items = json.loads(raw)
    d = deferred_rollforward(items, a.rate, prior=a.prior)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
