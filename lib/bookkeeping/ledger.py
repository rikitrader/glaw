#!/usr/bin/env python3
"""GLAW general ledger — the persistent, double-entry book of record.

The accounting foundation: an append-only journal of balanced entries that
accumulates across periods. Bank transactions and manual/adjusting journal
entries both post here as proper Dr/Cr journal entries; balances and statements
are computed from the posted ledger as-of any date.

Design goals (IRS / CPA grade):
  * Double-entry, always balanced     sum(debits) == sum(credits) per entry, enforced.
  * Append-only audit trail           each entry is sequential, hashed, timestamped;
                                       entries are never edited — corrections are reversing
                                       entries. Nothing is silently mutated.
  * Period locking                    a locked period rejects new/back-dated entries.
  * As-of queries                     account balances / trial balance / GL detail at any date.

Storage: one JSONL file of entries per set of books, under
  $GLAW_HOME/books/<book>/ledger.jsonl   (+ meta.json for locked periods)
GLAW_HOME defaults to ~/.glaw (matches the rest of GLAW's state).
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

# Account-root → (type, normal-balance-sign). Debit-normal accounts carry positive
# balances; credit-normal carry negative (the signed-amount convention statements uses).
ACCOUNT_TYPES = {
    "Assets": ("asset", "debit"),
    "Expenses": ("expense", "debit"),
    "Liabilities": ("liability", "credit"),
    "Equity": ("equity", "credit"),
    "Income": ("income", "credit"),
    "Revenue": ("income", "credit"),
}


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _home() -> Path:
    return Path(os.environ.get("GLAW_HOME", str(Path.home() / ".glaw")))


class LedgerError(Exception):
    pass


def validate_entry(je: dict) -> dict:
    """Validate and normalize a journal entry. Raises LedgerError on any problem.
    je = {date, memo, source?, lines: [{account, debit?, credit?}, ...]}"""
    try:
        d = date.fromisoformat(str(je["date"])[:10])
    except Exception:
        raise LedgerError(f"invalid or missing entry date: {je.get('date')!r}")
    lines = je.get("lines") or []
    if len(lines) < 2:
        raise LedgerError("a journal entry needs at least two lines (a debit and a credit)")
    norm_lines, tot_d, tot_c = [], Decimal("0"), Decimal("0")
    for i, ln in enumerate(lines):
        acct = (ln.get("account") or "").strip()
        if not acct:
            raise LedgerError(f"line {i}: missing account")
        deb = _dec(ln.get("debit", 0))
        cred = _dec(ln.get("credit", 0))
        if deb < 0 or cred < 0:
            raise LedgerError(f"line {i} ({acct}): debit/credit must be non-negative")
        if (deb > 0) == (cred > 0):
            raise LedgerError(f"line {i} ({acct}): exactly one of debit/credit must be > 0")
        tot_d += deb
        tot_c += cred
        nl = {"account": acct, "debit": str(deb), "credit": str(cred), "memo": ln.get("memo", "")}
        if ln.get("currency"):                  # preserve per-line currency (FX/cross-currency entries)
            nl["currency"] = ln["currency"]
        norm_lines.append(nl)
    if tot_d != tot_c:
        raise LedgerError(f"entry does not balance: debits {tot_d} != credits {tot_c}")
    if tot_d == 0:
        raise LedgerError("entry has zero value")
    return {"date": d.isoformat(), "memo": je.get("memo", ""), "source": je.get("source", "manual"),
            "lines": norm_lines}


def bank_rows_to_entries(rows: list[dict], *, bank_account: str = "Assets:Bank:Checking") -> list[dict]:
    """Convert glaw-bank-ingest rows into balanced journal entries (bank leg + contra)."""
    from statements import _resolve_contra  # local module
    out = []
    for r in rows:
        amt = _dec(r.get("amount"))
        if amt == 0:
            continue
        contra = _resolve_contra(r.get("category"))
        memo = (r.get("description") or "")[:120]
        d = str(r.get("booking_date") or "")[:10] or date.today().isoformat()
        if amt > 0:   # money in: debit bank, credit contra
            lines = [{"account": bank_account, "debit": amt, "credit": 0},
                     {"account": contra, "debit": 0, "credit": amt}]
        else:         # money out: credit bank, debit contra
            lines = [{"account": bank_account, "debit": 0, "credit": -amt},
                     {"account": contra, "debit": -amt, "credit": 0}]
        out.append({"date": d, "memo": memo, "source": r.get("source_method", "bank"),
                    "lines": lines, "transaction_hash": r.get("transaction_hash"),
                    "currency": r.get("currency")})
    return out


class Ledger:
    def __init__(self, book: str = "default", home: Path | None = None):
        self.book = book
        self.dir = (home or _home()) / "books" / book
        self.path = self.dir / "ledger.jsonl"
        self.meta_path = self.dir / "meta.json"

    # ---- persistence -------------------------------------------------------
    def _meta(self) -> dict:
        if self.meta_path.exists():
            return json.loads(self.meta_path.read_text())
        return {"locked_through": None, "next_id": 1, "seen_hashes": []}

    def _write_meta(self, m: dict) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        self.meta_path.write_text(json.dumps(m, indent=2))

    def entries(self, as_of: str | None = None) -> list[dict]:
        if not self.path.exists():
            return []
        out = []
        cutoff = date.fromisoformat(as_of[:10]) if as_of else None
        for line in self.path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            if cutoff and date.fromisoformat(e["date"]) > cutoff:
                continue
            out.append(e)
        return out

    # ---- posting -----------------------------------------------------------
    def post(self, je: dict, *, dedupe_hash: str | None = None) -> dict:
        norm = validate_entry(je)
        meta = self._meta()
        # period lock: cannot post into or before a locked period
        if meta.get("locked_through"):
            if date.fromisoformat(norm["date"]) <= date.fromisoformat(meta["locked_through"]):
                raise LedgerError(f"period locked through {meta['locked_through']}; "
                                  f"cannot post entry dated {norm['date']} (use a reversing entry in an open period)")
        if dedupe_hash and dedupe_hash in meta.get("seen_hashes", []):
            return {"skipped": True, "reason": "duplicate", "hash": dedupe_hash}
        eid = meta.get("next_id", 1)
        posted_at = datetime.now(timezone.utc).isoformat()
        payload = {"id": eid, "posted_at": posted_at, **norm}
        if je.get("transaction_hash"):
            payload["transaction_hash"] = je["transaction_hash"]
        if je.get("currency"):
            payload["currency"] = je["currency"]
        # tamper-evident: hash the entry content
        payload["entry_hash"] = hashlib.sha256(
            json.dumps({k: payload[k] for k in ("id", "date", "memo", "lines")},
                       sort_keys=True, default=str).encode()).hexdigest()[:16]
        self.dir.mkdir(parents=True, exist_ok=True)
        with self.path.open("a") as fh:
            fh.write(json.dumps(payload, default=str) + "\n")
        meta["next_id"] = eid + 1
        if dedupe_hash:
            meta.setdefault("seen_hashes", []).append(dedupe_hash)
        self._write_meta(meta)
        return {"id": eid, "entry_hash": payload["entry_hash"], "date": norm["date"]}

    def import_bank(self, rows: list[dict], *, bank_account: str = "Assets:Bank:Checking") -> dict:
        posted, skipped = 0, 0
        for je in bank_rows_to_entries(rows, bank_account=bank_account):
            res = self.post(je, dedupe_hash=je.get("transaction_hash"))
            if res.get("skipped"):
                skipped += 1
            else:
                posted += 1
        return {"posted": posted, "skipped_duplicates": skipped}

    def post_opening(self, account: str, amount, as_of: str, *, account_type: str = "asset",
                     equity: str = "Equity:Opening Balance Equity") -> dict:
        """Post an account's opening balance against Opening Balance Equity so the GL reflects
        the true starting position (an ongoing company's books don't start at zero).
        `amount` is the natural-balance magnitude: a debit balance for assets, a credit
        balance (amount owed) for liabilities. Idempotent per (account, as_of)."""
        amt = _dec(amount)
        if amt == 0:
            return {"skipped": True, "reason": "zero opening"}
        h = f"opening:{account}:{as_of}"
        if h in self._meta().get("seen_hashes", []):
            return {"skipped": True, "reason": "opening already posted"}
        if account_type == "liability":          # credit-normal: Cr the account, Dr OBE
            lines = [{"account": equity, "debit": amt, "credit": 0},
                     {"account": account, "debit": 0, "credit": amt}]
        else:                                    # asset (debit-normal): Dr the account, Cr OBE
            lines = [{"account": account, "debit": amt, "credit": 0},
                     {"account": equity, "debit": 0, "credit": amt}]
        return self.post({"date": as_of, "memo": f"Opening balance — {account}",
                          "source": "opening-balance", "lines": lines}, dedupe_hash=h)

    # ---- queries -----------------------------------------------------------
    def postings(self, as_of: str | None = None) -> list[dict]:
        """Flatten entries to signed postings: amount = debit - credit (debit positive)."""
        out = []
        for e in self.entries(as_of):
            for ln in e["lines"]:
                out.append({"date": e["date"], "id": e["id"], "memo": e["memo"],
                            "account": ln["account"],
                            "amount": _dec(ln["debit"]) - _dec(ln["credit"])})
        return out

    def balances(self, as_of: str | None = None) -> dict[str, Decimal]:
        bal: dict[str, Decimal] = {}
        for p in self.postings(as_of):
            bal[p["account"]] = bal.get(p["account"], Decimal("0")) + p["amount"]
        return bal

    def gl(self, account: str, frm: str | None = None, to: str | None = None) -> dict:
        run = Decimal("0")
        rows = []
        f = date.fromisoformat(frm) if frm else None
        for p in self.postings(to):
            if p["account"] != account:
                continue
            d = date.fromisoformat(p["date"])
            run += p["amount"]                 # running balance includes opening
            if f and d < f:
                continue
            rows.append({"date": p["date"], "id": p["id"], "memo": p["memo"],
                         "amount": p["amount"], "balance": run})
        return {"account": account, "rows": rows, "ending_balance": run}

    # ---- controls ----------------------------------------------------------
    def lock(self, through: str) -> dict:
        d = date.fromisoformat(through[:10]).isoformat()
        meta = self._meta()
        meta["locked_through"] = d
        self._write_meta(meta)
        return {"locked_through": d}

    def status(self) -> dict:
        es = self.entries()
        return {"book": self.book, "entries": len(es),
                "locked_through": self._meta().get("locked_through"),
                "first": es[0]["date"] if es else None,
                "last": es[-1]["date"] if es else None}

    def close_year(self, year: int, *, retained: str = "Equity:RetainedEarnings") -> dict:
        """Year-end closing entry: zero Income & Expense into Retained Earnings."""
        as_of = f"{year}-12-31"
        # net of income+expense FOR THE YEAR (entries dated in `year`)
        ytd = {}
        start = date(year, 1, 1)
        for p in self.postings(as_of):
            if date.fromisoformat(p["date"]) < start:
                continue
            root = p["account"].split(":", 1)[0]
            if root in ("Income", "Revenue", "Expenses"):
                ytd[p["account"]] = ytd.get(p["account"], Decimal("0")) + p["amount"]
        lines, net = [], Decimal("0")
        for acct, bal in sorted(ytd.items()):
            if bal == 0:
                continue
            # reverse the account's balance to zero it
            if bal > 0:   # debit balance (expense) → credit it to close
                lines.append({"account": acct, "debit": 0, "credit": bal})
            else:
                lines.append({"account": acct, "debit": -bal, "credit": 0})
            net += -bal   # net income = -(sum of I/E signed balances)
        # no non-zero income/expense to close (no activity, or the year is already closed)
        if not lines:
            return {"closed": False, "reason": "no income/expense activity to close (already closed?)"}
        # plug to retained earnings
        if net >= 0:
            lines.append({"account": retained, "debit": 0, "credit": net})
        else:
            lines.append({"account": retained, "debit": -net, "credit": 0})
        res = self.post({"date": as_of, "memo": f"Year-end close {year} → {retained}",
                         "source": "year-end-close", "lines": lines})
        return {"closed": True, "year": year, "net_income": net, "entry": res}
