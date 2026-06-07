#!/usr/bin/env python3
"""GLAW Bookkeeping runner — thin orchestration over the vendored
glaw_engine engine.

Pipeline:  ingest -> Golden-Rule balance verify -> dedupe -> account map
           -> export (hledger / beancount / json)

Every row keeps its immutable transaction_hash and source_method audit tag.
No figures are invented: a row that cannot be parsed is reported, not guessed.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

from glaw_engine.hybrid.orchestrator import smart_ingest, IngestResult
from glaw_engine.hybrid.scanner import scan_and_ingest
from glaw_engine.export.ledger import to_hledger, to_beancount
from glaw_engine.enrichment.account_mapper import AccountMapper
from glaw_engine.transaction_deduplicator import Deduplicator


CHARTS_DIR = Path(__file__).parent / "charts"


def _charts() -> list[str]:
    """Names of bundled charts of accounts (charts/*.json), stem only."""
    if not CHARTS_DIR.is_dir():
        return []
    return sorted(p.stem for p in CHARTS_DIR.glob("*.json"))


def _resolve_chart(name: str):
    """Resolve a bundled chart name to its JSON path, or None."""
    p = CHARTS_DIR / f"{name}.json"
    return str(p) if p.exists() else None


def _dec(v):
    if v is None:
        return None
    try:
        return Decimal(str(v))
    except (InvalidOperation, ValueError):
        return None


def _ingest_pdf(path: Path, open_bal, close_bal, ocr="auto"):
    """PDF front-end: opendataloader-pdf (digital) or tesseract OCR (scanned)
    -> CSV -> deterministic parser.

    Uses balances sniffed from the PDF text for the Golden Rule when the
    caller didn't pass --open/--close explicitly.
    """
    from pdf_extract import extract_to_csv  # local module, lives inside GLAW

    csv_path, meta = extract_to_csv(path, ocr=ocr)
    if open_bal is None:
        open_bal = _dec(meta.get("opening_balance"))
    if close_bal is None:
        close_bal = _dec(meta.get("closing_balance"))
    res = smart_ingest(csv_path, opening_balance=open_bal, closing_balance=close_bal)
    # IngestResult is frozen; carry the PDF provenance alongside it for the audit.
    how = "tesseract OCR" if meta.get("source_method_hint") == "ocr" else "opendataloader-pdf"
    note = f"source PDF: {path.name} (extracted via {how})"
    return list(res.transactions), [res], {id(res): note}


def _collect(path: Path, pattern: str, open_bal, close_bal, ocr="auto"):
    """Return (transactions, results, notes) across a file or directory tree.

    ``notes`` maps id(result) -> a provenance string injected into the audit.
    """
    if path.is_dir():
        scan = scan_and_ingest(str(path), pattern=pattern)
        # ScanResult exposes .results and a deduped .unique_transactions
        results = list(getattr(scan, "results", []) or [])
        txs = list(getattr(scan, "unique_transactions", []) or [])
        return txs, results, {}
    if path.suffix.lower() == ".pdf":
        return _ingest_pdf(path, open_bal, close_bal, ocr=ocr)
    res = smart_ingest(path, opening_balance=open_bal, closing_balance=close_bal)
    return list(res.transactions), [res], {}


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-bank-ingest")
    ap.add_argument("input", help="Statement file or directory")
    ap.add_argument("--matter", default=None, help="GLAW matter slug (for the audit header)")
    ap.add_argument("--map", dest="mapfile", default=None,
                    help="AccountMapper rules JSON (custom path)")
    ap.add_argument("--chart", default=None,
                    help="Bundled chart of accounts: " + ", ".join(_charts()))
    ap.add_argument("--format", default="hledger",
                    choices=["hledger", "beancount", "json", "gsheet"])
    ap.add_argument("--out", default=None, help="Write output to this path instead of stdout")
    ap.add_argument("--sheet-title", default=None,
                    help="Title for the Google Sheet when --format gsheet")
    ap.add_argument("--pattern", default="**/*.*", help="Glob when input is a directory")
    ap.add_argument("--open", dest="open_bal", default=None, help="Opening balance override")
    ap.add_argument("--close", dest="close_bal", default=None, help="Closing balance override")
    ap.add_argument("--currency", default="USD",
                    help="Default currency for rows with none set (default: USD)")
    ap.add_argument("--ocr", default="auto", choices=["auto", "force", "off"],
                    help="Scanned-PDF OCR: auto (fallback), force (always OCR), off")
    args = ap.parse_args()

    in_path = Path(args.input).expanduser()
    if not in_path.exists():
        print(f"ERROR: input not found: {in_path}", file=sys.stderr)
        return 2

    # Resolve the chart of accounts: --map (custom) wins, else --chart (bundled).
    mapfile = args.mapfile
    if not mapfile and args.chart:
        mapfile = _resolve_chart(args.chart)
        if not mapfile:
            print(f"ERROR: unknown chart '{args.chart}'. Available: {', '.join(_charts())}",
                  file=sys.stderr)
            return 2

    txs, results, notes = _collect(in_path, args.pattern, _dec(args.open_bal),
                                   _dec(args.close_bal), ocr=args.ocr)

    # Dedupe across the whole batch (idempotent re-ingestion).
    # dedupe_by_hash returns (unique, skipped_hashes). The directory path
    # already deduped, so only run here for the single-file path.
    if not in_path.is_dir():
        unique, _skipped = Deduplicator().dedupe_by_hash(txs)
        txs = list(unique)

    # Account mapping (optional): set Transaction.category as the contra-account.
    # Transaction is frozen, so build immutable copies rather than mutate.
    mapped = 0
    if mapfile:
        mapper = AccountMapper.from_json(mapfile)
        remapped = []
        for tx in txs:
            acct = mapper.map(tx)
            if acct and acct != mapper.default:
                tx = tx.model_copy(update={"category": acct})
                mapped += 1
            remapped.append(tx)
        txs = remapped

    # Balance audit (Golden Rule) per source statement
    audit = []
    for r in results:
        v = getattr(r, "verification", None)
        warns = list(getattr(r, "warnings", []) or [])
        if id(r) in notes:
            warns.append(notes[id(r)])
        audit.append({
            "source": notes.get(id(r)) or getattr(r, "source_path", None) or str(in_path),
            "method": getattr(r, "source_method", None),
            "rows": len(getattr(r, "transactions", []) or []),
            "balance_status": getattr(getattr(v, "status", None), "value", None),
            "warnings": warns,
        })

    # Render output
    if args.format == "gsheet":
        from sheets_export import export as gsheet_export
        title = args.sheet_title or f"GLAW Bookkeeping — {args.matter or in_path.stem}"
        url = gsheet_export(txs, title=title, matter=args.matter,
                            default_currency=args.currency)
        print(f"Google Sheet created ({len(txs)} tx, {mapped} mapped):\n{url}")
        print("\n--- BALANCE AUDIT (Golden Rule) ---", file=sys.stderr)
        for a in audit:
            print(f"  {a['source']}  [{a['method']}]  rows={a['rows']}  "
                  f"balance={a['balance_status']}  warnings={len(a['warnings'])}",
                  file=sys.stderr)
        return 0

    if args.format == "json":
        payload = {
            "matter": args.matter,
            "transactions": len(txs),
            "accounts_mapped": mapped,
            "audit": audit,
            "rows": [json.loads(tx.model_dump_json()) for tx in txs],
        }
        body = json.dumps(payload, indent=2, default=str)
    else:
        header = f"; GLAW Bookkeeping — matter: {args.matter or '(none)'}  rows: {len(txs)}\n"
        header += "; NOT bookkeeping/tax advice — attorney/CPA work-product for licensed review.\n"
        if args.format == "hledger":
            journal = to_hledger(txs, default_currency=args.currency)
        else:
            journal = to_beancount(txs, default_currency=args.currency)
        body = header + journal

    if args.out:
        Path(args.out).expanduser().write_text(body, encoding="utf-8")
        print(f"Wrote {args.format} -> {args.out}  ({len(txs)} tx, {mapped} mapped)")
    else:
        print(body)

    # Audit summary always to stderr so it never pollutes a redirected journal
    print("\n--- BALANCE AUDIT (Golden Rule) ---", file=sys.stderr)
    for a in audit:
        print(f"  {a['source']}  [{a['method']}]  rows={a['rows']}  "
              f"balance={a['balance_status']}  warnings={len(a['warnings'])}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
