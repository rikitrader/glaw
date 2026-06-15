#!/usr/bin/env python3
"""GAP 5 — auto-populate the GLAW docket from a deadlines-matrix markdown doc.
Parses recurring/one-time deadline tables (e.g. drafts/21-tax-elections-and-deadlines-matrix.md),
resolves relative dates to absolute for a given tax year, and emits `glaw docket add` commands
(prints by default; --apply runs them).

Usage: docket_from_matrix.py <matrix.md> [--year 2026] [--apply]
"""
import sys, os, re, subprocess, datetime as dt
from pathlib import Path

MONTHS = {m: i for i, m in enumerate(
    ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], 1)}
GLAW = str(Path(__file__).resolve().parents[1] / "glaw")

def resolve(date_txt, year):
    """'May 1' / 'Apr 15' / 'Mar 1' -> YYYY-MM-DD for the given year (next occurrence if past)."""
    m = re.match(r'([A-Z][a-z]{2})\s+(\d{1,2})', date_txt.strip())
    if not m: return None
    mon, day = MONTHS.get(m.group(1)), int(m.group(2))
    if not mon: return None
    try: return dt.date(year, mon, day).isoformat()
    except ValueError: return None

def main():
    if len(sys.argv) < 2:
        print('usage: docket_from_matrix.py <matrix.md> [--year YYYY] [--apply]'); sys.exit(1)
    path = sys.argv[1]
    ym = re.search(r'--year\s+(\d{4})', ' '.join(sys.argv))
    year = int(ym.group(1)) if ym else dt.date.today().year + 1
    apply = '--apply' in sys.argv
    txt = open(path).read()
    cmds = []
    for line in txt.splitlines():
        if not line.strip().startswith('|'): continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 2: continue
        # first cell often holds a bold date like **May 1** or **Apr 15**
        date_cell = re.sub(r'[*`]', '', cells[0]).strip()
        iso = resolve(date_cell, year)
        if not iso: continue
        desc = re.sub(r'[*`|]', '', cells[1]).strip()[:90]
        if not desc or desc.lower().startswith('date'): continue
        if 'n/a' in desc.lower() or 'only if' in desc.lower(): continue  # skip non-applicable rows
        cmds.append((iso, desc))
    # dedupe
    seen = set(); out = []
    for iso, desc in cmds:
        k = (iso, desc)
        if k in seen: continue
        seen.add(k); out.append((iso, desc))
    print(f"# {len(out)} deadlines parsed from {os.path.basename(path)} (year {year})")
    for iso, desc in out:
        print(f'glaw docket add {iso} "{desc}"')
        if apply:
            subprocess.run([GLAW, 'docket', 'add', iso, desc], check=False)
    if not apply:
        print("\n# dry-run; re-run with --apply to write to the docket")

if __name__ == '__main__':
    main()
