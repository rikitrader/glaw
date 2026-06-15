#!/usr/bin/env python3
"""GAP 5 — auto-populate the GLAW docket from a deadlines-matrix markdown doc.
Parses recurring/one-time deadline tables (e.g. drafts/21-tax-elections-and-deadlines-matrix.md),
resolves relative dates to absolute for a given tax year, and emits `glaw docket add` commands
(prints by default; --apply runs them).

Usage: docket_from_matrix.py <matrix.md> --source SRC-0001 [--owner "tax docket clerk"] [--year 2026] [--apply]
"""
import argparse
import re
import shlex
import subprocess
import datetime as dt
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
    ap = argparse.ArgumentParser(
        description="Emit source-backed glaw docket add commands from a deadline matrix."
    )
    ap.add_argument("matrix")
    ap.add_argument("--year", type=int, default=dt.date.today().year + 1)
    ap.add_argument("--owner", default="tax docket clerk")
    ap.add_argument("--source", required=True, help="current matter source ID supporting the matrix, e.g. SRC-0001")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    txt = Path(args.matrix).read_text(encoding="utf-8")
    cmds = []
    for line in txt.splitlines():
        if not line.strip().startswith('|'): continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 2: continue
        # first cell often holds a bold date like **May 1** or **Apr 15**
        date_cell = re.sub(r'[*`]', '', cells[0]).strip()
        iso = resolve(date_cell, args.year)
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
    print(f"# {len(out)} deadlines parsed from {Path(args.matrix).name} (year {args.year})")
    for iso, desc in out:
        command = [
            "glaw",
            "docket",
            "add",
            "--owner",
            args.owner,
            "--source",
            args.source,
            iso,
            desc,
        ]
        print(" ".join(shlex.quote(part) for part in command))
        if args.apply:
            subprocess.run(
                [GLAW, "docket", "add", "--owner", args.owner, "--source", args.source, iso, desc],
                check=False,
            )
    if not args.apply:
        print("\n# dry-run; re-run with --apply to write to the docket")

if __name__ == '__main__':
    main()
