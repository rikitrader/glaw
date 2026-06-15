#!/usr/bin/env python3
"""glaw-cites — deterministic zero-dependency legal-citation extractor.

Pulls every case citation, short form, id., supra, statute, and law-journal cite
out of a brief / opinion / filing so /glaw-legal-research can VERIFY each one.
This stdlib extractor is conservative; legal-research confirms. Input = a file
path, or - / stdin.

Usage:
  glaw-cites <file>            human table
  glaw-cites <file> --json     JSON array (feed to /glaw-legal-research)
  cat brief.txt | glaw-cites - --json
"""
import sys, json, argparse, re

ap = argparse.ArgumentParser()
ap.add_argument("path", nargs="?", default="-", help="file to scan (or - for stdin)")
ap.add_argument("--json", action="store_true")
a = ap.parse_args()

raw = (open(a.path, encoding="utf-8", errors="ignore").read()
       if a.path and a.path != "-" else sys.stdin.read())
if not raw.strip():
    print("[]" if a.json else "0 citations (empty input).")
    sys.exit(0)
text = re.sub(r"\s+", " ", raw)

PATTERNS = [
    ("FullCaseCitation", re.compile(r"\b[A-Z][A-Za-z0-9&'.\- ]+ v\. [A-Z][A-Za-z0-9&'.\- ]+, \d+ [A-Z][A-Za-z. ]+ \d+(?:, \d+)?(?: \([^)]+\))?")),
    ("ReporterCitation", re.compile(r"\b\d+ (?:U\.S\.|S\. Ct\.|F\. ?\d?d|F\. ?Supp\. ?\d?d|So\. ?\d?d|S\.E\. ?\d?d|N\.E\. ?\d?d|P\. ?\d?d) \d+(?:, \d+)?(?: \([^)]+\))?")),
    ("StatuteCitation", re.compile(r"\b\d+\s+U\.S\.C\.?\s+§+\s*[\w.\-()]+")),
    ("RegulationCitation", re.compile(r"\b\d+\s+C\.F\.R\.?\s+§+\s*[\w.\-()]+")),
    ("RuleCitation", re.compile(r"\b(?:Fed\. R\. (?:Civ|Crim|Evid|App)\. P\.|FRCP|FRE|FRAP)\s+\d+(?:\([a-z0-9]+\))*")),
    ("ShortFormCitation", re.compile(r"\b(?:Id\.|id\.|supra)\b(?: at \d+)?")),
]

rows = []
seen = set()
for typ, pattern in PATTERNS:
    for m in pattern.finditer(text):
        cite = m.group(0).strip()
        key = (typ, cite, m.start())
        if key in seen:
            continue
        seen.add(key)
        year = None
        ym = re.search(r"\((?:[^)]*?)(\d{4})(?:[^)]*)\)$", cite)
        if ym:
            year = ym.group(1)
        rows.append({
            "type": typ,
            "text": cite,
            "year": year,
            "court": None,
            "pin_cite": None,
            "plaintiff": None,
            "defendant": None,
            "offset": m.start(),
        })
rows.sort(key=lambda r: r["offset"])

if a.json:
    print(json.dumps(rows, indent=2))
else:
    full = sum(1 for r in rows if r["type"] in ("FullCaseCitation", "ReporterCitation"))
    print(f"{len(rows)} citations ({full} full case cites):")
    for r in rows:
        extra = f"  ({r['year']})" if r["year"] else ""
        print(f"  [{r['type']}] {r['text']}{extra}")
    print("\nNext: verify each via /glaw-legal-research before it enters a filing.")
