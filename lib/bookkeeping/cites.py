#!/usr/bin/env python3
"""glaw-cites — deterministic legal-citation EXTRACTOR (Free Law Project eyecite).

Pulls every case citation, short form, id., supra, statute, and law-journal cite
out of a brief / opinion / filing so /glaw-legal-research can VERIFY each one.
eyecite extracts; legal-research confirms. Input = a file path, or - / stdin.

Usage:
  glaw-cites <file>            human table
  glaw-cites <file> --json     JSON array (feed to /glaw-legal-research)
  cat brief.txt | glaw-cites - --json
"""
import sys, json, argparse
try:
    from eyecite import get_citations, clean_text
except ModuleNotFoundError:
    sys.exit("ERROR: glaw-cites requires 'eyecite' — install it into the bookkeeping venv: "
             "lib/bookkeeping/.venv/bin/python -m pip install eyecite")

ap = argparse.ArgumentParser()
ap.add_argument("path", nargs="?", default="-", help="file to scan (or - for stdin)")
ap.add_argument("--json", action="store_true")
a = ap.parse_args()

raw = (open(a.path, encoding="utf-8", errors="ignore").read()
       if a.path and a.path != "-" else sys.stdin.read())
if not raw.strip():                       # empty input: eyecite/lxml would crash on ""
    print("[]" if a.json else "0 citations (empty input).")
    sys.exit(0)
text = clean_text(raw, ["html", "all_whitespace"])
cites = get_citations(text)

rows = []
for c in cites:
    md = getattr(c, "metadata", None)
    rows.append({
        "type": type(c).__name__,
        "text": c.matched_text(),
        "year": getattr(md, "year", None) if md else None,
        "court": getattr(md, "court", None) if md else None,
        "pin_cite": getattr(md, "pin_cite", None) if md else None,
        "plaintiff": getattr(md, "plaintiff", None) if md else None,
        "defendant": getattr(md, "defendant", None) if md else None,
    })

if a.json:
    print(json.dumps(rows, indent=2))
else:
    full = sum(1 for r in rows if r["type"] == "FullCaseCitation")
    print(f"{len(rows)} citations ({full} full case cites):")
    for r in rows:
        extra = f"  ({r['year']})" if r["year"] else ""
        print(f"  [{r['type']}] {r['text']}{extra}")
    print("\nNext: verify each via /glaw-legal-research before it enters a filing.")
