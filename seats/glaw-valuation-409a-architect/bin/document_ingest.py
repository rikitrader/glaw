#!/usr/bin/env python3
"""Source-document intake helper for the 409A architect seat.

Stdlib-only. Converts supplied cap-table / grant-ledger / financing CSVs and
document paths into an intake patch plus a source checklist. It does not replace
legal review; it makes missing evidence visible before valuation math runs.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def _rows(path):
    if not path:
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [{k.strip().lower(): v.strip() for k, v in row.items()} for row in csv.DictReader(f)]


def _num(value, default=0.0):
    try:
        return float(str(value).replace(",", "").replace("$", "")) if value not in (None, "") else default
    except ValueError:
        return default


def _pick(row, *names):
    for name in names:
        if name in row and row[name] != "":
            return row[name]
    return None


def cap_table_patch(path):
    rows = _rows(path)
    shares = {"common": 0, "option_pool": 0, "warrants": 0, "preferred": []}
    for row in rows:
        security = (_pick(row, "security_type", "type", "class", "security") or "").lower()
        name = _pick(row, "name", "series", "security", "holder") or "Security"
        count = _num(_pick(row, "shares", "share_count", "as_converted_shares"))
        if "preferred" in security or "series" in name.lower():
            shares["preferred"].append({
                "name": name,
                "shares": count,
                "invested": _num(_pick(row, "invested", "original_issue_amount", "amount")),
                "liquidation_multiple": _num(_pick(row, "liquidation_multiple", "liq_multiple"), 1.0),
                "seniority": int(_num(_pick(row, "seniority"), 0)),
                "participating": str(_pick(row, "participating") or "false").lower() in {"true", "yes", "1"},
                "participation_cap": None,
                "conversion_ratio": _num(_pick(row, "conversion_ratio"), 1.0),
            })
        elif "option" in security or "pool" in security:
            shares["option_pool"] += count
        elif "warrant" in security:
            shares["warrants"] += count
        else:
            shares["common"] += count
    return shares


def financing_rounds_patch(path):
    rounds = []
    for row in _rows(path):
        rounds.append({
            "round": _pick(row, "round", "series", "name") or "Priced round",
            "date": _pick(row, "date", "closing_date"),
            "price_per_share": _num(_pick(row, "price_per_share", "pps"), None),
            "amount": _num(_pick(row, "amount", "investment"), None),
            "post_money": _num(_pick(row, "post_money", "post_money_valuation"), None),
        })
    return rounds


def option_ledger_controls(path):
    rows = _rows(path)
    controls = {
        "option_grant_dates_confirmed": bool(rows),
        "option_exercise_price_fmv_on_grant_date": bool(rows),
    }
    warnings = []
    for row in rows:
        if not _pick(row, "grant_date", "date"):
            controls["option_grant_dates_confirmed"] = False
            warnings.append(f"Option grant missing date: {row}")
        if _num(_pick(row, "exercise_price", "strike_price"), -1) < 0:
            controls["option_exercise_price_fmv_on_grant_date"] = False
            warnings.append(f"Option grant missing exercise price: {row}")
    return controls, warnings


def doc_exists(path):
    return bool(path and Path(path).exists())


def main():
    ap = argparse.ArgumentParser(description="409A source-document intake helper")
    ap.add_argument("--cap-table-csv")
    ap.add_argument("--option-ledger-csv")
    ap.add_argument("--financing-rounds-csv")
    ap.add_argument("--board-minutes")
    ap.add_argument("--award-agreements")
    ap.add_argument("--out", default="intake_patch.json")
    ap.add_argument("--checklist", default="source_checklist.json")
    args = ap.parse_args()

    patch = {"review_controls": {}}
    warnings = []
    sources = {}

    if args.cap_table_csv:
        patch["shares"] = cap_table_patch(args.cap_table_csv)
        patch["review_controls"]["cap_table_source_attached"] = True
        sources["cap_table_csv"] = args.cap_table_csv
    if args.financing_rounds_csv:
        patch["financing_rounds"] = financing_rounds_patch(args.financing_rounds_csv)
        sources["financing_rounds_csv"] = args.financing_rounds_csv
    if args.option_ledger_csv:
        controls, option_warnings = option_ledger_controls(args.option_ledger_csv)
        patch["review_controls"].update(controls)
        warnings.extend(option_warnings)
        sources["option_ledger_csv"] = args.option_ledger_csv

    patch["review_controls"]["board_approval_planned"] = doc_exists(args.board_minutes)
    patch["review_controls"]["rsu_documents_reviewed"] = doc_exists(args.award_agreements)

    checklist = {
        "sources": sources,
        "documents": {
            "board_minutes": {"path": args.board_minutes, "present": doc_exists(args.board_minutes)},
            "award_agreements": {"path": args.award_agreements, "present": doc_exists(args.award_agreements)},
        },
        "warnings": warnings,
        "next_steps": [
            "Merge intake_patch.json into intake.json and run valuation_engine.py validate.",
            "Resolve every false review_controls item before relying on the memo.",
        ],
    }

    Path(args.out).write_text(json.dumps(patch, indent=2), encoding="utf-8")
    Path(args.checklist).write_text(json.dumps(checklist, indent=2), encoding="utf-8")
    print(json.dumps({"wrote": [args.out, args.checklist], "warnings": warnings}, indent=2))


if __name__ == "__main__":
    main()
