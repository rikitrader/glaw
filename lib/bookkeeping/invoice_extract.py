#!/usr/bin/env python3
"""GLAW invoice/bill extractor — line-item text → a draft AP bill journal entry.

The bank-statement pipeline parses transactions; this parses a vendor INVOICE/BILL: vendor,
invoice number, date, line items (description + amount), subtotal, tax, and total — then
produces a DRAFT accounts-payable entry (Dr expenses + tax / Cr Liabilities:AP) for review.

Invoice layouts vary wildly, so this is deterministic heuristics over the extracted text,
honest about confidence: every field carries whether it was found, and the draft entry is
flagged if the line items + tax do not reconcile to the stated total. It is a draft for a
human / the adversarial panel to clear, never a silently-trusted posting.

Input: a text file, stdin, or a PDF. Text PDFs use the local `pdftotext` binary when
available; scanned PDFs use local `pdftoppm` + `tesseract`. If text cannot be extracted,
the tool fails closed instead of inventing invoice fields.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

_AMT = re.compile(r"[$€£]?\s?-?\d[\d,]*\.\d{2}")
# require an explicit no/number/# marker AND a value containing a digit, so the standalone
# "INVOICE" header is not mistaken for the number.
_INV_NO = re.compile(r"invoice\s*(?:no\.?|number|#)\s*[:#]?\s*([A-Za-z0-9\-/]*\d[A-Za-z0-9\-/]*)", re.I)
_DATE = re.compile(r"(\d{4}-\d{2}-\d{2}|\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}|"
                   r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})", re.I)
_CCY = {"$": "USD", "€": "EUR", "£": "GBP"}
_HEADER_KW = ("description", "qty", "quantity", "unit price", "rate", "amount", "item", "#")
_TOTAL_KW = ("grand total", "total due", "balance due", "amount due", "total")
_TAX_KW = ("sales tax", "tax", "vat", "gst", "hst")
_SUBTOTAL_KW = ("subtotal", "sub total", "sub-total")


def _dec(s) -> Decimal:
    try:
        return Decimal(re.sub(r"[^\d.\-]", "", str(s)))
    except Exception:
        return Decimal("0")


def _amounts(line: str) -> list[Decimal]:
    return [_dec(m) for m in _AMT.findall(line)]


def extract_text(path: str) -> str:
    p = Path(path)
    if p.suffix.lower() != ".pdf":
        return p.read_text(encoding="utf-8", errors="replace")
    texts: list[str] = []
    if shutil.which("pdftotext"):
        proc = subprocess.run(
            ["pdftotext", "-layout", str(p), "-"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            texts.append(proc.stdout)
    if shutil.which("pdftoppm") and shutil.which("tesseract"):
        with tempfile.TemporaryDirectory(prefix="glaw-invoice-ocr-") as td:
            prefix = str(Path(td) / "page")
            raster = subprocess.run(
                ["pdftoppm", "-r", "300", "-png", str(p), prefix],
                capture_output=True,
                text=True,
                timeout=90,
            )
            if raster.returncode == 0:
                for img in sorted(Path(td).glob("page-*.png")):
                    ocr = subprocess.run(
                        ["tesseract", str(img), "stdout", "--psm", "6"],
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                    if ocr.returncode == 0 and ocr.stdout.strip():
                        texts.append(ocr.stdout)
    best = max(texts, key=len) if texts else ""
    if not best.strip():
        raise RuntimeError(
            "Could not extract invoice PDF text with local source-only tools. Install "
            "poppler/tesseract or provide a text export; unresolved fields stay in REVIEW."
        )
    return best


def _keyword_amount(lines: list[str], keywords) -> Decimal | None:
    """The amount on the LAST line matching any keyword (totals usually appear at the bottom)."""
    found = None
    for ln in lines:
        low = ln.lower()
        if any(k in low for k in keywords):
            amts = _amounts(ln)
            if amts:
                found = amts[-1]
    return found


def parse_invoice(text: str) -> dict:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    ccy = next((v for k, v in _CCY.items() if k in text), "USD")

    inv_no = (_INV_NO.search(text) or [None, None])[1] if _INV_NO.search(text) else None
    date_m = _DATE.search(text)
    date = date_m.group(1) if date_m else None
    # vendor: first non-empty line that isn't an "invoice"/number/date header
    vendor = None
    for ln in lines[:6]:
        low = ln.lower()
        if "invoice" in low or "bill" in low or _AMT.search(ln) or _DATE.match(ln):
            continue
        vendor = ln
        break

    total = _keyword_amount(lines, ("grand total", "total due", "balance due", "amount due"))
    if total is None:
        total = _keyword_amount(lines, ("total",))
    tax = _keyword_amount(lines, _TAX_KW)
    subtotal = _keyword_amount(lines, _SUBTOTAL_KW)

    # line items: lines with an amount that are NOT headers/totals/tax/subtotal
    items = []
    for ln in lines:
        low = ln.lower()
        if any(k in low for k in _TOTAL_KW + _TAX_KW + _SUBTOTAL_KW):
            continue
        if sum(k in low for k in _HEADER_KW) >= 2 and not _AMT.search(ln):
            continue                                   # a column-header row
        amts = _amounts(ln)
        if not amts:
            continue
        first = _AMT.search(ln)
        desc = ln[:first.start()].strip(" .:-\t|") if first else ln
        if not desc:
            continue
        items.append({"description": desc[:80], "amount": str(amts[-1])})

    return {"vendor": vendor, "invoice_number": inv_no, "date": date, "currency": ccy,
            "line_items": items, "subtotal": str(subtotal) if subtotal is not None else None,
            "tax": str(tax) if tax is not None else None,
            "total": str(total) if total is not None else None,
            "confidence": {"vendor": vendor is not None, "invoice_number": inv_no is not None,
                           "date": date is not None, "total": total is not None,
                           "line_items": len(items)}}


def to_bill_je(inv: dict, *, ap_account: str = "Liabilities:AP",
               expense_account: str = "Expenses:Uncategorized",
               tax_account: str = "Expenses:Sales Tax") -> dict:
    total = _dec(inv.get("total"))
    tax = _dec(inv.get("tax"))
    items = inv.get("line_items") or []
    # nothing extractable → no postable entry (do NOT emit a degenerate single-line/zero JE)
    if not items and tax == 0 and total == 0:
        return {"date": inv.get("date"), "memo": "Bill — (not extractable)", "source": "invoice",
                "lines": [], "reconciles": False, "postable": False, "total": "0",
                "note": "no line items, tax, or total found — extraction failed; review the source"}
    lines, dr = [], Decimal("0")
    for it in items:
        amt = _dec(it["amount"])
        lines.append({"account": expense_account, "debit": str(amt), "credit": "0",
                      "memo": it["description"]})
        dr += amt
    if tax:
        lines.append({"account": tax_account, "debit": str(tax), "credit": "0"})
        dr += tax
    # the AP credit is the stated total; plug any difference so the entry balances + flag it
    reconciles = (total != 0 and dr == total)
    if total == 0:
        total = dr                                     # no stated total → use the sum
    plug = total - dr
    if plug != 0:
        lines.append({"account": expense_account, "debit": str(plug) if plug > 0 else "0",
                      "credit": str(-plug) if plug < 0 else "0", "memo": "reconciling plug (REVIEW)"})
    vendor = (inv.get("vendor") or "vendor").strip()
    lines.append({"account": f"{ap_account}:{vendor[:30]}", "debit": "0", "credit": str(total)})
    return {"date": inv.get("date"), "memo": f"Bill — {vendor} {inv.get('invoice_number') or ''}".strip(),
            "source": "invoice", "lines": lines, "reconciles": reconciles, "postable": True,
            "total": str(total)}


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-invoice")
    ap.add_argument("input", nargs="?", default="-", help="invoice text file or '-' for stdin")
    ap.add_argument("--pdf", action="store_true", help="accepted for compatibility; PDF extraction is disabled")
    ap.add_argument("--je", action="store_true", help="also emit the draft AP bill journal entry")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    if a.input in (None, "-"):
        text = sys.stdin.read()
    elif a.pdf or a.input.lower().endswith(".pdf"):
        try:
            text = extract_text(a.input)
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
    else:
        text = Path(a.input).read_text(encoding="utf-8", errors="replace")
    inv = parse_invoice(text)
    je = to_bill_je(inv) if a.je else None
    if a.format == "json":
        print(json.dumps({"invoice": inv, "draft_entry": je}, indent=2, default=str))
    else:
        print(f"INVOICE — {inv['vendor'] or '(vendor not found)'}  #{inv['invoice_number'] or '?'}  {inv['date'] or '?'}")
        for it in inv["line_items"]:
            print(f"   {it['description'][:50]:<50}{_dec(it['amount']):>14,.2f}")
        for k in ("subtotal", "tax", "total"):
            if inv.get(k):
                print(f"   {k:<50}{_dec(inv[k]):>14,.2f}")
        missing = [k for k, v in inv["confidence"].items() if not v]
        if missing:
            print(f"   ⚠️ low confidence / not found: {', '.join(missing)} — REVIEW")
        if je:
            print(f"   draft AP entry {'✓ reconciles' if je['reconciles'] else '⚠️ does NOT reconcile (plugged) — REVIEW'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
