#!/usr/bin/env python3
"""GLAW Bookkeeping runner — thin orchestration over the vendored
glaw_engine engine.

Pipeline:  ingest -> Golden-Rule balance verify -> dedupe -> account map
           -> export (hledger / beancount / json / local csv)

Every row keeps its immutable transaction_hash and source_method audit tag.
No figures are invented: a row that cannot be parsed is reported, not guessed.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
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


def _ingest_pdf(path: Path, open_bal, close_bal, ocr="auto", ocr_profile="bank-statement"):
    """PDF front-end: local text extraction or local OCR binaries -> CSV -> parser."""
    from pdf_extract import extract_to_csv  # local module, lives inside GLAW

    csv_path, meta = extract_to_csv(path, ocr=ocr, profile=ocr_profile)
    if open_bal is None:
        open_bal = _dec(meta.get("opening_balance"))
    if close_bal is None:
        close_bal = _dec(meta.get("closing_balance"))
    res = smart_ingest(csv_path, opening_balance=open_bal, closing_balance=close_bal)
    how = meta.get("source_method_hint") or "pdf_text"
    note = f"source PDF: {path.name} (extracted via {how})"
    return list(res.transactions), [res], {id(res): note}


def _is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def _google_sheet_csv_url(url: str) -> str:
    """Convert a Google Sheets edit/pub URL into a CSV export URL when possible."""
    parsed = urllib.parse.urlparse(url)
    if "docs.google.com" not in parsed.netloc or "/spreadsheets/" not in parsed.path:
        return url
    parts = parsed.path.split("/")
    try:
        sheet_id = parts[parts.index("d") + 1]
    except (ValueError, IndexError):
        return url
    query = urllib.parse.parse_qs(parsed.query)
    gid = query.get("gid", ["0"])[0]
    if "gid=" not in parsed.query and parsed.fragment:
        frag = urllib.parse.parse_qs(parsed.fragment)
        gid = frag.get("gid", [gid])[0]
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def _gcloud_token() -> str | None:
    for args in (["auth", "application-default", "print-access-token"],
                 ["auth", "print-access-token"]):
        try:
            proc = subprocess.run(["gcloud", *args], capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.SubprocessError):
            continue
        token = proc.stdout.strip()
        if proc.returncode == 0 and token:
            return token
    return None


def _download_sheet_or_csv(url: str, google_auth: str = "auto") -> Path:
    csv_url = _google_sheet_csv_url(url)
    headers = {"User-Agent": "GLAW/1.0"}
    if "docs.google.com" in urllib.parse.urlparse(csv_url).netloc and google_auth in ("auto", "gcloud"):
        token = _gcloud_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        elif google_auth == "gcloud":
            raise RuntimeError(
                "Google Sheet auth requested, but no local gcloud OAuth token was available. "
                "Run `gcloud auth application-default login` or make the sheet exportable by link."
            )
    req = urllib.request.Request(csv_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except Exception as exc:
        raise RuntimeError(
            "Could not read Google Sheet/CSV URL. Make the sheet viewable by link, "
            "publish it to CSV, authenticate with local gcloud, or export it manually as CSV."
        ) from exc
    if not data.strip():
        raise RuntimeError("Google Sheet/CSV URL returned no data.")
    out = Path(tempfile.mkdtemp(prefix="glaw-sheet-")) / "sheet.csv"
    out.write_bytes(data)
    return out


def _collect(path: Path, pattern: str, open_bal, close_bal, ocr="auto", ocr_profile="bank-statement"):
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
        return _ingest_pdf(path, open_bal, close_bal, ocr=ocr, ocr_profile=ocr_profile)
    res = smart_ingest(path, opening_balance=open_bal, closing_balance=close_bal)
    return list(res.transactions), [res], {}


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-bank-ingest")
    ap.add_argument("input", help="Statement file, directory, Google Sheet URL, or CSV URL")
    ap.add_argument("--matter", default=None, help="GLAW matter slug (for the audit header)")
    ap.add_argument("--map", dest="mapfile", default=None,
                    help="AccountMapper rules JSON (custom path)")
    ap.add_argument("--chart", default=None,
                    help="Bundled chart of accounts: " + ", ".join(_charts()))
    ap.add_argument("--format", default="hledger",
                    choices=["hledger", "beancount", "json", "csv", "gsheet"])
    ap.add_argument("--out", default=None, help="Write output to this path instead of stdout")
    ap.add_argument("--sheet-title", default=None,
                    help="Title for local CSV files when --format gsheet")
    ap.add_argument("--pattern", default="**/*.*", help="Glob when input is a directory")
    ap.add_argument("--open", dest="open_bal", default=None, help="Opening balance override")
    ap.add_argument("--close", dest="close_bal", default=None, help="Closing balance override")
    ap.add_argument("--currency", default="USD",
                    help="Default currency for rows with none set (default: USD)")
    ap.add_argument("--ocr", default="auto", choices=["auto", "force", "off"],
                    help="PDF OCR mode: auto, force, or off")
    ap.add_argument("--ocr-profile", default="bank-statement",
                    choices=["bank-statement", "dense", "simple"],
                    help="OCR/rendering profile for scanned bank statements")
    ap.add_argument("--google-auth", default="auto", choices=["auto", "none", "gcloud"],
                    help="Google Sheet auth: auto, none, or local gcloud token")
    args = ap.parse_args()

    try:
        if _is_url(args.input):
            in_path = _download_sheet_or_csv(args.input, google_auth=args.google_auth)
            input_label = args.input
        else:
            in_path = Path(args.input).expanduser()
            input_label = str(in_path)
            if not in_path.exists():
                print(f"ERROR: input not found: {in_path}", file=sys.stderr)
                return 2
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    # Resolve the chart of accounts: --map (custom) wins, else --chart (bundled).
    mapfile = args.mapfile
    if not mapfile and args.chart:
        mapfile = _resolve_chart(args.chart)
        if not mapfile:
            print(f"ERROR: unknown chart '{args.chart}'. Available: {', '.join(_charts())}",
                  file=sys.stderr)
            return 2

    try:
        txs, results, notes = _collect(in_path, args.pattern, _dec(args.open_bal),
                                       _dec(args.close_bal), ocr=args.ocr,
                                       ocr_profile=args.ocr_profile)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

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
        _txs = getattr(r, "transactions", []) or []
        _dates = sorted(str(getattr(t, "booking_date", "") or "")[:10] for t in _txs if getattr(t, "booking_date", None))
        audit.append({
            "source": notes.get(id(r)) or getattr(r, "source_path", None) or input_label,
            "method": getattr(r, "source_method", None),
            "rows": len(_txs),
            "balance_status": getattr(getattr(v, "status", None), "value", None),
            # per-statement metadata for continuity / per-account tie-out
            "opening_balance": (str(v.opening_balance) if v is not None and v.opening_balance is not None else None),
            "closing_balance": (str(v.closing_balance) if v is not None and v.closing_balance is not None else None),
            "total_credits": (str(getattr(v, "total_credits", None)) if v is not None else None),
            "total_debits": (str(getattr(v, "total_debits", None)) if v is not None else None),
            "period_start": (_dates[0] if _dates else None),
            "period_end": (_dates[-1] if _dates else None),
            "warnings": warns,
        })

    # Render output
    if args.format in ("csv", "gsheet"):
        from sheets_export import export as gsheet_export
        title = args.sheet_title or f"GLAW Bookkeeping — {args.matter or in_path.stem}"
        csv_path = gsheet_export(txs, title=title, matter=args.matter,
                                 default_currency=args.currency)
        if args.format == "gsheet":
            print("NOTE: --format gsheet is a backwards-compatible alias for local CSV export.", file=sys.stderr)
        print(f"Local CSV export created ({len(txs)} tx, {mapped} mapped):\n{csv_path}")
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
