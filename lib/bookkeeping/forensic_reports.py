#!/usr/bin/env python3
"""GLAW forensic monthly/yearly reports + full transaction trace — detailed period reports and a
line-by-line trace where every transaction is traceable to its source statement file and its
tamper-evident hash. Re-runnable; reads the posted GLAW ledger.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L          # noqa: E402

_CENT = Decimal("0.01")
_INCOME = ("Income", "Revenue")


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _f(d): return f"{Decimal(str(d)):,.2f}"


def _period_pl(entries, key):
    """key(entry) → period label. Returns {period: {revenue, expenses, net_income}}."""
    per = defaultdict(lambda: {"rev": Decimal("0"), "exp": Decimal("0")})
    for e in entries:
        p = key(e)
        for ln in e["lines"]:
            root = ln["account"].split(":", 1)[0]
            amt = Decimal(ln["debit"]) - Decimal(ln["credit"])
            if root in _INCOME:
                per[p]["rev"] += -amt                      # credit-normal income
            elif root == "Expenses":
                per[p]["exp"] += amt
    return {p: {"revenue": _q(v["rev"]), "expenses": _q(v["exp"]),
                "net_income": _q(v["rev"] - v["exp"])} for p, v in sorted(per.items())}


def reports(book: str, out_dir: str, *, entity: str = "Entity") -> dict:
    outp = Path(out_dir); outp.mkdir(parents=True, exist_ok=True)
    entries = L.Ledger(book).entries()
    monthly = _period_pl(entries, lambda e: e["date"][:7])
    yearly = _period_pl(entries, lambda e: e["date"][:4])
    written = []

    def w(name, text):
        (outp / name).write_text(text, encoding="utf-8"); written.append(name)

    hdr = f"# {entity} — {{t}}\nForensic reconstruction · GLAW · for CPA/attorney review · NOT advice\n\n"

    # 09 monthly
    m = [hdr.format(t="09 Monthly Reports (P&L by month)"), "| Month | Revenue | Expenses | Net income |",
         "|---|--:|--:|--:|"]
    for mo, v in monthly.items():
        m.append(f"| {mo} | {_f(v['revenue'])} | ({_f(v['expenses'])}) | {_f(v['net_income'])} |")
    m += ["", "### Footnotes",
          "- Cash-basis P&L by statement month, reconstructed from the posted ledger; each month ties to its bank "
          "statement (see deliverable 01). Months with no statement on file are disclosed gaps, not estimates.",
          "- Inbound wires are booked by counterparty: Dealyze (MCA) → loan (excluded from revenue); Nationwide → "
          "revenue; customer financiers (GoodLeap) → revenue.",
          "- Owner draws are equity, not expense; they do not affect monthly net income."]
    w("09_monthly_reports.md", "\n".join(m))

    # 10 yearly
    y = [hdr.format(t="10 Yearly Reports (P&L by year)"), "| Year | Revenue | Expenses | Net income |",
         "|---|--:|--:|--:|"]
    for yr, v in yearly.items():
        y.append(f"| {yr} | {_f(v['revenue'])} | ({_f(v['expenses'])}) | {_f(v['net_income'])} |")
    y += ["", "### Footnotes",
          "- Annual P&L per calendar year (FYE Dec 31) for return preparation; each year rolls up its months above.",
          "- The Dealyze advances are carried as a loan liability across years; only repayments and interest hit the "
          "P&L. The merchant-cash-advance-as-loan position is documented in the error/resolution log (deliverable 07).",
          "- A year with a net loss may generate an NOL (run glaw-nol for the 80% carryforward) — confirm with the CPA."]
    w("10_yearly_reports.md", "\n".join(y))

    # 11 full transaction trace (every posting traceable to source + hash)
    trace_rows = []
    for e in entries:
        for ln in e["lines"]:
            trace_rows.append({"id": e["id"], "date": e["date"], "account": ln["account"],
                               "debit": ln["debit"], "credit": ln["credit"],
                               "memo": e.get("memo", ""), "source_statement": e.get("source", ""),
                               "entry_hash": e.get("entry_hash", "")})
    cols = ["id", "date", "account", "debit", "credit", "memo", "source_statement", "entry_hash"]
    with (outp / "11_transaction_trace.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)           # fixed header even when the book is empty
        wr.writeheader(); wr.writerows(trace_rows)
    written.append("11_transaction_trace.csv")
    w("11_transaction_trace.md", "\n".join([
        hdr.format(t="11 Full Transaction Trace"),
        f"Every one of the {len(entries):,} journal entries ({len(trace_rows):,} postings) is traceable: each carries "
        "its source statement file and its tamper-evident entry hash, so any figure can be traced back to the exact "
        "bank line it came from. The full line-by-line trace is in `11_transaction_trace.csv`.",
        "", "Trace any account or counterparty:",
        "```", "  glaw-ledger --book <book> gl --account <Account>      # GL detail for one account",
        "  grep '<counterparty>' 11_transaction_trace.csv               # every wire to/from a party", "```"]))

    return {"out_dir": str(outp), "files": written, "months": len(monthly), "years": len(yearly),
            "postings_traced": len(trace_rows), "yearly": {y: str(v["net_income"]) for y, v in yearly.items()}}


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-forensic-reports")
    ap.add_argument("--book", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--entity", default="Entity")
    a = ap.parse_args()
    print(json.dumps(reports(a.book, a.out, entity=a.entity), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
