#!/usr/bin/env python3
"""glaw-ledger — CLI over the persistent general ledger.

Subcommands:
  post          post a balanced manual/adjusting journal entry
  import-bank   post glaw-bank-ingest rows as journal entries
  rebuild       AUDIT REBUILD — reconstruct the whole books from source statements
  balances      trial balance (as-of)
  gl            general-ledger detail for one account (running balance)
  statements    P&L / Balance Sheet / Cash Flow / Trial Balance from the posted ledger
  audit         audit pack — statements + integrity check + per-entry trace + cross-reference
  lock          lock the books through a date
  close-year    year-end closing entry (Income/Expense → Retained Earnings)
  status        book summary
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L          # noqa: E402
import statements as S      # noqa: E402

INGEST = str(Path(__file__).resolve().parents[2] / "bin" / "glaw-bank-ingest")


def _ingest_to_rows(path: str, chart: str | None, mapfile: str | None) -> dict:
    args = [INGEST, path, "--format", "json"]
    if chart:
        args += ["--chart", chart]
    if mapfile:
        args += ["--map", mapfile]
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode not in (0, 1) or not out.stdout.strip():
        raise SystemExit(f"ingest failed for {path}: {out.stderr.strip()[:200]}")
    return json.loads(out.stdout)


def _print(obj, fmt):
    print(json.dumps(obj, indent=2, default=str) if fmt == "json" else obj)


def cmd_post(led: L.Ledger, a):
    if a.json:
        je = json.load(open(a.json, encoding="utf-8"))
    else:
        lines = [{"account": acct, "debit": amt} for acct, amt in (a.debit or [])]
        lines += [{"account": acct, "credit": amt} for acct, amt in (a.credit or [])]
        je = {"date": a.date, "memo": a.memo or "", "source": "manual", "lines": lines}
    res = led.post(je)
    print(f"posted entry #{res.get('id')}  {res.get('date')}  hash {res.get('entry_hash')}"
          if not res.get("skipped") else f"skipped ({res.get('reason')})")
    return 0


def cmd_import_bank(led: L.Ledger, a):
    payload = json.load(open(a.json, encoding="utf-8")) if a.json != "-" else json.load(sys.stdin)
    rows = payload["rows"] if isinstance(payload, dict) and "rows" in payload else payload
    res = led.import_bank(rows, bank_account=a.bank)
    print(f"imported: {res['posted']} posted, {res['skipped_duplicates']} duplicates skipped")
    return 0


def cmd_rebuild(led: L.Ledger, a):
    """Reconstruct the books from raw statements — for an audit / fresh set of books."""
    inputs = a.inputs
    if len(inputs) == 1 and Path(inputs[0]).is_dir():
        inputs = sorted(str(p) for p in Path(inputs[0]).glob("**/*")
                        if p.is_file() and p.suffix.lower() in
                        (".csv", ".ofx", ".qfx", ".mt940", ".sta", ".xml", ".pdf"))
    total_posted = total_skip = 0
    sources = []
    for f in inputs:
        payload = _ingest_to_rows(f, a.chart, a.map)
        rows = payload.get("rows", [])
        res = led.import_bank(rows, bank_account=a.bank)
        total_posted += res["posted"]
        total_skip += res["skipped_duplicates"]
        for au in payload.get("audit", []):
            sources.append({"file": f, "method": au.get("method"),
                            "rows": au.get("rows"), "balance_status": au.get("balance_status")})
    print(f"REBUILD complete: {len(inputs)} statements → {total_posted} entries posted "
          f"({total_skip} duplicates skipped).")
    for s in sources:
        print(f"  {s['file']}  [{s['method']}]  rows={s['rows']}  Golden-Rule={s['balance_status']}")
    return 0


def cmd_balances(led: L.Ledger, a):
    tb = S.trial_balance(led.balances(a.as_of))
    if a.format == "json":
        _print(tb, "json")
    else:
        print(S.render_text(S.build(postings=led.postings(a.as_of)), currency=a.currency))
    return 0 if tb["balanced"] else 1


def cmd_gl(led: L.Ledger, a):
    g = led.gl(a.account, a.frm, a.to)
    if a.format == "json":
        _print(g, "json"); return 0
    print(f"GENERAL LEDGER — {a.account}")
    print(f"  {'Date':<12}{'#':>5}  {'Memo':<34}{'Amount':>14}{'Balance':>14}")
    for r in g["rows"]:
        print(f"  {r['date']:<12}{r['id']:>5}  {(r['memo'] or '')[:34]:<34}"
              f"{r['amount']:>14,.2f}{r['balance']:>14,.2f}")
    print(f"  ending balance: {g['ending_balance']:,.2f}")
    return 0


def cmd_statements(led: L.Ledger, a):
    s = S.build(postings=led.postings(a.as_of))
    _print(s, "json") if a.format == "json" else print(S.render_text(s, currency=a.currency))
    return 0 if (s["trial_balance"]["balanced"] and s["balance_sheet"]["balances"]) else 1


def cmd_audit(led: L.Ledger, a):
    """Audit pack: statements + integrity (tamper-evident chain, TB/BS balance) + per-entry trace."""
    entries = led.entries(a.as_of)
    s = S.build(postings=led.postings(a.as_of))
    # integrity: the chained hash-verify (catches edits, currency tamper, deletion, insertion)
    problems = L.verify_integrity(entries)
    tampered = sorted({eid for eid, _ in problems})
    pack = {
        "book": led.book, "as_of": a.as_of, "entries": len(entries),
        "trial_balance_balanced": s["trial_balance"]["balanced"],
        "balance_sheet_balances": s["balance_sheet"]["balances"],
        "integrity_ok": not tampered, "tampered_or_unbalanced_entries": sorted(set(tampered)),
        "net_income": s["profit_loss"]["net_income"],
        "statements": s,
        "trace": [{"id": e["id"], "date": e["date"], "source": e.get("source"),
                   "memo": e["memo"], "entry_hash": e.get("entry_hash"),
                   "transaction_hash": e.get("transaction_hash"),
                   "lines": e["lines"]} for e in entries],
    }
    audit_ok = (pack["trial_balance_balanced"] and pack["balance_sheet_balances"]
                and pack["integrity_ok"])
    if a.format == "json":
        _print(pack, "json")
    else:
        print(S.render_text(s, currency=a.currency))
        print("\n" + "=" * 60)
        print("AUDIT INTEGRITY")
        print("-" * 60)
        print(f"  entries: {pack['entries']}")
        print(f"  trial balance balanced:  {'✓' if pack['trial_balance_balanced'] else '✗'}")
        print(f"  balance sheet balances:  {'✓' if pack['balance_sheet_balances'] else '✗'}")
        print(f"  tamper-evidence intact:  {'✓' if pack['integrity_ok'] else '✗ ' + str(pack['tampered_or_unbalanced_entries'])}")
        print(f"  {'🛡️  AUDIT-READY' if audit_ok else '❌ AUDIT FAILED'}")
        print("=" * 60)
    return 0 if audit_ok else 1


def cmd_lock(led: L.Ledger, a):
    print(f"locked through {led.lock(a.through)['locked_through']}")
    return 0


def cmd_close_year(led: L.Ledger, a):
    r = led.close_year(a.year, retained=a.retained)
    print(json.dumps(r, indent=2, default=str) if r["closed"]
          else f"no close: {r.get('reason')}")
    return 0


def cmd_status(led: L.Ledger, a):
    print(json.dumps(led.status(), indent=2, default=str))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-ledger")
    ap.add_argument("--book", default="default", help="set of books (default: 'default')")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("post"); p.add_argument("--date", required=False); p.add_argument("--memo")
    p.add_argument("--debit", nargs=2, action="append", metavar=("ACCT", "AMT"))
    p.add_argument("--credit", nargs=2, action="append", metavar=("ACCT", "AMT"))
    p.add_argument("--json", help="entry JSON file"); p.set_defaults(fn=cmd_post)

    p = sub.add_parser("import-bank"); p.add_argument("json", nargs="?", default="-")
    p.add_argument("--bank", default="Assets:Bank:Checking"); p.set_defaults(fn=cmd_import_bank)

    p = sub.add_parser("rebuild"); p.add_argument("inputs", nargs="+")
    p.add_argument("--chart"); p.add_argument("--map"); p.add_argument("--bank", default="Assets:Bank:Checking")
    p.set_defaults(fn=cmd_rebuild)

    for name, fn in (("balances", cmd_balances), ("statements", cmd_statements), ("audit", cmd_audit)):
        p = sub.add_parser(name); p.add_argument("--as-of", default=None)
        p.add_argument("--currency", default="USD"); p.add_argument("--format", default="text", choices=["text", "json"])
        p.set_defaults(fn=fn)

    p = sub.add_parser("gl"); p.add_argument("--account", required=True)
    p.add_argument("--from", dest="frm", default=None); p.add_argument("--to", default=None)
    p.add_argument("--format", default="text", choices=["text", "json"]); p.set_defaults(fn=cmd_gl)

    p = sub.add_parser("lock"); p.add_argument("--through", required=True); p.set_defaults(fn=cmd_lock)
    p = sub.add_parser("close-year"); p.add_argument("--year", type=int, required=True)
    p.add_argument("--retained", default="Equity:RetainedEarnings"); p.set_defaults(fn=cmd_close_year)
    p = sub.add_parser("status"); p.set_defaults(fn=cmd_status)

    a = ap.parse_args()
    led = L.Ledger(a.book)
    try:
        return a.fn(led, a)
    except L.LedgerError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
