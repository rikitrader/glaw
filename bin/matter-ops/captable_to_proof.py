#!/usr/bin/env python3
"""GAP 2 — cap-table CSV/JSON export -> §351 control proof + §1202 per-holder register.
Canonical sample = the Example Holdings Carta workbook ("Cap Table View" tab). Any future corp clones that
workbook; this reader is HEADER-DRIVEN, so it works on any copy with the same column names:
  Stakeholder | Type | Share Class | Security Type | Shares | Investment Value | Ownership % (Basic) | Ownership % (FD)

Usage: captable_to_proof.py captable.csv
"""
import csv, json, sys, os, re

SHEET = os.environ.get("GLAW_CAPTABLE_FILE", "")
TAB = "Cap Table View"

def num(s):
    try: return float(re.sub(r"[,\s$%]", "", str(s)))
    except: return None

def col(headers, *names):
    low = [h.strip().lower() for h in headers]
    for n in names:
        for i, h in enumerate(low):
            if n in h: return i
    return None

def load_rows(path):
    if not path:
        return []
    if path.endswith(".json"):
        data = json.load(open(path, encoding="utf-8"))
        return data.get("values", data if isinstance(data, list) else [])
    return list(csv.reader(open(path, encoding="utf-8")))

def main():
    sid = next((a for a in sys.argv[1:] if not a.startswith("--")), SHEET)
    m = re.search(r'--tab\s+"?([^"]+)"?', " ".join(sys.argv))
    tab = m.group(1) if m else TAB
    rows = load_rows(sid)
    if not rows:
        print("no rows; pass a CSV/JSON cap table export path")
        return
    hdr = rows[0]
    ci = {k: col(hdr, *v) for k, v in {
        "name": ("stakeholder", "name"), "type": ("type",), "class": ("share class", "class"),
        "sec": ("security",), "shares": ("shares",), "inv": ("investment",)}.items()}
    if ci["name"] is None or ci["shares"] is None:
        print("could not find Stakeholder/Shares columns; headers:", hdr); return

    holders, total_row = [], None
    for r in rows[1:]:
        if len(r) <= ci["name"]: continue
        name = (r[ci["name"]] or "").strip()
        if not name: continue
        if name.upper().startswith("TOTAL"):
            total_row = num(r[ci["shares"]]) if len(r) > ci["shares"] else None
            continue
        sh = num(r[ci["shares"]]) if len(r) > ci["shares"] else None
        if sh is None: continue
        holders.append({
            "name": name,
            "type": (r[ci["type"]].strip().upper() if ci["type"] is not None and len(r) > ci["type"] else ""),
            "class": (r[ci["class"]].strip() if ci["class"] is not None and len(r) > ci["class"] else ""),
            "sec": (r[ci["sec"]].strip() if ci["sec"] is not None and len(r) > ci["sec"] else ""),
            "shares": sh})
    total = total_row or sum(h["shares"] for h in holders) or 1
    founders = [h for h in holders if h["type"] == "FOUNDER"]
    fctl = sum(h["shares"] for h in founders) / total * 100

    print(f"## §351 control + §1202 register (auto-generated from cap table)")
    print(f"Source: {sid}\n")
    print("| Stakeholder | Type | Share Class | Security | Shares | % (FD) | QSBS? |")
    print("|---|---|---|---|---:|---:|---|")
    for h in holders:
        qsbs = "candidate" if (h["sec"].upper() == "STOCK" and h["type"] in ("FOUNDER", "INVESTOR")) else "— (option/other)"
        print(f"| {h['name']} | {h['type']} | {h['class']} | {h['sec']} | {int(h['shares']):,} | {h['shares']/total*100:.2f}% | {qsbs} |")
    print(f"| **Total** |  |  |  | **{int(total):,}** | 100% | |\n")

    print(f"**§368(c) control check:** founder group ({', '.join(h['name'] for h in founders)}) holds "
          f"**{fctl:.2f}%** of shares.")
    if fctl >= 80:
        print("-> OK: >=80% — §351 control satisfied (founders alone).")
    else:
        print(f"-> WARNING: {fctl:.2f}% < 80% — founders ALONE do NOT meet §368(c) control. §351 nonrecognition for "
              f"the IP-for-stock contribution requires the property-contributing group to hold >=80% IMMEDIATELY AFTER. "
              f"FIX: issue founder stock (and any co-contributors in the same §351 transaction) BEFORE the priced "
              f"preferred round; do NOT let the Seed/Series-A issuance be part of the same transaction as the founder "
              f"IP contribution.")
    print("\n> §1202: only STOCK (not options) is QSBS-eligible, and only if each issuer test is met. "
          "Paste into doc 18 §4 (control proof) + doc 17 §2 (per-holder register). Re-run after any issuance.")

if __name__ == "__main__":
    main()
