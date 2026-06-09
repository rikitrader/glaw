#!/usr/bin/env python3
"""GLAW Texas child-support guideline calculator (Tex. Fam. Code ch. 154).

Guideline support = the applicable percentage × the obligor's monthly **net resources**, where net
resources are capped (§154.125(a-1)) at an OAG-adjusted ceiling. Percentages (§154.125): 1 child
20%, 2 = 25%, 3 = 30%, 4 = 35%, 5 = 40%, 6+ = not less than 5 children. When the obligor has other
children to support, §154.129 substitutes the multiple-family adjusted percentage table.

This computes the GUIDELINE figure from a given net-resources number; it does NOT derive net
resources from gross (that subtracts SS/Medicare, federal income tax for a single filer claiming
one exemption, state income tax, union dues, and the child's health-insurance cost — route the
build-up to the family-law seat). Texas only; other states route to /glaw-legal-research.

[VERIFY] The net-resources cap is OAG-adjusted for inflation every six years — confirm the current
ceiling (was $9,200/mo) before relying on this. DRAFT for a licensed attorney to verify.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
NET_RESOURCES_CAP = Decimal("9200")        # [VERIFY] §154.125(a-1), OAG-adjusted

# §154.125 single-family guideline %
SINGLE = {1: "20", 2: "25", 3: "30", 4: "35", 5: "40", 6: "40", 7: "40"}

# §154.129 multiple-family adjusted % — rows = children before the court (1-7),
# cols = number of OTHER children the obligor has a duty to support (0-7).
MULTI = {
    1: ["20.00", "17.50", "16.00", "14.75", "13.60", "13.33", "13.14", "13.00"],
    2: ["25.00", "22.50", "20.63", "19.00", "18.33", "17.86", "17.50", "17.22"],
    3: ["30.00", "27.38", "25.20", "24.00", "23.14", "22.50", "22.00", "21.60"],
    4: ["35.00", "32.20", "30.33", "29.00", "28.00", "27.22", "26.60", "26.09"],
    5: ["40.00", "37.33", "35.43", "34.00", "32.89", "32.00", "31.27", "30.67"],
    6: ["40.00", "37.71", "36.00", "34.67", "33.60", "32.73", "32.00", "31.38"],
    7: ["40.00", "38.00", "36.44", "35.20", "34.18", "33.33", "32.62", "32.00"],
}


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def child_support(*, net_resources="0", children="1", other_children="0") -> dict:
    nr = _dec(net_resources)
    n = max(1, min(7, int(_dec(children))))
    other = max(0, min(7, int(_dec(other_children))))
    capped = min(nr, NET_RESOURCES_CAP)
    if other > 0:
        pct = Decimal(MULTI[n][other])
        basis = f"§154.129 multiple-family ({n} before court / {other} other)"
    else:
        pct = Decimal(SINGLE[n])
        basis = f"§154.125 ({n} child{'ren' if n > 1 else ''})"
    monthly = capped * pct / Decimal("100")
    return {
        "state": "TX",
        "net_resources_monthly": str(_q(nr)),
        "net_resources_cap": str(_q(NET_RESOURCES_CAP)),
        "net_resources_applied": str(_q(capped)),
        "children_before_court": n,
        "other_children": other,
        "guideline_percentage": str(pct),
        "percentage_basis": basis,
        "guideline_monthly_support": str(_q(monthly)),
        "guideline_annual_support": str(_q(monthly * 12)),
        "_verify": "net-resources cap is OAG-adjusted [VERIFY]; net resources must be built up from gross "
                   "(minus SS/Medicare, single-filer fed tax, union dues, child health-insurance) — see the "
                   "family-law seat; above-cap or special-needs cases justify deviation under §154.126.",
    }


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 60, "TX CHILD SUPPORT (ch. 154) — GUIDELINE DRAFT", "-" * 60,
        f"  monthly net resources           {_dec(d['net_resources_monthly']):>16,.2f}",
        f"  applied (cap {_dec(d['net_resources_cap']):,.0f})          {_dec(d['net_resources_applied']):>16,.2f}",
        f"  children before court           {d['children_before_court']:>16}",
        f"  other children supported        {d['other_children']:>16}",
        f"  guideline %                     {d['guideline_percentage']:>15}%   [{d['percentage_basis']}]",
        f"  ► GUIDELINE MONTHLY SUPPORT     {_dec(d['guideline_monthly_support']):>16,.2f}",
        f"    (annual                       {_dec(d['guideline_annual_support']):>16,.2f})",
        "=" * 60, f"  ⚠ VERIFY: {d['_verify']}",
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-child-support", description="Texas ch.154 child-support guideline (DRAFT).")
    ap.add_argument("--net-resources", default="0", help="obligor monthly NET resources")
    ap.add_argument("--children", default="1", help="children before the court (1-7)")
    ap.add_argument("--other-children", default="0", help="other children the obligor must support (0-7)")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = child_support(net_resources=a.net_resources, children=a.children, other_children=a.other_children)
    print(json.dumps(d, indent=2) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
