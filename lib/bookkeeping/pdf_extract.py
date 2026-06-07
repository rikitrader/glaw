#!/usr/bin/env python3
"""PDF front-end for GLAW bookkeeping — deterministic, no LLM.

Two paths, both local and $0:

1. **Digital (text) PDFs** — `opendataloader-pdf` turns the PDF into markdown; we
   lift the transaction table out and write a normalized CSV that the engine's
   CsvStatementParser already knows how to read.
2. **Scanned / image-only PDFs** (`ocr_pdf_to_csv`) — when path 1 finds no table,
   rasterize each page with `pdftoppm` (poppler) and OCR it with `tesseract`, then
   parse one-transaction-per-line text into rows. No model, no API, no daemon.

Also sniffs opening/closing balances so the Golden Rule can run without the user
supplying them.

External OS binaries required: `opendataloader-pdf`, and for the scanned path
`tesseract` + `pdftoppm`. All parsing logic lives here inside GLAW.
"""
from __future__ import annotations

import csv
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

_AMOUNT_CLEAN = re.compile(r"[,$\s]")
_BAL = re.compile(r"(opening|closing)\s+balance[:\s]*\$?\s*(-?[\d,]+\.?\d*)", re.IGNORECASE)
# A markdown table header row that looks like a transaction table.
_HEADER_HINTS = ("date", "description", "amount", "debit", "credit", "memo", "details")


def _clean_amount(cell: str) -> str:
    c = cell.strip().replace("(", "-").replace(")", "")
    return _AMOUNT_CLEAN.sub("", c)


def _split_md_row(line: str) -> list[str]:
    # "|a|b|c|" -> ["a","b","c"]
    return [c.strip() for c in line.strip().strip("|").split("|")]


_SLASH_DATE = re.compile(r"^\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\s*$")


def _normalize_dates(rows: list[list[str]], date_col: int) -> list[list[str]]:
    """Convert a slash/dash date column to ISO (YYYY-MM-DD).

    Detects day-first vs month-first per column: if ANY row's first field is
    >12 the column is day-first; otherwise assume US month-first (the dominant
    format for these matters). ISO dates already in the column pass through.
    Rows that cannot be parsed keep their original value (never dropped).
    """
    parsed = [(_SLASH_DATE.match(r[date_col]) if date_col < len(r) else None)
              for r in rows]
    firsts = [int(m.group(1)) for m in parsed if m]
    day_first = any(f > 12 for f in firsts)
    for r, m in zip(rows, parsed):
        if not m:
            continue
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100:
            y += 2000
        day, month = (a, b) if day_first else (b, a)
        try:
            r[date_col] = datetime(y, month, day).date().isoformat()
        except ValueError:
            pass  # leave as-is rather than lose the row
    return rows


# One transaction per OCR line: a date near the start, an amount at the end,
# description in between. Handles $, commas, parens-negatives, trailing CR/DR.
_OCR_LINE = re.compile(
    r"^\s*(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+"
    r"(?P<desc>.+?)\s+"
    r"(?P<amt>\(?-?\$?\s?[\d,]+\.\d{2}\)?)\s*(?P<sign>CR|DR)?\s*$",
    re.IGNORECASE,
)


def ocr_pdf_to_rows(pdf_path: str | Path, *, dpi: int = 300) -> tuple[list[list[str]], dict]:
    """OCR a scanned PDF into [[date, description, amount], ...] rows.

    Rasterizes with `pdftoppm`, OCRs each page with `tesseract` (psm 6 = a block
    of text, good for statement tables). Pure subprocess — no Python OCR deps.
    """
    pdf_path = Path(pdf_path)
    work = Path(tempfile.mkdtemp(prefix="glaw-ocr-"))
    # 1) PDF -> page PNGs
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(pdf_path),
                    str(work / "page")], check=True, capture_output=True)
    pages = sorted(work.glob("page*.png"))
    if not pages:
        raise RuntimeError(f"pdftoppm produced no page images for {pdf_path.name}")

    # psm 4 = "a single column of text of variable sizes" — keeps each statement
    # line intact (date … description … amount), which psm 6 tends to fragment.
    text_parts: list[str] = []
    for png in pages:
        out = subprocess.run(["tesseract", str(png), "stdout", "--psm", "4"],
                             capture_output=True, text=True)
        text_parts.append(out.stdout)
    text = "\n".join(text_parts)

    meta: dict = {}
    for kind, val in _BAL.findall(text):
        meta[f"{kind.lower()}_balance"] = _clean_amount(val)

    rows: list[list[str]] = []
    for line in text.splitlines():
        m = _OCR_LINE.match(line)
        if not m:
            continue
        amt = _clean_amount(m.group("amt"))
        if (m.group("sign") or "").upper() == "DR" and not amt.startswith("-"):
            amt = "-" + amt
        rows.append([m.group("date").strip(), m.group("desc").strip(), amt])

    meta["rows"] = len(rows)
    meta["source_pdf"] = str(pdf_path)
    meta["ocr_pages"] = len(pages)
    return rows, meta


