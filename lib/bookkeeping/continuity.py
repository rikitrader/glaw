#!/usr/bin/env python3
"""GLAW statement continuity — the audit completeness gate.

A real audit's completeness assertion requires that each account's statements form a
gap-free chain: every statement's opening balance equals the prior statement's closing
balance, and no periods are missing. This checks that chain per account from the
per-statement metadata surfaced by ingest (opening/closing/period). A break or a gap means
a statement is missing or mis-keyed — caught here instead of producing "balanced but
incomplete" books.

Input: a list of statement records, each
  {"account": "...", "period_start": "YYYY-MM-DD", "period_end": "...",
   "opening_balance": "...", "closing_balance": "...", "balance_status": "verified"}
Run by the /glaw-reconstruct workflow, not as a standalone command.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from decimal import Decimal


def _dec(v):
    try:
        return Decimal(str(v))
    except Exception:
        return None


def check(records: list[dict], *, gap_tolerance_days: int = 5) -> dict:
    by_acct: dict[str, list] = {}
    for r in records:
        by_acct.setdefault(r.get("account") or "(unknown)", []).append(r)
    accounts, all_ok = [], True
    for acct, recs in by_acct.items():
        recs = sorted(recs, key=lambda r: str(r.get("period_start") or r.get("period_end") or ""))
        breaks, gaps, unverified = [], [], []
        for i, r in enumerate(recs):
            if r.get("balance_status") not in (None, "verified"):
                unverified.append({"period_start": r.get("period_start"), "status": r.get("balance_status")})
            if i == 0:
                continue
            prev = recs[i - 1]
            po, pc = _dec(prev.get("closing_balance")), _dec(r.get("opening_balance"))
            if po is not None and pc is not None and po != pc:
                breaks.append({"between": [prev.get("period_end"), r.get("period_start")],
                               "prior_closing": str(po), "opening": str(pc),
                               "difference": str(pc - po)})
            # gap: this statement should start ~right after the prior ends
            try:
                pe = date.fromisoformat(str(prev.get("period_end"))[:10])
                cs = date.fromisoformat(str(r.get("period_start"))[:10])
                if (cs - pe).days > gap_tolerance_days + 1:
                    gaps.append({"after": prev.get("period_end"), "next": r.get("period_start"),
                                 "gap_days": (cs - pe).days})
            except Exception:
                pass
        ok = not breaks and not gaps and not unverified
        all_ok = all_ok and ok
        accounts.append({"account": acct, "statements": len(recs), "continuous": ok,
                         "breaks": breaks, "gaps": gaps, "unverified": unverified})
    return {"accounts": accounts, "complete": all_ok}


def render_text(d: dict) -> str:
    o = ["=" * 64, "STATEMENT CONTINUITY (audit completeness)", "-" * 64]
    for a in d["accounts"]:
        mark = "✓" if a["continuous"] else "✗"
        o.append(f"  {mark} {a['account']:<34} {a['statements']} statements")
        for b in a["breaks"]:
            o.append(f"      ✗ balance break {b['between']}: prior close {b['prior_closing']} ≠ open {b['opening']} (Δ {b['difference']})")
        for g in a["gaps"]:
            o.append(f"      ✗ period gap after {g['after']} → {g['next']} ({g['gap_days']} days)")
        for u in a["unverified"]:
            o.append(f"      ✗ statement {u['period_start']} Golden-Rule {u['status']}")
    o.append("-" * 64)
    o.append("  ✅ COMPLETE — every account's statements chain with no gaps"
             if d["complete"] else "  ❌ INCOMPLETE — missing/mis-keyed statements above")
    o.append("=" * 64)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-continuity")
    ap.add_argument("records", nargs="?", default="-", help="statement records JSON (or '-')")
    ap.add_argument("--gap-tolerance", type=int, default=5)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.records in (None, "-") else open(a.records, encoding="utf-8").read()
    recs = json.loads(raw)
    if isinstance(recs, dict) and "records" in recs:
        recs = recs["records"]
    d = check(recs, gap_tolerance_days=a.gap_tolerance)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0 if d["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
