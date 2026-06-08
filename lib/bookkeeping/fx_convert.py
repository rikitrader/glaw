#!/usr/bin/env python3
"""GLAW FX conversion — true multi-currency double-entry with REALIZED FX gain/loss.

Converting a foreign-currency balance (e.g. EUR) into the reporting currency (or another
currency) at a rate that differs from the rate it was CARRIED at realizes an FX gain or loss.
This books that conversion as one balanced journal entry, in reporting-currency terms:

  carrying value = foreign amount × carrying rate      (what the source was on the books at)
  proceeds       = foreign amount × conversion rate    (what you received)
  realized FX    = proceeds − carrying value            (gain if the rate moved in your favor)

  Dr  to-account            proceeds            (reporting; fx_amount = proceeds)
      Cr  from-account       carrying value      (reporting value removed; fx_amount = foreign amount)
      Cr  Income:Realized FX Gain   realized     (gain)   — or  Dr Expenses:Realized FX Loss
The debit/credit are reporting-currency values (so the entry balances), and each foreign leg
carries `fx_amount` so per-currency balances track the foreign amount, not the reporting value.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def convert(*, from_account: str, from_amount: Decimal, from_currency: str,
            carrying_rate: Decimal, to_account: str, conversion_rate: Decimal,
            reporting: str = "USD", to_currency: str | None = None, date: str = "",
            gain_account: str = "Income:Realized FX Gain",
            loss_account: str = "Expenses:Realized FX Loss") -> dict:
    to_currency = to_currency or reporting
    carrying = _q(from_amount * carrying_rate)
    proceeds = _q(from_amount * conversion_rate)
    realized = _q(proceeds - carrying)
    lines = [
        {"account": to_account, "debit": str(proceeds), "credit": "0",
         "currency": to_currency, "fx_amount": str(proceeds)},
        {"account": from_account, "debit": "0", "credit": str(carrying),
         "currency": from_currency, "fx_amount": str(_q(from_amount))},
    ]
    if realized > 0:
        lines.append({"account": gain_account, "debit": "0", "credit": str(realized)})
    elif realized < 0:
        lines.append({"account": loss_account, "debit": str(_q(-realized)), "credit": "0"})
    entry = {"date": date, "source": "fx-convert",
             "memo": f"FX convert {_q(from_amount):,.2f} {from_currency} @ {conversion_rate} "
                     f"(carried @ {carrying_rate})",
             "lines": lines}
    return {"carrying_value": carrying, "proceeds": proceeds,
            "realized_fx": realized, "result": "gain" if realized > 0 else ("loss" if realized < 0 else "none"),
            "entry": entry}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "FX CONVERSION (realized)", "-" * 56,
        f"  carrying value {d['carrying_value']:>16,.2f}",
        f"  proceeds       {d['proceeds']:>16,.2f}",
        f"  realized {d['result']:<6}{d['realized_fx']:>16,.2f}",
        "-" * 56,
        "  entry (reporting-balanced):",
        *[f"    {l['account'][:34]:<36}"
          f"{'Dr ' + str(_dec(l['debit'])) if _dec(l['debit']) else 'Cr ' + str(_dec(l['credit']))}"
          + (f"  [{l['fx_amount']} {l['currency']}]" if l.get('fx_amount') else "")
          for l in d["entry"]["lines"]],
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-fx-convert")
    ap.add_argument("--from-account", required=True)
    ap.add_argument("--from-amount", required=True, help="foreign amount being converted")
    ap.add_argument("--from-currency", required=True)
    ap.add_argument("--carrying-rate", required=True, help="reporting per foreign — the booked rate")
    ap.add_argument("--to-account", required=True)
    ap.add_argument("--conversion-rate", required=True, help="reporting per foreign — the rate achieved")
    ap.add_argument("--reporting", default="USD")
    ap.add_argument("--to-currency", default=None)
    ap.add_argument("--date", default="")
    ap.add_argument("--book", default=None, help="post the entry to this ledger book (else print)")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = convert(from_account=a.from_account, from_amount=_dec(a.from_amount),
                from_currency=a.from_currency, carrying_rate=_dec(a.carrying_rate),
                to_account=a.to_account, conversion_rate=_dec(a.conversion_rate),
                reporting=a.reporting, to_currency=a.to_currency, date=a.date)
    if a.book:
        import ledger as L
        if not d["entry"]["date"]:
            from datetime import date as _date
            d["entry"]["date"] = _date.today().isoformat()
        res = L.Ledger(a.book).post(d["entry"])
        print(f"posted FX conversion entry #{res.get('id')}  realized {d['result']} {d['realized_fx']:,.2f}")
    elif a.format == "json":
        print(json.dumps(d, indent=2, default=str))
    else:
        print(render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
