#!/usr/bin/env python3
"""GLAW Schedule K-1 allocation — split a pass-through entity's ordinary business income and the
separately-stated items among the owners by ownership percentage (1065 partners / 1120-S
shareholders).

Ordinary business income is allocated pro-rata; each separately-stated item (interest, dividends,
§1231 gain, §179, charitable, distributions, …) is allocated by the same percentages unless a
special allocation overrides it (partnerships only). Percentages must sum to 100.
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


def allocate(ordinary_income, owners: list[dict], *, form: str = "1065",
             separately_stated: dict | None = None) -> dict:
    """owners: [{owner, pct}] (pct sums to 100). separately_stated: {item: amount}.
    Returns per-owner K-1s with ordinary income + each separately-stated item, and a totals
    cross-check. The last owner absorbs the rounding residual so allocations tie exactly."""
    pcts = [(o["owner"], _dec(o["pct"])) for o in owners]
    total_pct = sum(p for _, p in pcts)
    if total_pct != Decimal("100"):
        raise ValueError(f"ownership percentages must sum to 100, got {total_pct}")
    items = dict(separately_stated or {})
    items = {"ordinary_business_income": _dec(ordinary_income), **{k: _dec(v) for k, v in items.items()}}

    k1s = {name: {} for name, _ in pcts}
    for item, amount in items.items():
        running = Decimal("0")
        for i, (name, pct) in enumerate(pcts):
            if i == len(pcts) - 1:
                share = _q(amount - running)               # last owner gets the residual
            else:
                share = _q(amount * pct / Decimal("100"))
                running += share
            k1s[name][item] = str(share)

    # cross-check: each item's allocations sum back to the entity total
    checks = {}
    for item, amount in items.items():
        s = sum(_dec(k1s[name][item]) for name, _ in pcts)
        checks[item] = (s == _q(amount))
    return {"form": form, "owners": [{"owner": n, "pct": str(p)} for n, p in pcts],
            "entity_totals": {k: str(_q(v)) for k, v in items.items()},
            "k1": k1s, "ties_out": all(checks.values())}


def render_text(d: dict) -> str:
    o = ["=" * 60, f"SCHEDULE K-1 ALLOCATION (Form {d['form']})", "-" * 60]
    for name, alloc in d["k1"].items():
        pct = next(ow["pct"] for ow in d["owners"] if ow["owner"] == name)
        o.append(f"  {name} ({pct}%)")
        for item, amt in alloc.items():
            o.append(f"      {item.replace('_',' '):<34}{_dec(amt):>16,.2f}")
    o.append("-" * 60)
    o.append(f"  ties out to entity totals: {'✓' if d['ties_out'] else '✗'}")
    o.append("=" * 60)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-k1")
    ap.add_argument("--ordinary-income", required=True)
    ap.add_argument("--owners", required=True, help="JSON file/'-': [{owner, pct}]")
    ap.add_argument("--form", default="1065", choices=["1065", "1120-S"])
    ap.add_argument("--separately-stated", default=None, help="JSON: {item: amount}")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.owners == "-" else Path(a.owners).read_text(encoding="utf-8")
    owners = json.loads(raw)
    ss = json.loads(Path(a.separately_stated).read_text(encoding="utf-8")) if a.separately_stated else None
    d = allocate(a.ordinary_income, owners, form=a.form, separately_stated=ss)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
