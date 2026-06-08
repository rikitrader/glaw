#!/usr/bin/env python3
"""GLAW forensic adversarial gate — a REAL, EXECUTABLE red-team that runs the government-enforcement
checks deterministically against the reconstructed ledger, then has the chief produce a resolution
that clears each issue or holds it open. This is the wired adversarial gate, not a reference: it
reads the posted GL, raises every finding an IRS Revenue Agent / forensic accountant / BSA examiner
would raise, applies the client's documented resolutions, and returns AUDIT-READY only when no
critical/high finding is still open.

Run after a reconstruction; re-runnable. Resolutions are supplied in a JSON file the client extends
as each issue is cured, so the gate converges to AUDIT-READY as the file gets closed out.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import sys

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L          # noqa: E402
import statements as S      # noqa: E402

_CENT = Decimal("0.01")


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def _finding(fid, lens, severity, issue, authority, exposure, cure):
    return {"id": fid, "lens": lens, "severity": severity, "issue": issue,
            "authority": authority, "exposure": exposure, "cure": cure}


def gap_months(book: str) -> list:
    led = L.Ledger(book)
    months = sorted({e["date"][:7] for e in led.entries()})
    if not months:
        return []
    def span(lo, hi):
        (y0, m0), (y1, m1) = (int(lo[:4]), int(lo[5:7])), (int(hi[:4]), int(hi[5:7]))
        out, y, m = [], y0, m0
        while (y, m) <= (y1, m1):
            out.append(f"{y:04d}-{m:02d}")
            m = 1 if m == 12 else m + 1
            y = y + 1 if m == 1 else y
        return out
    return [m for m in span(months[0], months[-1]) if m not in months]


def red_team(book: str, *, documented_loan_notes="0", job_cost_gross_profit=None) -> list:
    """The enforcement red-team — deterministic checks an IRS RA / forensic / BSA examiner runs."""
    led = L.Ledger(book)
    bal = led.balances()
    entries = led.entries()
    pl = S.build(postings=led.postings())["profit_loss"]
    F = []

    # --- IRS Revenue Agent ---
    loan = -sum((v for a, v in bal.items() if a.startswith("Liabilities:Loans-Payable")), Decimal("0"))
    docd = _dec(documented_loan_notes)
    if loan > docd:
        F.append(_finding("loan_without_note", "IRS Revenue Agent", "CRITICAL",
                          f"loan liability {_q(loan):,.2f} exceeds documented notes {_q(docd):,.2f} "
                          f"(naked {_q(loan - docd):,.2f})",
                          "§61 gross income; §108 COD; Indianapolis Power & Light 493 U.S. 203 (bona-fide debt)",
                          "recharacterization to income → §6662 20% accuracy penalty on the understatement",
                          "produce a note for the full loan or book only the documented amount as debt; "
                          "run the 11-factor bona-fide-debt memo"))
    card = bal.get("Expenses:Operating:Card-POS-Uncategorized", Decimal("0"))
    if card > Decimal("25000"):
        F.append(_finding("unsubstantiated_card", "IRS Revenue Agent", "CRITICAL",
                          f"unsubstantiated card/POS spend {_q(card):,.2f} deducted",
                          "§274(d) strict substantiation (no Cohan estimation for meals/travel/auto)",
                          "full disallowance of the unsupported portion → large understatement",
                          "re-class by merchant; build contemporaneous logs; suspend the unsupportable residue"))
    draw = bal.get("Equity:Owner Draw", Decimal("0"))
    wages = sum((v for a, v in bal.items() if "Wages" in a or "Payroll" in a or "Officer" in a), Decimal("0"))
    if draw > Decimal("0") and wages == 0:
        F.append(_finding("reasonable_comp", "IRS Revenue Agent", "HIGH",
                          f"owner draws {_q(draw):,.2f} with $0 officer wages (S-corp)",
                          "§3121 FICA; Watson v. United States 668 F.3d 1008 (reasonable comp)",
                          "distributions recharacterized to wages → employer+employee FICA + 941 penalties",
                          "reasonable-comp study; file/amend 941 + W-2; reclass part of draws to wages"))
    gaps = gap_months(book)
    if gaps:
        F.append(_finding("missing_months", "IRS Revenue Agent", "HIGH",
                          f"{len(gaps)} missing statement months: {', '.join(gaps)}",
                          "§446(b) reconstruction; §6501(e) 6-yr SOL on >25% omission; Holland 348 U.S. 121",
                          "unreported-income presumption via bank-deposits method; extended statute",
                          "obtain the missing bank statements (they exist) — highest-leverage cure"))

    # --- Forensic accountant ---
    rev, ni = pl["revenue_total"], pl["net_income"]
    if rev > 0 and abs(ni) / rev < Decimal("0.02"):
        msg = f"net income {_q(ni):,.2f} is < 2% of revenue {_q(rev):,.2f} (near-zero result)"
        if job_cost_gross_profit is not None:
            msg += f"; job-cost SOT shows gross profit {_q(_dec(job_cost_gross_profit)):,.2f} — must reconcile"
        F.append(_finding("engineered_loss", "Forensic accountant", "HIGH", msg,
                          "§446(b) clear reflection of income; badges-of-fraud (manufactured result)",
                          "examiner treats a near-zero/engineered result as a fraud indicator → scope expansion",
                          "bridge the job-cost model to the bank-reconstruction P&L in one tie-out schedule"))
    # same-day in/out wash (a deposit and a withdrawal of equal amount on the same date)
    by_day = defaultdict(lambda: {"in": [], "out": []})
    for e in entries:
        for ln in e["lines"]:
            if ln["account"].startswith("Assets:Bank:") and "Clearing" not in ln["account"]:
                if _dec(ln["debit"]) > 0:
                    by_day[e["date"]]["in"].append(_dec(ln["debit"]))
                if _dec(ln["credit"]) > 0:
                    by_day[e["date"]]["out"].append(_dec(ln["credit"]))
    washes = sum(1 for d, v in by_day.items() for a in v["in"] if a >= 50000 and a in v["out"])
    if washes:
        F.append(_finding("same_day_wash", "Forensic accountant", "MEDIUM",
                          f"{washes} same-day in-and-out flow(s) ≥ $50k (money in then back out same day)",
                          "conduit/pass-through forensic marker",
                          "supports recharacterization + BSA conduit concern",
                          "trace each flow to a signed instrument; document the business purpose"))

    # --- BSA examiner: structuring screen on cash ---
    cash_near = 0
    for e in entries:
        for ln in e["lines"]:
            a = ln["account"]
            if "Cash-Withdrawal" in a or ("Owner Draw" in a):
                amt = _dec(ln["debit"])
                if Decimal("9000") <= amt < Decimal("10000"):
                    cash_near += 1
    if cash_near:
        F.append(_finding("structuring", "BSA examiner", "HIGH",
                          f"{cash_near} cash withdrawal(s) in the $9,000–$9,999 band (CTR-evasion pattern)",
                          "31 U.S.C. §5324 structuring (standalone felony); 31 C.F.R. §1010.311 (CTR > $10k)",
                          "criminal referral risk independent of any tax issue",
                          "engage criminal-defense counsel before any IRS contact; document each withdrawal"))
    return F


def chief_resolution(findings: list, resolutions: dict | None = None) -> dict:
    """The chief reviews each red-team finding and either CLEARS it (a documented resolution exists)
    or HOLDS it OPEN. AUDIT-READY only when no CRITICAL/HIGH finding is still open."""
    res = resolutions or {}
    rows = []
    open_critical_high = 0
    for f in findings:
        cleared = f["id"] in res
        status = "CLEARED" if cleared else "OPEN"
        if not cleared and f["severity"] in ("CRITICAL", "HIGH"):
            open_critical_high += 1
        rows.append({**f, "status": status,
                     "resolution": res.get(f["id"], f"[OPEN] {f['cure']}")})
    verdict = "AUDIT-READY" if open_critical_high == 0 else "NOT AUDIT-READY"
    return {"verdict": verdict, "findings_total": len(findings),
            "open_critical_high": open_critical_high, "findings": rows}


def review(book: str, *, documented_loan_notes="0", job_cost_gross_profit=None, resolutions=None) -> dict:
    if isinstance(resolutions, str):
        resolutions = json.loads(Path(resolutions).read_text(encoding="utf-8"))
    F = red_team(book, documented_loan_notes=documented_loan_notes, job_cost_gross_profit=job_cost_gross_profit)
    return chief_resolution(F, resolutions)


def render_text(d: dict) -> str:
    o = ["=" * 70, "FORENSIC ADVERSARIAL GATE — enforcement red-team -> chief resolution", "-" * 70]
    for f in d["findings"]:
        mark = "CLEARED" if f["status"] == "CLEARED" else "OPEN"
        o.append(f"  [{mark}] [{f['severity']}] ({f['lens']}) {f['issue']}")
        o.append(f"       authority: {f['authority']}")
        o.append(f"       resolution: {f['resolution']}")
    o += ["-" * 70,
          f"  open critical/high: {d['open_critical_high']}",
          f"  CHIEF VERDICT: {d['verdict']}", "=" * 70]
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-forensic-adversarial")
    ap.add_argument("--book", required=True)
    ap.add_argument("--documented-loan-notes", default="0", help="$ of loan principal backed by signed notes")
    ap.add_argument("--job-cost-gross-profit", default=None, help="gross profit from the job-costing SOT (tie-out)")
    ap.add_argument("--resolutions", default=None, help="JSON {finding_id: resolution-text} of cleared issues")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = review(a.book, documented_loan_notes=a.documented_loan_notes,
               job_cost_gross_profit=a.job_cost_gross_profit, resolutions=a.resolutions)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0 if d["verdict"] == "AUDIT-READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
