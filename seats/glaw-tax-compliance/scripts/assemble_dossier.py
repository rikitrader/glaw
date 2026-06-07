#!/usr/bin/env python3
"""Assemble a filing dossier: generate a cover sheet + table of contents + filing
checklist, then merge it ahead of the listed PDFs into one combined packet.

The cover/TOC/checklist is generated with reportlab; the merge uses pypdf. The result is
a single review-and-sign packet — it is NOT submitted anywhere.

Usage:
    python3 assemble_dossier.py MANIFEST.json OUT.pdf

MANIFEST.json schema:
{
  "title": "IRS Filing Packet",
  "taxpayer": "Jane Q. Taxpayer  •  SSN xxx-xx-1234",
  "prepared": "2026-06-04",
  "items": [
    {"label": "Form 843 — Penalty Abatement (TY2022)", "file": "843_filled.pdf",
     "mail_to": "see Form 843 instructions / your CP notice address", "notes": "sign + date p.1"},
    {"label": "Reasonable-cause letter", "file": "rc_letter.pdf"}
  ],
  "checklist": ["Sign every form", "Attach medical records", "Send certified mail, return receipt"],
  "mailing": "Verify the correct address on each form's instructions or IRS 'Where to File'."
}
"""
import sys
import json
import io
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def cover_pdf(m: dict) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    w, h = letter
    y = h - 1 * inch

    c.setFont("Helvetica-Bold", 20)
    c.drawString(1 * inch, y, m.get("title", "IRS Filing Packet"))
    y -= 0.4 * inch
    c.setFont("Helvetica", 11)
    if m.get("taxpayer"):
        c.drawString(1 * inch, y, m["taxpayer"]); y -= 0.25 * inch
    if m.get("prepared"):
        c.drawString(1 * inch, y, f"Prepared: {m['prepared']}"); y -= 0.25 * inch
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(1 * inch, y, "DRAFT — review every entry and SIGN before filing. Not submitted to the IRS.")
    y -= 0.45 * inch

    c.setFont("Helvetica-Bold", 13)
    c.drawString(1 * inch, y, "Contents"); y -= 0.3 * inch
    c.setFont("Helvetica", 10)
    for i, it in enumerate(m.get("items", []), 1):
        line = f"{i}.  {it.get('label', it.get('file', ''))}"
        c.drawString(1.1 * inch, y, line[:95]); y -= 0.22 * inch
        if it.get("mail_to"):
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(1.4 * inch, y, f"mail to: {it['mail_to']}"[:90]); y -= 0.18 * inch
            c.setFont("Helvetica", 10)
        if it.get("notes"):
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(1.4 * inch, y, f"note: {it['notes']}"[:90]); y -= 0.18 * inch
            c.setFont("Helvetica", 10)
        if y < 1.5 * inch:
            c.showPage(); y = h - 1 * inch; c.setFont("Helvetica", 10)

    if m.get("checklist"):
        if y < 3 * inch:
            c.showPage(); y = h - 1 * inch
        c.setFont("Helvetica-Bold", 13)
        c.drawString(1 * inch, y, "Filing checklist"); y -= 0.3 * inch
        c.setFont("Helvetica", 10)
        for item in m["checklist"]:
            c.drawString(1.1 * inch, y, f"[ ]  {item}"[:95]); y -= 0.24 * inch
            if y < 1.2 * inch:
                c.showPage(); y = h - 1 * inch; c.setFont("Helvetica", 10)

    if m.get("mailing"):
        if y < 1.6 * inch:
            c.showPage(); y = h - 1 * inch
        y -= 0.1 * inch
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1 * inch, y, "Mailing"); y -= 0.24 * inch
        c.setFont("Helvetica", 9)
        c.drawString(1.1 * inch, y, m["mailing"][:100])

    c.showPage()
    c.save()
    return buf.getvalue()


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        m = json.load(f)
    out = sys.argv[2]

    writer = PdfWriter()
    writer.append(PdfReader(io.BytesIO(cover_pdf(m))))

    missing = []
    for it in m.get("items", []):
        path = it.get("file")
        if not path:
            continue
        try:
            writer.append(PdfReader(path))
        except Exception as e:
            missing.append(f"{path} ({e})")

    with open(out, "wb") as f:
        writer.write(f)
    print(f"OK    assembled {out}  ({len(m.get('items', []))} items + cover)")
    for x in missing:
        print(f"WARN  could not append: {x}", file=sys.stderr)
    print("NOTE  packet is for review/signature only — not transmitted to the IRS.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
