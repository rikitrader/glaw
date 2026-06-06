#!/usr/bin/env python3
"""GLAW facts gate — the intake form that decides RUN vs STOP for the Chief loop.
A matter cannot reach BULLETPROOF while real facts are missing, so a live loop on a
fact-incomplete matter only burns budget grinding to DRAFTING-CLEAN. This gate is the
machine-readable intake: fill the 8 facts, and ONLY when READY may the live loop run.

Facts file: $GLAW_HOME/matters/<slug>/facts.json (default ~/.glaw)

Usage:
  facts_gate.py init   <slug>                 # create the blank 8-fact intake
  facts_gate.py set    <slug> <key> "<value>" # fill one fact
  facts_gate.py status <slug>                 # human table + READY/BLOCKED
  facts_gate.py check  <slug>                 # machine: prints READY or BLOCKED + missing; exit 0/1
"""
import sys, os, json

# The 8 facts (keys) + human labels. A fact counts as MISSING if empty or contains [VERIFY]/TBD/?.
FACTS = [
    ("issuance_date",       "Founder-stock issuance date (after 7/4/2025 for OBBBA QSBS)"),
    ("cap_table",           "Founder names + exact share splits + par + option pool"),
    ("gross_assets",        "Gross-assets balance sheet at issuance (cash + adj. basis)"),
    ("ip_valuation",        "Third-party IP valuation (independent, not CEO-signed)"),
    ("ein_hq",              "EIN + principal HQ address"),
    ("controlled_group",    "§52/§448(c) controlled-group determination"),
    ("residence_state",     "State of residence at sale + marital characterization"),
    ("valuation_409a",      "409A valuation (independent appraiser)"),
]
KEYS = [k for k, _ in FACTS]

def glaw_home():
    # Respect $GLAW_HOME (matches bin/glaw); default to ~/.glaw.
    return os.environ.get("GLAW_HOME") or os.path.expanduser("~/.glaw")

def path(slug):
    return os.path.join(glaw_home(), "matters", slug, "facts.json")

def load(slug):
    p = path(slug)
    return json.load(open(p)) if os.path.exists(p) else {}

def missing(d):
    bad = lambda v: (not v) or any(t in str(v).upper() for t in ("[VERIFY", "TBD", "????"))
    return [(k, lbl) for k, lbl in FACTS if bad(d.get(k))]

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    cmd, slug = sys.argv[1], sys.argv[2]
    if cmd == "init":
        p = path(slug); os.makedirs(os.path.dirname(p), exist_ok=True)
        if os.path.exists(p): print(f"exists: {p}"); return
        json.dump({k: "" for k in KEYS}, open(p, "w"), indent=2)
        print(f"created blank intake: {p}\nfill with: facts_gate.py set {slug} <key> \"value\"\nkeys: {', '.join(KEYS)}")
    elif cmd == "set" and len(sys.argv) >= 5:
        key, val = sys.argv[3], sys.argv[4]
        if key not in KEYS: print(f"unknown key '{key}'. valid: {', '.join(KEYS)}"); sys.exit(2)
        d = load(slug); d[key] = val
        p = path(slug); os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump(d, open(p, "w"), indent=2)
        print(f"set {key} = {val}")
    elif cmd == "status":
        d = load(slug); miss = missing(d)
        print(f"FACTS for {slug}  ({len(KEYS)-len(miss)}/{len(KEYS)} filled)")
        for k, lbl in FACTS:
            v = d.get(k, "")
            mark = "✗ MISSING" if (k, lbl) in miss else "✓"
            print(f"  {mark}  {k}: {v or '—'}   [{lbl}]")
        print("\nVERDICT:", "READY — live loop may run" if not miss else f"BLOCKED — {len(miss)} fact(s) missing")
    elif cmd == "check":
        d = load(slug); miss = missing(d)
        if not miss:
            print("READY"); sys.exit(0)
        print("BLOCKED — missing: " + ", ".join(k for k, _ in miss)); sys.exit(1)
    else:
        print(__doc__); sys.exit(2)

if __name__ == "__main__":
    main()
