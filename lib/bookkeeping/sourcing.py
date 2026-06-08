#!/usr/bin/env python3
"""GLAW sales-factor sourcing — assign each sale to a state for the apportionment sales factor.

- Market-based sourcing (most states now): a sale of a service/intangible is sourced to where the
  customer receives the benefit (the market). Sales of tangible goods are sourced to the ship-to
  state (destination).
- Cost-of-performance (older / minority): a service is sourced to where the income-producing
  activity is performed (often all-or-nothing to the state with the greater cost).
- Throwback rule: a sale shipped to a state where the seller is NOT taxable (no nexus) is "thrown
  back" into the origin state's numerator (so it is taxed somewhere). Throwout instead removes it
  from the denominator. Supply the set of states where the seller has nexus.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

_CENT = Decimal("0.01")
_PCT = Decimal("0.0001")


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _qp(d): return Decimal(str(d)).quantize(_PCT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def source_sales(sales: list, *, home_state, nexus_states=None, throwback=True, method="market") -> dict:
    """sales: [{amount, market_state (or ship_to), performance_state}]. Returns the sales factor
    numerator by state after market/COP sourcing + throwback to home_state."""
    nexus = set(nexus_states or [home_state])
    by_state = defaultdict(lambda: Decimal("0"))
    total = Decimal("0")
    for s in sales:
        amt = _dec(s.get("amount", 0))
        total += amt
        dest = s.get("market_state") if method == "market" else s.get("performance_state")
        dest = dest or s.get("ship_to") or home_state
        if dest not in nexus and throwback:
            dest = home_state                        # thrown back to the origin state
        by_state[dest] += amt
    home_num = by_state.get(home_state, Decimal("0"))
    factor = (home_num / total) if total else Decimal("0")
    return {"method": method, "throwback": throwback, "total_sales": str(_q(total)),
            "by_state": {k: str(_q(v)) for k, v in sorted(by_state.items())},
            "home_state": home_state, "home_numerator": str(_q(home_num)),
            "sales_factor_pct": str(_qp(factor * 100))}


def render_text(d: dict) -> str:
    o = ["=" * 56, f"SALES SOURCING ({d['method']}, throwback={d['throwback']})", "-" * 56]
    for st, v in d["by_state"].items():
        o.append(f"  {st:<6} {_dec(v):>16,.2f}")
    o += ["-" * 56,
          f"  {d['home_state']} sales factor: {d['sales_factor_pct']}%", "=" * 56]
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-sourcing")
    ap.add_argument("sales", help="JSON file/'-': [{amount, market_state|ship_to, performance_state}]")
    ap.add_argument("--home-state", required=True)
    ap.add_argument("--nexus-states", default=None, help="comma-separated")
    ap.add_argument("--method", default="market", choices=["market", "cop"])
    ap.add_argument("--no-throwback", action="store_true")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.sales == "-" else Path(a.sales).read_text(encoding="utf-8")
    d = source_sales(json.loads(raw), home_state=a.home_state,
                     nexus_states=(a.nexus_states.split(",") if a.nexus_states else None),
                     throwback=not a.no_throwback, method=a.method)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
