#!/usr/bin/env python3
"""GLAW Florida Causes of Action index — query tool over fl-causes-index.json (110 causes + the
legal standards), authored from public Florida law (Standard Jury Instructions, statutes, case law).

  list                 — every cause (name, category, SOL)
  category <cat>       — causes in one category (contract, tort-*, equity, property, statutory, ...)
  show <name|substr>   — elements + statute of limitations + defenses + authority for a cause
  search <term>        — find causes whose name/elements/defenses/basis match
  standards            — the motion / appellate standards (MTD, MSJ, DV, JNOV, Daubert, punitive...)
  sol <years>          — causes with that limitations period (a quick SOL triage)

A reference, not advice; verify every element, SOL, and authority against current Florida law.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

DB = Path(__file__).parent / "fl-causes-index.json"


def _load() -> dict:
    return json.loads(DB.read_text(encoding="utf-8"))


def _match(d, term):
    t = term.lower()
    return [c for c in d["causes"] if t in c["n"].lower()] or \
           [c for c in d["causes"] if t in json.dumps(c, default=str).lower()]


def list_all(d) -> str:
    o = [f"FLORIDA CAUSES OF ACTION ({len(d['causes'])})", "-" * 64]
    for c in d["causes"]:
        sol = f"{c['sol_years']}yr" if c.get("sol_years") else "—"
        o.append(f"  [{c['cat']:<16}] {sol:<5} {c['n']}")
    return "\n".join(o)


def category(d, cat) -> str:
    cs = [c for c in d["causes"] if cat.lower() in c["cat"].lower()]
    o = [f"CATEGORY '{cat}' ({len(cs)})", "-" * 64]
    for c in cs:
        o.append(f"  {c['n']}  (SOL {c.get('sol_years') or '—'} yr)")
    return "\n".join(o) if cs else f"No causes in category '{cat}'. Try: " + \
        ", ".join(sorted({c['cat'] for c in d['causes']}))


def show(d, name) -> str:
    cs = _match(d, name)
    if not cs:
        return f"No cause matching '{name}'."
    o = []
    for c in cs[:4]:
        o += [f"━━ {c['n']}  [{c['cat']}]  ·  SOL {c.get('sol_years') or '—'} yr", f"   authority: {c['basis']}",
              "   ELEMENTS:"]
        o += [f"     {i+1}. {e}" for i, e in enumerate(c.get("elements", []))]
        if c.get("defenses"):
            o.append("   KEY DEFENSES: " + "; ".join(c["defenses"]))
        o.append("")
    return "\n".join(o)


def search(d, term) -> str:
    cs = _match(d, term)
    o = [f"search '{term}' — {len(cs)} match(es)", "-" * 64]
    for c in cs:
        o.append(f"  {c['n']}  [{c['cat']}]  (SOL {c.get('sol_years') or '—'})")
    return "\n".join(o)


def standards(d) -> str:
    o = ["FLORIDA LEGAL STANDARDS (motions / appeal)", "-" * 64]
    extra = [c for c in d["causes"] if c["cat"] == "standard"]
    for s in d["standards"] + [{"n": c["n"], "basis": c["basis"], "note": "; ".join(c.get("elements", []))} for c in extra]:
        o.append(f"  • {s['n']} — {s['basis']}\n      {s.get('note','')}")
    return "\n".join(o)


def by_sol(d, years) -> str:
    cs = [c for c in d["causes"] if str(c.get("sol_years")) == str(years)]
    o = [f"causes with a {years}-year limitations period ({len(cs)})", "-" * 64]
    for c in cs:
        o.append(f"  {c['n']}  [{c['cat']}]")
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-fl-cause")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    c = sub.add_parser("category"); c.add_argument("cat")
    sh = sub.add_parser("show"); sh.add_argument("name")
    se = sub.add_parser("search"); se.add_argument("term")
    sub.add_parser("standards")
    so = sub.add_parser("sol"); so.add_argument("years")
    a = ap.parse_args()
    d = _load()
    print({"list": lambda: list_all(d), "category": lambda: category(d, a.cat),
           "show": lambda: show(d, a.name), "search": lambda: search(d, a.term),
           "standards": lambda: standards(d), "sol": lambda: by_sol(d, a.years)}[a.cmd]())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
