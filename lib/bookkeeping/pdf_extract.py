#!/usr/bin/env python3
"""PDF/OCR front-end for GLAW bookkeeping.

This module stays package-free: all orchestration and parsing lives in the repo,
and OCR/PDF rendering is delegated to local command-line tools when installed:

- `opendataloader-pdf` or `pdftotext` for digital PDFs
- `pdftoppm` + `tesseract` for scanned PDFs

If those binaries are unavailable, the tool fails with a clean operator message.
"""
from __future__ import annotations

import csv
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

_AMOUNT_CLEAN = re.compile(r"[,$\s]")
_BAL = re.compile(r"(opening|closing)\s+balance[:\s]*\$?\s*(-?[\d,]+\.?\d*)", re.IGNORECASE)
_HEADER_HINTS = ("date", "description", "amount", "debit", "credit", "memo", "details")
_SLASH_DATE = re.compile(r"^\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\s*$")
_OCR_LINE = re.compile(
    r"^\s*(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+"
    r"(?P<desc>.+?)\s+"
    r"(?P<amt>\(?-?\$?\s?[\d,]+\.\d{2}\)?)\s*(?P<sign>CR|DR)?\s*$",
    re.IGNORECASE,
)

_PROFILES = {
    "bank-statement": {"dpi": (300, 240, 360), "psm": ("4", "6")},
    "dense": {"dpi": (360, 300, 240), "psm": ("6", "4", "11")},
    "simple": {"dpi": (240, 300), "psm": ("6", "4")},
}


class PDFExtractionUnavailable(RuntimeError):
    """Raised when local PDF/OCR tooling is unavailable or cannot parse rows."""


def _need(cmd: str) -> str:
    path = shutil.which(cmd)
    if not path:
        raise PDFExtractionUnavailable(
            f"PDF/OCR ingestion needs local binary `{cmd}`. Install OCR tooling "
            "or export the statement from Google Sheets/your bank as CSV."
        )
    return path


def _clean_amount(cell: str) -> str:
    c = cell.strip().replace("(", "-").replace(")", "")
    return _AMOUNT_CLEAN.sub("", c)


def _split_md_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _normalize_dates(rows: list[list[str]], date_col: int) -> list[list[str]]:
    parsed = [(_SLASH_DATE.match(r[date_col]) if date_col < len(r) else None) for r in rows]
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
            pass
    return rows


def _rows_to_csv(header: list[str], rows: list[list[str]], date_col: int | None, out_csv: Path) -> Path:
    if date_col is not None and date_col >= 0:
        rows = _normalize_dates(rows, date_col)
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
    return out_csv


def _extract_markdown(pdf_path: Path, work: Path) -> str:
    odl = shutil.which("opendataloader-pdf")
    if odl:
        proc = subprocess.run(
            [odl, "-o", str(work), "-f", "markdown", str(pdf_path)],
            capture_output=True, text=True,
        )
        md_files = list(work.glob("*.md"))
        if proc.returncode == 0 and md_files:
            text = md_files[0].read_text(encoding="utf-8", errors="replace")
            if text.strip():
                return text

    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        out = work / "pdftotext.txt"
        proc = subprocess.run([pdftotext, "-layout", str(pdf_path), str(out)], capture_output=True, text=True)
        if proc.returncode == 0 and out.exists():
            text = out.read_text(encoding="utf-8", errors="replace")
            if text.strip():
                return text

    return ""


def _rows_from_text(text: str) -> tuple[list[str], list[list[str]], dict]:
    meta: dict = {}
    for kind, val in _BAL.findall(text):
        meta[f"{kind.lower()}_balance"] = _clean_amount(val)

    lines = text.splitlines()
    header_idx = None
    header_cols: list[str] = []
    for i, line in enumerate(lines):
        if line.strip().startswith("|"):
            cols = [c.lower() for c in _split_md_row(line)]
            if sum(any(h in c for h in _HEADER_HINTS) for c in cols) >= 2:
                header_idx = i
                header_cols = _split_md_row(line)
                break

    if header_idx is not None:
        lower = [c.lower() for c in header_cols]
        amount_like = {j for j, c in enumerate(lower) if any(k in c for k in ("amount", "debit", "credit"))}
        rows: list[list[str]] = []
        for line in lines[header_idx + 1:]:
            s = line.strip()
            if not s.startswith("|"):
                if rows:
                    break
                continue
            cells = _split_md_row(line)
            if set(cells) <= {"", "---"} or all(set(c) <= {"-", ":"} for c in cells):
                continue
            if len(cells) != len(header_cols):
                continue
            for j in amount_like:
                cells[j] = _clean_amount(cells[j])
            rows.append(cells)
        if rows:
            return header_cols, rows, meta

    rows = []
    for line in lines:
        m = _OCR_LINE.match(line)
        if not m:
            continue
        amt = _clean_amount(m.group("amt"))
        if (m.group("sign") or "").upper() == "DR" and not amt.startswith("-"):
            amt = "-" + amt
        rows.append([m.group("date").strip(), m.group("desc").strip(), amt])
    return ["Date", "Description", "Amount"], rows, meta


