#!/usr/bin/env python3
"""GLAW inventory & COGS — FIFO / weighted-average cost.

Given purchase lots and units sold, computes cost of goods sold and ending inventory,
plus the entry (Dr COGS / Cr Inventory). Conservation holds: COGS + ending inventory ==
total cost purchased.

Input JSON: {"method": "fifo"|"wac", "lots": [{"units": 100, "unit_cost": 5.00}, ...],
             "units_sold": 120, "sale_price": 9.00 (optional, for gross margin)}
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def cogs(method: str, lots: list[dict], units_sold: Decimal) -> dict:
    total_units = sum(_dec(l["units"]) for l in lots)
    total_cost = sum(_dec(l["units"]) * _dec(l["unit_cost"]) for l in lots)
    if units_sold > total_units:
        raise SystemExit(f"ERROR: units_sold {units_sold} exceeds units available {total_units}")
    if method == "fifo":
        remaining = units_sold
        cost = Decimal("0")
        for l in lots:                                 # consume oldest first
            u, c = _dec(l["units"]), _dec(l["unit_cost"])
            take = min(u, remaining)
            cost += take * c
            remaining -= take
            if remaining <= 0:
                break
        cogs_amt = _q(cost)
    elif method == "wac":
        avg = (total_cost / total_units) if total_units else Decimal("0")
        cogs_amt = _q(units_sold * avg)
    else:
        raise SystemExit("ERROR: method must be fifo or wac")
    ending = _q(total_cost - cogs_amt)
    return {"method": method, "units_available": total_units, "units_sold": units_sold,
            "units_ending": total_units - units_sold, "total_cost": _q(total_cost),
            "cogs": cogs_amt, "ending_inventory": ending,
            "entry": [{"account": "Expenses:COGS", "debit": str(cogs_amt), "credit": "0"},
                      {"account": "Assets:Inventory", "debit": "0", "credit": str(cogs_amt)}]}


def render_text(d: dict, sale_price: Decimal | None) -> str:
    o = ["=" * 56, f"INVENTORY / COGS ({d['method'].upper()})", "-" * 56,
         f"  units available {d['units_available']:>10}   sold {d['units_sold']:>10}",
         f"  total cost      {d['total_cost']:>14,.2f}",
         f"  COGS            {d['cogs']:>14,.2f}",
         f"  ending inventory{d['ending_inventory']:>14,.2f}"]
    if sale_price:
        rev = _q(_dec(d["units_sold"]) * sale_price)
        gp = rev - d["cogs"]
        o.append(f"  revenue         {rev:>14,.2f}")
        o.append(f"  gross profit    {gp:>14,.2f}  ({gp / rev * 100:.1f}% margin)" if rev else "")
    o.append("=" * 56)
    return "\n".join(x for x in o if x)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-inventory")
    ap.add_argument("json", nargs="?", default="-", help="inventory JSON (or '-')")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.json in (None, "-") else open(a.json, encoding="utf-8").read()
    d = json.loads(raw)
    res = cogs(d.get("method", "fifo"), d.get("lots", []), _dec(d.get("units_sold")))
    sp = _dec(d["sale_price"]) if d.get("sale_price") else None
    print(json.dumps(res, indent=2, default=str) if a.format == "json" else render_text(res, sp))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
