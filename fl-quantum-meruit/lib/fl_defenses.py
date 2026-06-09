#!/usr/bin/env python3
"""GLAW Florida Affirmative Defenses index — query tool over fl-defenses-index.json (the Rule
1.110(d) / 1.140(b) defenses + common-law and statutory avoidances), authored from public FL law.

  list                — every defense (category)
  category <cat>      — defenses in one category (procedural/contract/tort/equitable/statutory/constitutional)
  show <name|substr>  — what to show + who bears the burden + what it defeats + authority
  search <term>       — find by name/showing/defeats/basis
  for "<claim>"       — defenses that commonly defeat a given claim type (substring of 'defeats')

A reference, not advice; affirmative defenses must be pleaded (1.110(d)) or are waived. Verify each.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
DB = Path(__file__).parent / "fl-defenses-index.json"
def _load(): return json.loads(DB.read_text(encoding="utf-8"))
def _m(d,t):
    t=t.lower(); return [x for x in d["defenses"] if t in x["d"].lower()] or [x for x in d["defenses"] if t in json.dumps(x,default=str).lower()]
def list_all(d):
    o=[f"FLORIDA AFFIRMATIVE DEFENSES ({len(d['defenses'])})","-"*64]
    for x in d["defenses"]: o.append(f"  [{x['cat']:<13}] {x['d']}")
    return "\n".join(o)
def category(d,c):
    xs=[x for x in d["defenses"] if c.lower() in x["cat"].lower()]
    return "\n".join([f"CATEGORY '{c}' ({len(xs)})","-"*64]+[f"  {x['d']}" for x in xs]) if xs else f"No defenses in '{c}'."
def show(d,n):
    xs=_m(d,n); o=[]
    for x in xs[:5]:
        o+= [f"━━ {x['d']}  [{x['cat']}]", f"   authority: {x['basis']}  ·  burden: {x['burden']}",
             f"   DEFEATS: {x['defeats']}", "   MUST SHOW:"]
        o+= [f"     - {s}" for s in x.get("show",[])]; o.append("")
    return "\n".join(o) if xs else f"No defense matching '{n}'."
def search(d,t):
    xs=_m(d,t); return "\n".join([f"search '{t}' — {len(xs)}","-"*64]+[f"  {x['d']}  [{x['cat']}]" for x in xs])
def for_claim(d,c):
    c=c.lower(); xs=[x for x in d["defenses"] if c in x["defeats"].lower()]
    return "\n".join([f"defenses that commonly defeat '{c}' ({len(xs)})","-"*64]+[f"  {x['d']} — {x['defeats']}" for x in xs])
def main():
    ap=argparse.ArgumentParser(prog="glaw-fl-defense"); sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("list"); 
    for nm,arg in (("category","cat"),("show","name"),("search","term"),("for","claim")):
        p=sub.add_parser(nm); p.add_argument(arg)
    a=ap.parse_args(); d=_load()
    print({"list":lambda:list_all(d),"category":lambda:category(d,a.cat),"show":lambda:show(d,a.name),
           "search":lambda:search(d,a.term),"for":lambda:for_claim(d,a.claim)}[a.cmd]())
    return 0
if __name__=="__main__": raise SystemExit(main())