def _ocr_text(pdf_path: Path, work: Path, *, profile: str = "bank-statement") -> tuple[str, int, dict]:
    pdftoppm = _need("pdftoppm")
    tesseract = _need("tesseract")
    cfg = _PROFILES.get(profile, _PROFILES["bank-statement"])
    best = {"text": "", "pages": 0, "dpi": None, "psm": None}
    last_error = ""
    for dpi in cfg["dpi"]:
        prefix = work / f"page-{dpi}"
        try:
            subprocess.run([pdftoppm, "-r", str(dpi), "-png", str(pdf_path), str(prefix)],
                           check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as exc:
            last_error = (exc.stderr or exc.stdout or str(exc)).strip()
            continue
        pages = sorted(work.glob(f"page-{dpi}*.png"))
        if not pages:
            continue
        for psm in cfg["psm"]:
            parts = []
            for png in pages:
                proc = subprocess.run([tesseract, str(png), "stdout", "--psm", psm],
                                      capture_output=True, text=True)
                parts.append(proc.stdout if proc.returncode == 0 else "")
            text = "\n".join(parts)
            if len(text) > len(str(best["text"])):
                best = {"text": text, "pages": len(pages), "dpi": dpi, "psm": psm}
    if not best["text"]:
        raise PDFExtractionUnavailable(
            f"Could not render/OCR PDF pages with local tools: {last_error or 'no OCR text produced'}"
        )
    return str(best["text"]), int(best["pages"]), {"ocr_dpi": best["dpi"], "ocr_psm": best["psm"], "ocr_profile": profile}


def extract_to_csv(pdf_path: str | Path, *, out_csv: str | Path | None = None,
                   ocr: str = "auto", profile: str = "bank-statement") -> tuple[Path, dict]:
    pdf_path = Path(pdf_path)
    work = Path(tempfile.mkdtemp(prefix="glaw-pdf-"))
    out_csv = Path(out_csv) if out_csv else work / "extracted.csv"

    text = "" if ocr == "force" else _extract_markdown(pdf_path, work)
    header, rows, meta = _rows_from_text(text) if text else (["Date", "Description", "Amount"], [], {})
    source = "pdf_text"

    if not rows:
        if ocr == "off":
            raise PDFExtractionUnavailable(
                f"No transaction table found in {pdf_path.name}; OCR disabled with --ocr off."
            )
        text, pages, ocr_meta = _ocr_text(pdf_path, work, profile=profile)
        header, rows, meta = _rows_from_text(text)
        meta["ocr_pages"] = pages
        meta.update(ocr_meta)
        source = "ocr"

    if not rows:
        raise PDFExtractionUnavailable(
            f"No transaction rows found in {pdf_path.name}. Export the sheet/bank data as CSV."
        )

    date_cols = [j for j, c in enumerate([h.lower() for h in header]) if "date" in c]
    _rows_to_csv(header, rows, date_cols[0] if date_cols else None, out_csv)
    meta["rows"] = len(rows)
    meta["source_pdf"] = str(pdf_path)
    meta["source_method_hint"] = source
    if source == "ocr":
        meta.setdefault("warnings", [])
        if len(rows) < 2:
            meta["warnings"].append("low-confidence OCR: fewer than two transaction rows parsed")
    return out_csv, meta


if __name__ == "__main__":
    import json
    import sys
    try:
        csv_path, metadata = extract_to_csv(sys.argv[1])
    except PDFExtractionUnavailable as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
    print(csv_path)
    print(json.dumps(metadata, indent=2))
