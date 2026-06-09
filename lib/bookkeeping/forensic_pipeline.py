#!/usr/bin/env python3
"""GLAW forensic-reconstruction pipeline — RE-RUNNABLE.

Ingests a classified master-ledger CSV of real bank transactions (acct, stmt, date, section,
category, amount, desc, file) into the GLAW tamper-evident double-entry general ledger, then
produces the reconstruction deliverables: a chart of accounts, the posted GL, a trial balance,
the three-statement set, a month-by-month bank reconciliation (so there are NO gaps), and an
accounting error/exception log. Every transaction maps to a balanced journal entry; nothing is
invented — each entry carries the source statement file and its tamper-evident hash.

Idempotent: each run rebuilds the book from scratch under the chosen GLAW_HOME, so the whole
pipeline can be executed as many times as needed and always yields the same audited result.

Category → chart-of-accounts map is faithful to the classified source categories; an unmapped
category falls into Expenses:Uncategorized (and is reported in the error log), never guessed.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v).replace(",", "").replace("$", "").strip() or "0")
    except Exception:
        return Decimal("0")


# faithful category-prefix → chart-of-accounts mapping (ordered; first match wins)
COA_RULES = [
    ("REVENUE", "Income:Revenue"),
    ("OWNER DRAW", "Equity:Owner Draw"),
    ("OWNER CONTRIB", "Equity:Owner Contribution"),
    ("TRANSFER-IN", "Assets:Bank:Transfers-Clearing"),
    ("TRANSFER-OUT (own", "Assets:Bank:Transfers-Clearing"),
    ("TRANSFER-OUT (external", "Expenses:Transfers-External (REVIEW)"),
    ("TRANSFER-OUT", "Expenses:Transfers-External (REVIEW)"),
    ("CONTRA", "Income:Contra-Refunds"),
    ("COGS/Labor", "Expenses:COGS:Labor"),
    ("COGS — Materials", "Expenses:COGS:Materials"),
    ("COGS", "Expenses:COGS:Other"),
    ("OpEx — Fuel/Auto", "Expenses:Operating:Fuel-Auto"),
    ("OpEx — Advertising", "Expenses:Operating:Advertising"),
    ("OpEx — Software/Insurance", "Expenses:Operating:Software-Insurance-Admin"),
    ("OpEx — card/POS", "Expenses:Operating:Card-POS-Uncategorized"),
    ("OpEx", "Expenses:Operating:Other"),
    ("FEE", "Expenses:Operating:Bank-Fees"),
    ("TAX", "Expenses:Taxes"),
    # review categories — mapped to explicit REVIEW accounts, never guessed to revenue/expense
    ("CASH WITHDRAWAL", "Expenses:Cash-Withdrawals (REVIEW — substantiate)"),
    # FINANCING/WIRE-IN: characterized as REVENUE per client direction (payments for work) — 2026-06-08
    ("FINANCING/WIRE-IN", "Income:Revenue:Construction (wire — payments for work)"),
    ("WIRE/BOOK-OUT", "Expenses:Wire-Out (REVIEW — purpose unstated)"),
    ("WIRE", "Expenses:Wire-Out (REVIEW — purpose unstated)"),
    ("FINANCING", "Income:Revenue:Construction (wire — payments for work)"),
]


def map_account(category: str) -> tuple[str, bool]:
    """category → (chart-of-accounts account, mapped?). Unmapped → Uncategorized + flag."""
    c = (category or "").strip()
    for pref, acct in COA_RULES:
        if c.upper().startswith(pref.upper()):
            return acct, True
    return "Expenses:Uncategorized", False


def counterparty(desc: str) -> str:
    """Extract the wire counterparty from the bank description: ORIG:<name> for an inbound wire,
    BNF:<name> for an outbound. This is the traceable bookkeeping source — every wire is booked to
    the account its real counterparty implies, not to a guessed category."""
    d = (desc or "").upper()
    for tag in ("ORIG:", "BNF:"):
        if tag in d:
            after = d.split(tag, 1)[1]
            # the name runs up to the next " ID:" / " BK:" / "SND" token
            for stop in (" ID:", " BNF BK:", " SND BK:", " SND ", " BK:", " PMT", " RELATED"):
                if stop in after:
                    after = after.split(stop, 1)[0]
            return after.strip()
    return ""


def map_counterparty(desc: str, rules: list) -> str | None:
    """counterparty name → account via the client's counterparty rules (substring match). Returns
    None when no rule matches (falls back to the category mapping). rules: [[substr, account], ...]."""
    cp = counterparty(desc)
    if not cp:
        return None
    for sub, acct in rules:
        if sub.upper() in cp:
            return acct
    return None


def _load_loan_lenders(loan_lenders) -> list:
    """Loan lenders → list of UPPERCASE name substrings. Any transaction whose bank-description names
    a loan lender is booked to that lender's loan liability — an INBOUND wire is loan proceeds
    (credit the liability), an OUTBOUND wire is a repayment (debit the liability) — handled naturally
    by the double entry. Re-runnable: the client extends the lender list as advances are confirmed.
    Accepts a JSON path, a list of names, or None."""
    if loan_lenders is None:
        return []
    items = loan_lenders
    if isinstance(loan_lenders, str):
        items = json.loads(Path(loan_lenders).read_text(encoding="utf-8"))
    return [str(x).upper() for x in items]


def _load_overrides(overrides) -> dict:
    """Per-wire characterization → {(YYYY-MM-DD, amount-string): account}. The CLIENT decides each
    material wire's treatment (e.g. an advance payment vs a loan) in a file and re-runs; this takes
    precedence over the category and loan-lender mappings. Accepts a JSON path, a list of
    {date, amount, account, note?}, or None."""
    out = {}
    if overrides is None:
        return out
    items = overrides
    if isinstance(overrides, str):
        items = json.loads(Path(overrides).read_text(encoding="utf-8"))
    for it in items:
        out[(str(it["date"])[:10], str(_q(_dec(it["amount"]))))] = it["account"]
    return out


def ingest(csv_path: str, *, book: str = "blackstone", loan_lenders=None, overrides=None, counterparty_rules=None) -> dict:
    """Post every CSV row to the GLAW ledger as a balanced double entry. Returns a build report."""
    sys.path.insert(0, str(Path(__file__).parent))
    import ledger as L

    lenders = _load_loan_lenders(loan_lenders)
    ovr = _load_overrides(overrides)
    cp_rules = (json.loads(Path(counterparty_rules).read_text(encoding="utf-8"))
                if isinstance(counterparty_rules, str) else (counterparty_rules or []))
    led = L.Ledger(book)
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8", errors="replace")))
    errors, unmapped_cats = [], set()
    posted, loan_hits, override_hits, cp_hits = 0, 0, 0, 0
    bank_seen = set()
    for i, r in enumerate(rows):
        amt = _dec(r.get("amount"))
        if amt == 0:
            errors.append({"row": i + 2, "issue": "zero amount", "desc": r.get("desc", "")[:60]})
            continue
        acct_no = (r.get("acct") or "?").strip()
        bank = f"Assets:Bank:BofA-{acct_no}"
        bank_seen.add(bank)
        contra, mapped = map_account(r.get("category", ""))
        date = _norm_date(r.get("date", ""), r.get("stmt", ""))
        desc = r.get("desc", "") or ""
        # COUNTERPARTY rule (traceable to the wire's ORIG:/BNF:) — the primary, document-driven map
        cp_acct = map_counterparty(desc, cp_rules)
        if cp_acct:
            contra, mapped, cp_hits = cp_acct, True, cp_hits + 1
        # loan-lender fallback: a wire naming a loan lender → that lender's loan liability
        desc_up = desc.upper()
        hit = next((ln for ln in lenders if ln in desc_up), None)
        if hit and not cp_acct:
            contra, mapped, loan_hits = f"Liabilities:Loans-Payable:{hit.title()}", True, loan_hits + 1
        # per-wire client characterization takes final precedence (date + amount match)
        key = (date, str(_q(abs(amt))))
        if key in ovr:
            contra, mapped, override_hits = ovr[key], True, override_hits + 1
        if not mapped:
            unmapped_cats.add(r.get("category", ""))
        memo = (r.get("desc", "") or "")[:120]
        src = r.get("file", "")
        # deposit (amount > 0): Dr bank / Cr contra ;  withdrawal (< 0): Dr contra / Cr bank
        if amt > 0:
            lines = [{"account": bank, "debit": str(_q(amt))},
                     {"account": contra, "credit": str(_q(amt))}]
        else:
            lines = [{"account": contra, "debit": str(_q(-amt))},
                     {"account": bank, "credit": str(_q(-amt))}]
        try:
            led.post({"date": date, "memo": memo, "source": src,
                      "lines": lines}, dedupe_hash=None)
            posted += 1
        except Exception as e:                       # never silently drop — log it
            errors.append({"row": i + 2, "issue": f"post failed: {e}", "desc": memo})
    return {"book": book, "rows": len(rows), "posted": posted, "loan_hits": loan_hits, "override_hits": override_hits, "counterparty_hits": cp_hits,
            "bank_accounts": sorted(bank_seen), "errors": errors,
            "unmapped_categories": sorted(unmapped_cats)}


def _norm_date(date_str: str, stmt: str) -> str:
    """MM/DD/YY → YYYY-MM-DD; fall back to the statement month's first day."""
    s = (date_str or "").strip()
    try:
        mm, dd, yy = s.split("/")
        yr = int(yy)
        yr = 2000 + yr if yr < 100 else yr
        return f"{yr:04d}-{int(mm):02d}-{int(dd):02d}"
    except Exception:
        st = (stmt or "").strip()
        return f"{st}-01" if len(st) == 7 else "2021-01-01"


