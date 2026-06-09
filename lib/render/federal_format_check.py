#!/usr/bin/env python3
"""federal_format_check — AUTO-ASSERT that a .docx conforms to the Federal Filing Style Directive.
Opens the DOCX and checks the Normal style + section margins against the directive. Exit 0 = conforms;
exit 1 = non-conforming (prints each violation). The /glaw-file hard pre-check runs this on every
rendered federal filing, and glaw-doctor round-trips it. Usage: glaw-format-check <file.docx> [--json]
"""
from __future__ import annotations
import sys, argparse, json
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

REQ = {"font": "Times New Roman", "size_pt": 12, "line_spacing": 2.0,
       "alignment": "JUSTIFY", "first_line_indent_in": 0.5,
       "margin_top_in": 1.0, "margin_bottom_in": 1.0, "margin_left_in": 1.25, "margin_right_in": 1.0}

def check(path):
    doc = Document(path)
    st = doc.styles["Normal"]
    pf = st.paragraph_format
    sec = doc.sections[0]
    errs = []
    if st.font.name != REQ["font"]:
        errs.append(f"font is {st.font.name!r}, must be {REQ['font']!r}")
    if st.font.size != Pt(REQ["size_pt"]):
        errs.append(f"body size is {st.font.size.pt if st.font.size else None}pt, must be {REQ['size_pt']}pt")
    if pf.line_spacing != REQ["line_spacing"]:
        errs.append(f"line spacing is {pf.line_spacing}, must be {REQ['line_spacing']} (double)")
    if pf.alignment != WD_ALIGN_PARAGRAPH.JUSTIFY:
        errs.append(f"alignment is {pf.alignment}, must be JUSTIFY")
    if pf.first_line_indent != Inches(REQ["first_line_indent_in"]):
        got = round(pf.first_line_indent.inches, 3) if pf.first_line_indent else None
        errs.append(f"first-line indent is {got}\", must be {REQ['first_line_indent_in']}\"")
    for side, key in (("top", "margin_top_in"), ("bottom", "margin_bottom_in"),
                      ("left", "margin_left_in"), ("right", "margin_right_in")):
        got = getattr(sec, f"{side}_margin")
        if got != Inches(REQ[key]):
            errs.append(f"{side} margin is {round(got.inches,3)}\", must be {REQ[key]}\"")
    # page numbers present in the footer?
    if "PAGE" not in doc.sections[0].footer.paragraphs[0]._p.xml:
        errs.append("no page-number field in the footer")
    return errs

def main():
    ap = argparse.ArgumentParser(prog="glaw-format-check")
    ap.add_argument("docx")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        errs = check(a.docx)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}) if a.json else f"ERROR opening {a.docx}: {e}")
        return 2
    if a.json:
        print(json.dumps({"ok": not errs, "violations": errs}, indent=2))
    elif errs:
        print(f"✗ NON-CONFORMING — {a.docx}\n  Federal Filing Style Directive violations:")
        for e in errs:
            print(f"    - {e}")
    else:
        print(f"✓ CONFORMS to the Federal Filing Style Directive — {a.docx}")
        print("  TNR 12pt · double-spaced · justified · 0.5\" indent · margins 1/1/1.25/1 · page #s")
    return 1 if errs else 0

if __name__ == "__main__":
    raise SystemExit(main())
