#!/usr/bin/env python3
"""GLAW Federal Causes of Action index — query tool over federal-causes-index.json (civil + criminal-
referral + regulatory federal claims), authored by an adversarially-verified multi-agent panel from
public federal law. Mirrors glaw-fl-cause.
  list · category <cat> · show <name|substr> · search <term> · sol <years|substr>
Each cause's 'defenses' cross-reference the federal defenses library — enumerate the killers with
`glaw-fed-defense for "<claim>"`. Reference, not advice; cites flagged [VERIFY] must be confirmed."""
from __future__ import annotations
import argparse, json
from pathlib import Path
DB = Path(__file__).parent / "federal-causes-index.json"
def _load(): return json.loads(DB.read_text(encoding="utf-8"))
def _m(d,t):
    t=t.lower(); return [c for c in d["causes"] if t in c["n"].lower()] or [c for c in d["causes"] if t in json.dumps(c,default=str).lower()]
def _sol(c): return f"{c['sol_years']}" if c.get("sol_years") not in (None,"") else "—"
def list_all(d):
    o=[f"FEDERAL CAUSES OF ACTION ({len(d['causes'])})","-"*70]
    for c in d["causes"]: o.append(f"  [{c['cat']:<14}] {c['n']}")
    return "\n".join(o)
def category(d,cat):
    cs=[c for c in d["causes"] if cat.lower() in c["cat"].lower()]
    return "\n".join([f"CATEGORY '{cat}' ({len(cs)})","-"*70]+[f"  {c['n']}  (SOL {_sol(c)})" for c in cs]) if cs else \
        "No causes in '%s'. Categories: %s" % (cat, ", ".join(d.get("categories",[])))
def show(d,name):
    cs=_m(d,name); o=[]
    for c in cs[:4]:
        o+=[f"━━ {c['n']}  [{c['cat']}]  ·  SOL {_sol(c)}", f"   authority: {c['basis']}", "   ELEMENTS:"]
        o+=[f"     {i+1}. {e}" for i,e in enumerate(c.get("elements",[]))]
        if c.get("defenses"): o.append("   KEY DEFENSES: "+"; ".join(c["defenses"]))
        o.append("")
    return "\n".join(o) if cs else f"No cause matching '{name}'."
def search(d,t):
    cs=_m(d,t); return "\n".join([f"search '{t}' — {len(cs)}","-"*70]+[f"  {c['n']}  [{c['cat']}]  (SOL {_sol(c)})" for c in cs])
def by_sol(d,y):
    cs=[c for c in d["causes"] if str(y).lower() in str(c.get("sol_years","")).lower()]
    return "\n".join([f"causes with SOL ~ '{y}' ({len(cs)})","-"*70]+[f"  {c['n']}  [{c['cat']}]" for c in cs])
def main():
    ap=argparse.ArgumentParser(prog="glaw-fed-cause"); sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("list")
    for nm,arg in (("category","cat"),("show","name"),("search","term"),("sol","years")):
        p=sub.add_parser(nm); p.add_argument(arg)
    a=ap.parse_args(); d=_load()
    print({"list":lambda:list_all(d),"category":lambda:category(d,a.cat),"show":lambda:show(d,a.name),
           "search":lambda:search(d,a.term),"sol":lambda:by_sol(d,a.years)}[a.cmd]())
    return 0
if __name__=="__main__": raise SystemExit(main())
