#!/usr/bin/env python3
"""GLAW international information returns — Forms 5471 and 5472 filing determination + the data
checklist + the §6038/§6038A penalty exposure for non-filing.

- Form 5471 (§6038): a U.S. person who is an officer, director, or 10%+ shareholder of a foreign
  corporation. Category of filer (1-5) drives which schedules are required. Penalty: $10,000 per
  form per year (+$10,000/month continuation up to $50,000; plus a 10% FTC reduction).
- Form 5472 (§6038A): a 25%-foreign-owned U.S. corporation, or a foreign corporation engaged in a
  U.S. trade or business, that has reportable transactions with a related party. Penalty: $25,000
  per form per year (+$25,000/month continuation).
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)


def determine(*, us_person_owns_foreign_corp=False, ownership_pct=0, is_officer_or_director=False,
              us_corp_25pct_foreign_owned=False, foreign_corp_us_trade=False,
              has_related_party_transactions=False, years_delinquent=0) -> dict:
    forms = []
    pct = Decimal(str(ownership_pct))
    needs_5471 = us_person_owns_foreign_corp and (pct >= 10 or is_officer_or_director)
    needs_5472 = (us_corp_25pct_foreign_owned or foreign_corp_us_trade) and has_related_party_transactions
    penalty = Decimal("0")
    yrs = int(years_delinquent)
    if needs_5471:
        forms.append({"form": "5471", "authority": "§6038", "per_year_penalty": "10000"})
        penalty += Decimal("10000") * yrs
    if needs_5472:
        forms.append({"form": "5472", "authority": "§6038A", "per_year_penalty": "25000"})
        penalty += Decimal("25000") * yrs
    checklist = {
        "5471": ["category of filer (1-5)", "Sch C income statement", "Sch F balance sheet",
                 "Sch I-1 GILTI/Subpart F", "Sch J E&P", "Sch P PTEP", "functional currency + FX"],
        "5472": ["25% foreign shareholder identity", "reportable transactions by type",
                 "transfer-pricing method", "intercompany agreements"],
    }
    return {"forms_required": forms,
            "required_5471": needs_5471, "required_5472": needs_5472,
            "delinquency_penalty_exposure": str(_q(penalty)),
            "data_checklist": {f["form"]: checklist[f["form"]] for f in forms}}


def render_text(d: dict) -> str:
    o = ["=" * 56, "INTERNATIONAL INFORMATION RETURNS (5471 / 5472)", "-" * 56]
    for f in d["forms_required"]:
        o.append(f"  Form {f['form']} ({f['authority']}) — ${f['per_year_penalty']}/yr if not filed")
    o += [f"  DELINQUENCY PENALTY EXPOSURE {Decimal(d['delinquency_penalty_exposure']):>12,.2f}", "=" * 56]
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-intl-forms")
    ap.add_argument("--us-person-owns-foreign-corp", action="store_true")
    ap.add_argument("--ownership-pct", type=float, default=0)
    ap.add_argument("--is-officer-or-director", action="store_true")
    ap.add_argument("--us-corp-25pct-foreign-owned", action="store_true")
    ap.add_argument("--foreign-corp-us-trade", action="store_true")
    ap.add_argument("--has-related-party-transactions", action="store_true")
    ap.add_argument("--years-delinquent", type=int, default=0)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = determine(us_person_owns_foreign_corp=a.us_person_owns_foreign_corp, ownership_pct=a.ownership_pct,
                  is_officer_or_director=a.is_officer_or_director,
                  us_corp_25pct_foreign_owned=a.us_corp_25pct_foreign_owned,
                  foreign_corp_us_trade=a.foreign_corp_us_trade,
                  has_related_party_transactions=a.has_related_party_transactions,
                  years_delinquent=a.years_delinquent)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
