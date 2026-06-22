#!/usr/bin/env python3
"""Executable reviewer checks for the 409A architect reviewer agents."""
from __future__ import annotations

import argparse
import json


ROLE_CONTROLS = {
    "appraiser": [
        "appraiser_engaged", "valuation_method_reasonable", "valuation_freshness_confirmed",
        "cap_table_source_attached", "material_events_reviewed",
    ],
    "equity-awards-lawyer": [
        "option_grant_dates_confirmed", "option_exercise_price_fmv_on_grant_date",
        "average_price_period_controls", "option_modification_reviewed",
        "dividend_equivalent_rights_reviewed", "rsu_documents_reviewed",
        "rsu_short_term_deferral_checked", "rsu_payment_schedule_409a_compliant",
        "release_timing_reviewed", "legal_counsel_review_required",
    ],
    "auditor-tax": [
        "cap_table_source_attached", "board_approval_planned", "material_events_reviewed",
        "auditor_review_required", "valuation_freshness_confirmed",
    ],
}


def verdict(open_items):
    if not open_items:
        return "CLEAR"
    if len(open_items) <= 2:
        return "CLEAR WITH CONDITIONS"
    return "BLOCKED"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def evaluate(role, results, audit):
    legal = results.get("legal_audit", {})
    controls = legal.get("controls", {})
    warnings = audit.get("warnings", [])
    roles = ROLE_CONTROLS if role == "all" else {role: ROLE_CONTROLS[role]}
    out = {}
    for name, required in roles.items():
        open_items = [key for key in required if not controls.get(key)]
        if name == "appraiser" and any("PWERM diverge" in w or "OPM" in w for w in warnings):
            open_items.append("valuation approach divergence requires appraiser reconciliation")
        out[name] = {
            "verdict": verdict(open_items),
            "open_controls": open_items,
            "warnings_considered": warnings,
        }
    return out


def main():
    ap = argparse.ArgumentParser(description="409A reviewer verdict checker")
    ap.add_argument("--results", required=True)
    ap.add_argument("--audit", required=True)
    ap.add_argument("--role", choices=["appraiser", "equity-awards-lawyer", "auditor-tax", "all"], default="all")
    args = ap.parse_args()
    print(json.dumps(evaluate(args.role, load(args.results), load(args.audit)), indent=2))


if __name__ == "__main__":
    main()
