#!/usr/bin/env python3
"""GLAW penalty-abatement engine — First-Time Abatement (FTA) eligibility and reasonable-cause
scoring, to abate failure-to-file / failure-to-pay / failure-to-deposit penalties (Form 843 /
penalty-relief request).

FTA (IRM 20.1.1.3.3.2.1) applies when the taxpayer has a clean compliance history — no penalties
in the prior three years — all required returns are filed (or on valid extension), and any tax due
is paid or under an arrangement. If FTA is unavailable, reasonable cause is a facts-and-
circumstances test (death/serious illness, casualty, inability to obtain records, reliance on a
competent professional, etc.); the strongest available basis is recommended.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
# reasonable-cause factors → weight (strength contribution)
RC_FACTORS = {
    "death_or_serious_illness": 35, "casualty_fire_natural_disaster": 30,
    "unable_to_obtain_records": 20, "reliance_on_tax_professional": 20,
    "incorrect_irs_advice": 30, "first_time_inadvertent": 10,
    "ordinary_business_care_exercised": 15,
}


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def fta_eligibility(*, penalties_prior_3yr: bool, all_returns_filed: bool,
                    paid_or_arranged: bool) -> dict:
    reasons = []
    if penalties_prior_3yr:
        reasons.append("has penalties in the prior 3 years — not a clean compliance history")
    if not all_returns_filed:
        reasons.append("not all required returns are filed (or on valid extension)")
    if not paid_or_arranged:
        reasons.append("tax due is not paid or under an arrangement")
    eligible = not reasons
    return {"fta_eligible": eligible,
            "reasons_ineligible": reasons,
            "applies_to": ["failure-to-file", "failure-to-pay", "failure-to-deposit"] if eligible else []}


def reasonable_cause_score(factors: list[str], *, narrative: str = "") -> dict:
    score = sum(RC_FACTORS.get(f, 0) for f in factors)
    score = min(score, 100)
    tier = ("strong" if score >= 50 else "moderate" if score >= 25 else "weak" if score > 0 else "none")
    return {"factors": factors, "score": score, "strength": tier,
            "recommend_assert": score >= 25,
            "narrative_provided": bool(narrative)}


def abatement(penalty_amount, *, penalties_prior_3yr=False, all_returns_filed=True,
              paid_or_arranged=True, reasonable_cause_factors=None, narrative="") -> dict:
    amt = _q(_dec(penalty_amount))
    fta = fta_eligibility(penalties_prior_3yr=penalties_prior_3yr,
                          all_returns_filed=all_returns_filed, paid_or_arranged=paid_or_arranged)
    rc = reasonable_cause_score(reasonable_cause_factors or [], narrative=narrative)
    if fta["fta_eligible"]:
        basis, abatable = "First-Time Abatement (FTA)", amt
    elif rc["recommend_assert"]:
        basis, abatable = f"reasonable cause ({rc['strength']})", amt
    else:
        basis, abatable = "no clear basis — gather facts before requesting", Decimal("0.00")
    return {"penalty_amount": str(amt), "fta": fta, "reasonable_cause": rc,
            "recommended_basis": basis, "abatable_amount": str(_q(abatable)),
            "form": "Form 843 (or penalty-relief request)"}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "PENALTY ABATEMENT", "-" * 56,
        f"  penalty amount           {_dec(d['penalty_amount']):>16,.2f}",
        f"  FTA eligible: {d['fta']['fta_eligible']}",
        *[f"    - {r}" for r in d['fta']['reasons_ineligible']],
        f"  reasonable cause: {d['reasonable_cause']['strength']} (score {d['reasonable_cause']['score']})",
        "-" * 56,
        f"  recommended basis: {d['recommended_basis']}",
        f"  abatable amount          {_dec(d['abatable_amount']):>16,.2f}   via {d['form']}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-abatement")
    ap.add_argument("--penalty", required=True)
    ap.add_argument("--prior-penalties", action="store_true", help="had penalties in the prior 3 years")
    ap.add_argument("--returns-not-filed", action="store_true")
    ap.add_argument("--not-paid", action="store_true")
    ap.add_argument("--factors", default=None, help="comma-separated reasonable-cause factors")
    ap.add_argument("--narrative", default="")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    factors = a.factors.split(",") if a.factors else []
    d = abatement(a.penalty, penalties_prior_3yr=a.prior_penalties,
                  all_returns_filed=not a.returns_not_filed, paid_or_arranged=not a.not_paid,
                  reasonable_cause_factors=factors, narrative=a.narrative)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