def _rows_to_csv(header: list[str], rows: list[list[str]],
                 date_col: int | None, out_csv: Path) -> Path:
    if date_col is not None and date_col >= 0:
        rows = _normalize_dates(rows, date_col)
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    return out_csv


def extract_to_csv(pdf_path: str | Path, *, out_csv: str | Path | None = None,
                   ocr: str = "auto") -> tuple[Path, dict]:
    """Extract the transaction table from ``pdf_path`` into a CSV.

    Returns (csv_path, meta) where meta may carry opening/closing balances.
    Raises RuntimeError if no transaction table can be found.
    """
    pdf_path = Path(pdf_path)
    work = Path(tempfile.mkdtemp(prefix="glaw-pdf-"))
    out_csv = Path(out_csv) if out_csv else work / "extracted.csv"

    def _ocr_fallback(reason: str) -> tuple[Path, dict]:
        if ocr == "off":
            raise RuntimeError(f"{reason} (OCR disabled with ocr='off').")
        rows, meta = ocr_pdf_to_rows(pdf_path)
        if not rows:
            raise RuntimeError(
                f"{reason} OCR via tesseract also found no transaction lines "
                f"({meta.get('ocr_pages', 0)} pages scanned). The statement layout "
                "may be non-tabular, or the scan quality too low.")
        meta["source_method_hint"] = "ocr"
        _rows_to_csv(["Date", "Description", "Amount"], rows, 0, out_csv)
        return out_csv, meta

    if ocr == "force":
        return _ocr_fallback("Forced OCR.")

    proc = subprocess.run(
        ["opendataloader-pdf", "-o", str(work), "-f", "markdown", str(pdf_path)],
        capture_output=True, text=True,
    )
    md_files = list(work.glob("*.md"))
    if proc.returncode != 0 or not md_files:
        return _ocr_fallback(
            f"opendataloader-pdf produced no markdown for {pdf_path.name}.")
    md = md_files[0].read_text(encoding="utf-8")

    # Balances (best effort)
    meta: dict = {}
    for kind, val in _BAL.findall(md):
        meta[f"{kind.lower()}_balance"] = _clean_amount(val)

    # Find the transaction table: a header row with >=2 hint columns, then rows.
    lines = md.splitlines()
    header_idx = None
    header_cols: list[str] = []
    for i, line in enumerate(lines):
        if line.strip().startswith("|"):
            cols = [c.lower() for c in _split_md_row(line)]
            if sum(any(h in c for h in _HEADER_HINTS) for c in cols) >= 2:
                header_idx = i
                header_cols = _split_md_row(line)
                break
    if header_idx is None:
        # No tabular text layer — almost always a scanned/image-only PDF.
        return _ocr_fallback(f"No text transaction table in {pdf_path.name}.")

    # Locate the amount-bearing column(s) to clean numerics
    lower = [c.lower() for c in header_cols]
    amount_like = {j for j, c in enumerate(lower)
                   if any(k in c for k in ("amount", "debit", "credit"))}

    rows: list[list[str]] = []
    for line in lines[header_idx + 1:]:
        s = line.strip()
        if not s.startswith("|"):
            if rows:
                break          # table ended
            continue
        cells = _split_md_row(line)
        if set(cells) <= {"", "---"} or all(set(c) <= {"-", ":"} for c in cells):
            continue           # markdown separator row
        if len(cells) != len(header_cols):
            continue
        for j in amount_like:
            cells[j] = _clean_amount(cells[j])
        rows.append(cells)

    if not rows:
        return _ocr_fallback(f"Table in {pdf_path.name} had a header but no rows.")

    # Normalize the date column to ISO so the CSV parser never drops US-format rows.
    date_cols = [j for j, c in enumerate(lower) if "date" in c]
    _rows_to_csv(header_cols, rows, date_cols[0] if date_cols else None, out_csv)
    meta["rows"] = len(rows)
    meta["source_pdf"] = str(pdf_path)
    return out_csv, meta


if __name__ == "__main__":
    import json
    import sys
    csv_path, meta = extract_to_csv(sys.argv[1])
    print(csv_path)
    print(json.dumps(meta, indent=2))
