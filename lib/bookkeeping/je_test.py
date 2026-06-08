#!/usr/bin/env python3
"""GLAW journal-entry forensics — SAS-99-style JE tests + Benford's-law digit analysis.

Auditing standards (AU-C 240 / SAS 99) require testing journal entries for fraud. This
runs the standard tests over a posted ledger and a Benford first-digit analysis of the
amounts. Findings are risk indicators to investigate, not conclusions.

JE tests (each entry flagged with the reasons that apply):
  round-dollar      gross amount is an exact multiple of 1,000 at/above a threshold
  weekend           posted with a Saturday/Sunday booking date
  period-end        booked on the first or last day of a month (cut-off risk)
  large             gross amount at/above a large threshold
  rare-account      touches an account used in very few entries
  manual            source = manual (vs system/bank/subledger) — higher inherent risk

Benford's law: leading digits of naturally-occurring amounts follow P(d)=log10(1+1/d).
Reports observed vs expected and the mean absolute deviation (Nigrini bands).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L          # noqa: E402

BENFORD = {d: math.log10(1 + 1 / d) for d in range(1, 10)}
# Nigrini mean-absolute-deviation conformity bands for first-digit test
_MAD_BANDS = [(0.006, "close conformity"), (0.012, "acceptable conformity"),
              (0.015, "marginally acceptable"), (float("inf"), "nonconformity")]


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _gross(entry: dict) -> Decimal:
    return sum(_dec(l.get("debit", 0)) for l in entry["lines"])


def _first_digit(x: Decimal) -> int | None:
    s = str(abs(x)).lstrip("0.")
    for ch in s:
        if ch.isdigit() and ch != "0":
            return int(ch)
    return None


def benford(amounts: list[Decimal]) -> dict:
    digits = [d for d in (_first_digit(a) for a in amounts if a != 0) if d]
    n = len(digits)
    counts = Counter(digits)
    rows, mad = [], 0.0
    for d in range(1, 10):
        obs = counts.get(d, 0) / n if n else 0.0
        exp = BENFORD[d]
        rows.append({"digit": d, "observed": round(obs, 4), "expected": round(exp, 4),
                     "count": counts.get(d, 0)})
        mad += abs(obs - exp)
    mad = mad / 9 if n else 0.0
    band = next(label for thr, label in _MAD_BANDS if mad <= thr)
    return {"n": n, "mad": round(mad, 5), "conformity": band,
            "sufficient_data": n >= 50, "digits": rows}


def scan(book: str, *, round_threshold=Decimal("5000"), large_threshold=Decimal("25000"),
         rare_max: int = 2) -> dict:
    led = L.Ledger(book)
    entries = led.entries()
    acct_use: Counter = Counter()
    for e in entries:
        for l in e["lines"]:
            acct_use[l["account"]] += 1
    findings = []
    for e in entries:
        gross = _gross(e)
        reasons = []
        if gross >= round_threshold and gross % Decimal("1000") == 0:
            reasons.append("round-dollar")
        try:
            d = date.fromisoformat(e["date"])
            if d.weekday() >= 5:
                reasons.append("weekend")
            import calendar
            if d.day == 1 or d.day == calendar.monthrange(d.year, d.month)[1]:
                reasons.append("period-end")
        except Exception:
            pass
        if gross >= large_threshold:
            reasons.append("large")
        if any(acct_use[l["account"]] <= rare_max for l in e["lines"]):
            reasons.append("rare-account")
        if e.get("source", "manual") == "manual":
            reasons.append("manual")
        if reasons:
            findings.append({"id": e["id"], "date": e["date"], "memo": e.get("memo", ""),
                             "gross": str(gross), "reasons": reasons})
    bf = benford([_gross(e) for e in entries] +
                 [_dec(l.get("debit", 0)) for e in entries for l in e["lines"] if _dec(l.get("debit", 0)) > 0])
    return {"book": book, "entries": len(entries), "flagged": len(findings),
            "findings": findings, "benford": bf}


def render_text(s: dict) -> str:
    o = ["=" * 70, f"JOURNAL-ENTRY FORENSICS — {s['book']}", "-" * 70,
         f"  entries: {s['entries']}   flagged: {s['flagged']}", "-" * 70]
    for f in s["findings"][:40]:
        o.append(f"  #{f['id']:<4} {f['date']}  {_dec(f['gross']):>12,.2f}  "
                 f"{', '.join(f['reasons']):<40} {f['memo'][:24]}")
    bf = s["benford"]
    o.append("-" * 70)
    o.append(f"  BENFORD first-digit (n={bf['n']}, MAD={bf['mad']}, {bf['conformity']}"
             + ("" if bf["sufficient_data"] else ", INSUFFICIENT DATA <50") + ")")
    o.append("    digit  observed  expected")
    for r in bf["digits"]:
        o.append(f"      {r['digit']}     {r['observed']:.3f}     {r['expected']:.3f}")
    o.append("=" * 70)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-je-test")
    ap.add_argument("--book", required=True)
    ap.add_argument("--round-threshold", default="5000")
    ap.add_argument("--large-threshold", default="25000")
    ap.add_argument("--strict", action="store_true", help="exit non-zero if anything is flagged")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    s = scan(a.book, round_threshold=Decimal(a.round_threshold), large_threshold=Decimal(a.large_threshold))
    print(json.dumps(s, indent=2, default=str) if a.format == "json" else render_text(s))
    return 1 if (a.strict and s["flagged"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
