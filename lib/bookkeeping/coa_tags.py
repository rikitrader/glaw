#!/usr/bin/env python3
"""GLAW chart-of-accounts tags — type, current/non-current, and cash-flow category.

A flat ledger carries no current/non-current or cash-flow tag, so the dashboard and the
direct cash flow fall back to keyword heuristics. This module assigns every account three
tags — deterministically and overridably — so liquidity ratios and the INDIRECT cash-flow
statement become exact:

  type      asset | liability | equity | income | expense        (by account root)
  current   True/False/None  (None for income/expense)
  cashflow  operating | investing | financing | cash             (for the BS-change buckets)

Overrides come from a chart tags file (charts/<name>.tags.json): a list of
{"match": "<account prefix>", "current": bool, "cashflow": "..."} — longest prefix wins.
"""
from __future__ import annotations

import json
from pathlib import Path

CHARTS = Path(__file__).parent / "charts"

_TYPE_BY_ROOT = {"Assets": "asset", "Liabilities": "liability", "Equity": "equity",
                 "Income": "income", "Revenue": "income", "Expenses": "expense"}

# keyword → tag, evaluated on the lowercased account path
_CASH = ("bank", "cash")
_CUR_ASSET = ("receivable", ":ar", "inventory", "prepaid", "accrued revenue")
_ACCUM_DEP = ("accumulated dep", "accum dep", "accumulated depreciation")
_CUR_LIAB = ("payable", ":ap", "accrued", "deferred revenue", "tax payable", "card", "short-term", "current portion")
_FINANCING_LIAB = ("loan", "note payable", "long-term", "long term", "bond", "mortgage", "line of credit")


def load_chart_tags(name: str | None) -> list[dict]:
    if not name:
        return []
    p = CHARTS / f"{name}.tags.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    rules = data.get("accounts", data) if isinstance(data, dict) else data
    return sorted(rules, key=lambda r: -len(r.get("match", "")))   # longest prefix first


def classify(account: str, overrides: list[dict] | None = None) -> dict:
    root = account.split(":", 1)[0]
    typ = _TYPE_BY_ROOT.get(root, "unclassified")
    a = account.lower()
    # explicit override wins (longest prefix)
    for r in (overrides or []):
        if account.startswith(r.get("match", "\0")):
            return {"type": typ,
                    "current": r.get("current"),
                    "cashflow": r.get("cashflow", _default_cashflow(typ, a))}
    # defaults
    if typ == "asset":
        current = any(k in a for k in _CASH + _CUR_ASSET)
    elif typ == "liability":
        current = any(k in a for k in _CUR_LIAB) and not any(k in a for k in _FINANCING_LIAB)
    else:
        current = None
    return {"type": typ, "current": current, "cashflow": _default_cashflow(typ, a)}


def _default_cashflow(typ: str, a: str) -> str:
    if typ in ("income", "expense"):
        return "operating"
    if typ == "asset":
        if any(k in a for k in _CASH):
            return "cash"
        if any(k in a for k in _ACCUM_DEP):
            return "operating"          # depreciation addback
        if any(k in a for k in _CUR_ASSET):
            return "operating"          # working capital
        return "investing"              # fixed assets / investments
    if typ == "liability":
        if any(k in a for k in _FINANCING_LIAB):
            return "financing"
        return "operating"              # AP / accrued / deferred revenue / tax payable
    if typ == "equity":
        return "financing"
    return "operating"
