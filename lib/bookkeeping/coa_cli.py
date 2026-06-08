#!/usr/bin/env python3
"""glaw-coa — chart-of-accounts validation and ledger classification check.

  validate <chart.json>   — check a chart-of-accounts mapping (the {default, rules} format):
                            every account resolves to a known root, no empty patterns,
                            warns if the default is Uncategorized. Lists the accounts.
  check-ledger --book B    — scan a posted book for unclassified accounts and
                            Uncategorized leakage (a mapping gap = an audit finding).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import statements as S      # noqa: E402
import ledger as L          # noqa: E402

ROOTS = ("Assets", "Liabilities", "Equity", "Income", "Revenue", "Expenses")


def validate_chart(chart: dict) -> dict:
    errors, warns, accounts = [], [], set()
    if not isinstance(chart.get("rules"), list):
        errors.append("chart must have a 'rules' array")
        return {"ok": False, "errors": errors, "warnings": warns, "accounts": []}
    default = chart.get("default", "Expenses:Uncategorized")
    if "Uncategorized" in default:
        warns.append(f"default account is '{default}' — uncategorized transactions will leak here")
    seen_patterns = set()
    for i, r in enumerate(chart["rules"]):
        pat = (r.get("pattern") or "").strip()
        acct = (r.get("account") or "").strip()
        if not pat:
            errors.append(f"rule {i}: empty pattern")
        if not acct:
            errors.append(f"rule {i}: empty account")
            continue
        resolved = S._resolve_contra(acct)
        accounts.add(resolved)
        if resolved.split(":", 1)[0] not in ROOTS:
            errors.append(f"rule {i}: account '{acct}' has no recognized root (resolved '{resolved}')")
        if pat in seen_patterns:
            warns.append(f"rule {i}: duplicate pattern '{pat}' (earlier rule wins)")
        seen_patterns.add(pat)
    return {"ok": not errors, "errors": errors, "warnings": warns,
            "accounts": sorted(accounts), "rule_count": len(chart["rules"])}


def check_ledger(book: str) -> dict:
    led = L.Ledger(book)
    bal = led.balances()
    unclassified = sorted(a for a, b in bal.items()
                          if a.split(":", 1)[0] not in ROOTS and b != 0)
    uncategorized = sorted(a for a, b in bal.items() if "Uncategorized" in a and b != 0)
    return {"book": book, "accounts": len(bal),
            "unclassified": unclassified, "uncategorized_leakage": uncategorized,
            "clean": not unclassified and not uncategorized}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-coa")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("validate"); p.add_argument("chart"); p.add_argument("--format", default="text", choices=["text", "json"])
    p = sub.add_parser("check-ledger"); p.add_argument("--book", default="default")
    p.add_argument("--format", default="text", choices=["text", "json"])
    p = sub.add_parser("tags"); p.add_argument("--book", default=None)
    p.add_argument("--chart", default=None, help="chart tags name")
    p.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()

    if a.cmd == "tags":
        import coa_tags as T
        ov = T.load_chart_tags(a.chart)
        accounts = sorted(L.Ledger(a.book).balances()) if a.book else sorted({r["match"] for r in ov})
        rows = [{"account": acc, **T.classify(acc, ov)} for acc in accounts]
        if a.format == "json":
            print(json.dumps(rows, indent=2)); return 0
        print(f"  {'Account':<40}{'Type':<12}{'Current':<9}{'Cash flow'}")
        for r in rows:
            print(f"  {r['account'][:39]:<40}{r['type']:<12}{str(r['current']):<9}{r['cashflow']}")
        return 0

    if a.cmd == "validate":
        res = validate_chart(json.load(open(a.chart, encoding="utf-8")))
        if a.format == "json":
            print(json.dumps(res, indent=2)); return 0 if res["ok"] else 1
        print(f"chart: {a.chart}  ({res.get('rule_count', 0)} rules, {len(res['accounts'])} accounts)")
        for e in res["errors"]:
            print(f"  ❌ {e}")
        for w in res["warnings"]:
            print(f"  ⚠️  {w}")
        print(f"  {'✅ chart valid' if res['ok'] else '❌ invalid'}")
        return 0 if res["ok"] else 1

    res = check_ledger(a.book)
    if a.format == "json":
        print(json.dumps(res, indent=2)); return 0 if res["clean"] else 1
    print(f"book '{a.book}': {res['accounts']} accounts")
    for u in res["unclassified"]:
        print(f"  ❌ unclassified account: {u}")
    for u in res["uncategorized_leakage"]:
        print(f"  ⚠️  uncategorized leakage: {u}")
    print(f"  {'✅ all accounts classified' if res['clean'] else '❌ classification gaps'}")
    return 0 if res["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
