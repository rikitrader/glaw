#!/usr/bin/env python3
"""GLAW Federal Litigation Defenses index — the defenses/attacks a federal adversary brings.
Powers the central gate's DOJ/AUSA Prosecutor + Federal Defense Counsel personas.
  list · category <fed-civil|fed-criminal|fed-regulatory> · show <name> · search <t> · for "<claim>"
Reference, not advice; circuits split and standards shift — verify each."""
from __future__ import annotations
import argparse, json
from pathlib import Path
DB = Path(__file__).parent / "federal-defenses-index.json"
def _load(): return json.loads(DB.read_text(encoding="utf-8"))
def _m(d,t):
    t=t.lower(); return [x for x in d["defenses"] if t in x["d"].lower()] or [x for x in d["defenses"] if t in json.dumps(x,default=str).lower()]
def list_all(d):
    return "\n".join([f"FEDERAL LITIGATION DEFENSES ({len(d['defenses'])})","-"*64]+[f"  [{x['cat']:<14}] {x['d']}" for x in d["defenses"]])
def category(d,c):
    xs=[x for x in d["defenses"] if c.lower() in x["cat"].lower()]
    return "\n".join([f"CATEGORY '{c}' ({len(xs)})","-"*64]+[f"  {x['d']}" for x in xs]) if xs else f"No defenses in '{c}'. (fed-civil | fed-criminal | fed-regulatory)"
def show(d,n):
    xs=_m(d,n); o=[]
    for x in xs[:5]:
        o+=[f"━━ {x['d']}  [{x['cat']}]", f"   authority: {x['basis']}  ·  burden: {x['burden']}", f"   DEFEATS: {x['defeats']}", "   MUST SHOW:"]+[f"     - {s}" for s in x.get("show",[])]+[""]
    return "\n".join(o) if xs else f"No defense matching '{n}'."
def search(d,t):
    xs=_m(d,t); return "\n".join([f"search '{t}' — {len(xs)}","-"*64]+[f"  {x['d']}  [{x['cat']}]" for x in xs])
def for_claim(d,c):
    c=c.lower(); xs=[x for x in d["defenses"] if c in x["defeats"].lower()]
    return "\n".join([f"federal defenses that defeat '{c}' ({len(xs)})","-"*64]+[f"  {x['d']} — {x['defeats']}" for x in xs])
def main():
    ap=argparse.ArgumentParser(prog="glaw-fed-defense"); sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("list")
    for nm,arg in (("category","cat"),("show","name"),("search","term"),("for","claim")):
        p=sub.add_parser(nm); p.add_argument(arg)
    a=ap.parse_args(); d=_load()
    print({"list":lambda:list_all(d),"category":lambda:category(d,a.cat),"show":lambda:show(d,a.name),"search":lambda:search(d,a.term),"for":lambda:for_claim(d,a.claim)}[a.cmd]())
    return 0
if __name__=="__main__": raise SystemExit(main())