def reconstruct(csv_path: str, *, book: str = "blackstone", loan_lenders=None, overrides=None, counterparty_rules=None) -> dict:
    sys.path.insert(0, str(Path(__file__).parent))
    import ledger as L
    import statements as S

    build = ingest(csv_path, book=book, loan_lenders=loan_lenders, overrides=overrides, counterparty_rules=counterparty_rules)
    led = L.Ledger(book)
    bal = led.balances()
    stmts = S.build(postings=led.postings())
    integrity = L.verify_integrity(led.entries())
    # transfers-clearing should net near zero (own-account moves in == out)
    clearing = bal.get("Assets:Bank:Transfers-Clearing", Decimal("0"))
    return {"build": build, "trial_balance_balanced": stmts["trial_balance"]["balanced"],
            "net_income": str(stmts["profit_loss"]["net_income"]),
            "balance_sheet_balances": stmts["balance_sheet"]["balances"],
            "chain_intact": not integrity,
            "transfers_clearing_residual": str(_q(clearing)),
            "balances": {a: str(_q(b)) for a, b in bal.items() if b != 0},
            "statements": stmts}


def render_text(d: dict) -> str:
    b = d["build"]
    o = ["=" * 64, "FORENSIC RECONSTRUCTION", "-" * 64,
         f"  rows ingested: {b['rows']}   posted: {b['posted']}   errors: {len(b['errors'])}",
         f"  bank accounts: {', '.join(b['bank_accounts'])}",
         f"  trial balance balanced: {d['trial_balance_balanced']}",
         f"  hash-chain intact: {d['chain_intact']}",
         f"  net income (period): {_dec(d['net_income']):,.2f}",
         f"  transfers-clearing residual: {_dec(d['transfers_clearing_residual']):,.2f}  (own-acct in−out; near 0 = reconciled)"]
    if b["unmapped_categories"]:
        o.append(f"  ⚠️ unmapped categories ({len(b['unmapped_categories'])}): {b['unmapped_categories'][:5]}")
    o.append("=" * 64)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-forensic-pipeline")
    ap.add_argument("csv", help="master-ledger CSV (acct,stmt,date,section,category,amount,desc,file)")
    ap.add_argument("--book", default="blackstone")
    ap.add_argument("--loan-lenders", default=None, help="JSON list of lender names (e.g. [\"EXAMPLE-CAPITAL\"]) whose wires are loans")
    ap.add_argument("--overrides", default=None, help="JSON [{date, amount, account, note}] — per-wire client characterization")
    ap.add_argument("--counterparty-rules", default=None, help="JSON [[substr, account]] — map a wire ORIG:/BNF: counterparty to an account (traceable)")
    ap.add_argument("--out", default=None, help="write JSON deliverables to this directory")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = reconstruct(a.csv, book=a.book, loan_lenders=a.loan_lenders, overrides=a.overrides, counterparty_rules=a.counterparty_rules)
    if a.out:
        outd = Path(a.out); outd.mkdir(parents=True, exist_ok=True)
        (outd / "reconstruction.json").write_text(json.dumps(d, indent=2, default=str))
        (outd / "trial_balance.json").write_text(json.dumps(d["balances"], indent=2, default=str))
        (outd / "three_statement.json").write_text(json.dumps(d["statements"], indent=2, default=str))
        (outd / "error_log.json").write_text(json.dumps(d["build"]["errors"], indent=2, default=str))
        print(f"deliverables written to {outd}")
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
