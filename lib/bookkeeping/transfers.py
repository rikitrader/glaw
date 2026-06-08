#!/usr/bin/env python3
"""GLAW inter-account transfers — detect and reclassify money moved between own accounts.

When statements from several accounts are reconstructed, a transfer (Checking → Savings)
appears as a payment out of one account and a deposit into another. Ingested naively, the
out-leg is booked as an expense and the in-leg as income — double-counted, inflating both
sides of the P&L. This matches those pairs (equal amount, opposite cash direction, different
cash accounts, within a date window) and posts a reclassification that zeroes the bogus
income and expense, leaving only the true cash movement. Idempotent.

Operates on a posted ledger book; intended to be run by the /glaw-reconstruct workflow,
not as a standalone close step.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L          # noqa: E402


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _is_cash(acct: str) -> bool:
    a = acct.lower()
    return (acct.startswith(("Assets:Bank", "Assets:Cash"))
            or "credit card" in a or "creditcard" in a or ":card" in a or "credit:card" in a)


_XFER_KW = ("transfer", "xfer", "tfr", "to savings", "from savings", "to checking",
            "from checking", "internal", "move to", "sweep", "online transfer",
            "wire to", "between accounts")


def _looks_like_transfer(*memos) -> bool:
    return any(any(k in (m or "").lower() for k in _XFER_KW) for m in memos)


def _is_default_contra(acct: str) -> bool:
    return "uncategorized" in (acct or "").lower() or (acct or "").endswith(":Misc")


def _bank_leg(entry: dict):
    """Return (cash_account, signed_cash, contra_account) for a simple 2-leg bank entry, else None."""
    if len(entry["lines"]) != 2:
        return None
    cash = [l for l in entry["lines"] if _is_cash(l["account"])]
    contra = [l for l in entry["lines"] if not _is_cash(l["account"])]
    if len(cash) != 1 or len(contra) != 1:
        return None
    c = cash[0]
    signed = _dec(c["debit"]) - _dec(c["credit"])      # + = money in, − = money out
    return c["account"], signed, contra[0]["account"]


def _store(book: str) -> Path:
    return L.Ledger(book).dir / "transfers.json"


def detect(book: str, *, window_days: int = 5) -> list[dict]:
    led = L.Ledger(book)
    done = set(tuple(p) for p in (json.loads(_store(book).read_text()) if _store(book).exists() else []))
    parsed = []
    for e in led.entries():
        leg = _bank_leg(e)
        if leg:
            acct, signed, contra = leg
            parsed.append({"id": e["id"], "date": e["date"], "acct": acct,
                           "signed": signed, "contra": contra, "memo": e.get("memo", "")})
    outs = [p for p in parsed if p["signed"] < 0]
    ins = [p for p in parsed if p["signed"] > 0]
    used_in, pairs = set(), []
    for o in outs:
        for i in ins:
            if i["id"] in used_in or i["id"] == o["id"]:
                continue
            if i["acct"] == o["acct"]:
                continue                                  # must be different accounts
            if abs(o["signed"]) != i["signed"]:
                continue
            if abs((date.fromisoformat(o["date"]) - date.fromisoformat(i["date"])).days) > window_days:
                continue
            key = tuple(sorted((o["id"], i["id"])))
            if key in done:
                continue
            used_in.add(i["id"])
            # CONFIDENT only with positive evidence it's a transfer (a transfer-like memo, or both
            # legs landed in the default/uncategorized bucket). Without evidence, a same-amount
            # expense + income pair is NOT auto-netted — that would corrupt the P&L.
            # evidence = a transfer-like memo OR a contra account already categorized as a
            # transfer, OR both legs in the default/uncategorized bucket.
            confident = (_looks_like_transfer(o["memo"], i["memo"], o["contra"], i["contra"])
                         or (_is_default_contra(o["contra"]) and _is_default_contra(i["contra"])))
            pairs.append({"amount": str(i["signed"]), "from": o["acct"], "to": i["acct"],
                          "out_id": o["id"], "in_id": i["id"],
                          "out_contra": o["contra"], "in_contra": i["contra"],
                          "out_date": o["date"], "in_date": i["date"],
                          "out_memo": o["memo"], "in_memo": i["memo"], "confident": confident})
            break
    return pairs


def reclassify(book: str, *, window_days: int = 5, apply_all: bool = False) -> dict:
    """Net confident inter-account transfers. Pairs WITHOUT transfer evidence are returned as
    `candidates` (flagged for review), NOT auto-posted, unless apply_all=True."""
    led = L.Ledger(book)
    pairs = detect(book, window_days=window_days)
    to_post = [p for p in pairs if (p["confident"] or apply_all)]
    candidates = [p for p in pairs if not p["confident"] and not apply_all]
    posted = []
    for p in to_post:
        amt = _dec(p["amount"])
        # zero the bogus income (in_contra) and expense (out_contra); cash legs already correct
        led.post({"date": p["in_date"], "memo": f"Transfer reclass {p['from']} → {p['to']}",
                  "source": "transfer-reclass",
                  "lines": [{"account": p["in_contra"], "debit": str(amt), "credit": "0"},
                            {"account": p["out_contra"], "debit": "0", "credit": str(amt)}]})
        posted.append(tuple(sorted((p["out_id"], p["in_id"]))))
    done = set(tuple(x) for x in (json.loads(_store(book).read_text()) if _store(book).exists() else []))
    done |= set(posted)
    _store(book).parent.mkdir(parents=True, exist_ok=True)
    _store(book).write_text(json.dumps([list(x) for x in done]))
    return {"book": book, "transfers_found": len(pairs), "reclassified": len(posted),
            "candidates": candidates, "pairs": to_post}


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-transfers")
    ap.add_argument("--book", required=True)
    ap.add_argument("--window", type=int, default=5)
    ap.add_argument("--apply", action="store_true", help="post the reclassification entries (else dry-run)")
    ap.add_argument("--apply-all", action="store_true", help="also apply low-confidence matches (no transfer evidence)")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    if a.apply or a.apply_all:
        res = reclassify(a.book, window_days=a.window, apply_all=a.apply_all)
    else:
        pairs = detect(a.book, window_days=a.window)
        res = {"book": a.book, "transfers_found": len(pairs), "reclassified": 0,
               "pairs": [p for p in pairs if p["confident"]],
               "candidates": [p for p in pairs if not p["confident"]]}
    if a.format == "json":
        print(json.dumps(res, indent=2, default=str))
    else:
        print(f"transfers found: {res['transfers_found']}   reclassified: {res['reclassified']}")
        for p in res.get("pairs", []):
            print(f"  ✓ {p['out_date']}  {_dec(p['amount']):>12,.2f}  {p['from']} → {p['to']}")
        for p in res.get("candidates", []):
            print(f"  ? {p['out_date']}  {_dec(p['amount']):>12,.2f}  {p['from']} → {p['to']}  "
                  f"(no transfer evidence — REVIEW; --apply-all to net)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
