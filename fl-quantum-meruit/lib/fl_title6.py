#!/usr/bin/env python3
"""GLAW Florida Statutes Title VI (Civil Practice and Procedure) index DB — query tool.

Reads fl-title6-index.json (the structured index of all Title VI chapters) and answers:
  list     — every chapter (number, title, kind)
  causes   — every chapter that supplies a civil CAUSE OF ACTION or remedy/writ, with the claims
  chapter  — full detail for one chapter (causes, elements, key sections)
  search   — find chapters/causes/sections matching a term

The index is a reference, not advice; verify every section and limitations period against current
Florida law before pleading.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

DB = Path(__file__).parent / "fl-title6-index.json"
ACTIONABLE = {"cause_of_action", "remedy", "writ"}


def _load() -> dict:
    return json.loads(DB.read_text(encoding="utf-8"))


def list_chapters(d: dict) -> str:
    o = [f"FLORIDA STATUTES TITLE {d['title']} — {d['name']}", "-" * 60]
    for c in d["chapters"]:
        o.append(f"  Ch. {c['ch']:<4} [{c['kind']:<15}] {c['title']}")
    return "\n".join(o)


def list_causes(d: dict) -> str:
    o = [f"TITLE {d['title']} — CAUSES OF ACTION / REMEDIES / WRITS", "-" * 60]
    for c in d["chapters"]:
        if c["kind"] in ACTIONABLE or "causes" in c:
            o.append(f"\n  Ch. {c['ch']} — {c['title']}  [{c['kind']}]")
            for cause in c.get("causes", []):
                o.append(f"     • {cause}")
    return "\n".join(o)


def chapter(d: dict, n: int) -> str:
    c = next((x for x in d["chapters"] if x["ch"] == n), None)
    if not c:
        return f"Chapter {n} is not in Title VI."
    o = [f"Ch. {c['ch']} — {c['title']}  [{c['kind']}]", "-" * 60]
    for cause in c.get("causes", []):
        o.append(f"  cause/remedy: {cause}")
    for k in ("elements", "elements_dishonored_check", "elements_eviction"):
        if k in c:
            o.append(f"  {k}:")
            for e in c[k]:
                o.append(f"     - {e}")
    if c.get("key_sections"):
        o.append("  key sections:")
        for s, desc in c["key_sections"].items():
            o.append(f"     §{s}: {desc}")
    return "\n".join(o)


def search(d: dict, term: str) -> str:
    t = term.lower()
    o = [f"TITLE {d['title']} search: '{term}'", "-" * 60]
    for c in d["chapters"]:
        blob = json.dumps(c, default=str).lower()
        if t in blob:
            hits = [f"§{s}: {desc}" for s, desc in c.get("key_sections", {}).items() if t in f"{s} {desc}".lower()]
            causes = [x for x in c.get("causes", []) if t in x.lower()]
            o.append(f"\n  Ch. {c['ch']} — {c['title']}  [{c['kind']}]")
            for x in causes:
                o.append(f"     • {x}")
            for h in hits:
                o.append(f"     {h}")
    return "\n".join(o) if len(o) > 2 else o[0] + "\n  (no match)"


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-fl-statute")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    sub.add_parser("causes")
    ch = sub.add_parser("chapter"); ch.add_argument("n", type=int)
    se = sub.add_parser("search"); se.add_argument("term")
    a = ap.parse_args()
    d = _load()
    if a.cmd == "list":
        print(list_chapters(d))
    elif a.cmd == "causes":
        print(list_causes(d))
    elif a.cmd == "chapter":
        print(chapter(d, a.n))
    elif a.cmd == "search":
        print(search(d, a.term))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
