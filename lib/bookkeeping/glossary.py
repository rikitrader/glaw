#!/usr/bin/env python3
"""glaw-glossary — look up / search the GLAW accounting knowledge base.

Indexes the original glossary under knowledge/ (terms written as **Term** — definition,
in lists, prose, or ratio tables) and answers term lookups and keyword searches. Our own
code over our own, originally-authored reference — no third-party content.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

KNOWLEDGE = Path(__file__).parent / "knowledge"

# `- **Term** — def`  /  `**Term** — def`  /  `| **Term** | formula | tells |`
_LIST = re.compile(r"^\s*[-*]?\s*\*\*(?P<term>[^*]+?)\*\*\s*[—:-]\s*(?P<def>.+)$")
_ROW = re.compile(r"^\|\s*\*\*(?P<term>[^*]+?)\*\*\s*\|\s*(?P<a>[^|]*?)\s*\|\s*(?P<b>[^|]*?)\s*\|")


_HEAD = re.compile(r"^#{2,3}\s+(?P<term>[A-Za-z][A-Za-z0-9 /&'-]+?)\s*$")
_SECTION_WORDS = ("contents", "how the agents", "the cycle", "the four", "key terms",
                  "key ratios", "common accounts", "what ", "the accounting equation")


def build_index() -> dict[str, dict]:
    idx: dict[str, dict] = {}
    if not KNOWLEDGE.is_dir():
        return idx
    for f in sorted(KNOWLEDGE.glob("*.md")):
        lines = f.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            # headings as terms: capture the first non-empty following paragraph
            h = _HEAD.match(line)
            if h:
                term = h.group("term").strip()
                if any(w in term.lower() for w in _SECTION_WORDS):
                    h = None
                else:
                    definition = ""
                    for nxt in lines[i + 1:]:
                        s = nxt.strip()
                        if not s:
                            if definition:
                                break
                            continue
                        if s.startswith("#") or s.startswith("|") or s.startswith("- "):
                            break
                        definition += (" " if definition else "") + s
                    if definition:
                        key = term.lower()
                        idx.setdefault(key, {"term": term, "definition": definition.strip(), "source": f.name})
                    continue
            m = _LIST.match(line)
            if m:
                term, definition = m.group("term").strip(), m.group("def").strip()
            else:
                r = _ROW.match(line)
                if not r:
                    continue
                term = r.group("term").strip()
                definition = f"{r.group('b').strip()} (= {r.group('a').strip()})"
            # split "A / B" or "A (B)" headwords into aliases pointing at one entry
            heads = [h.strip() for h in re.split(r"\s*/\s*", re.sub(r"\(([^)]*)\)", r"/\1", term)) if h.strip()]
            canonical = heads[0]
            for h in heads:
                key = h.lower()
                if key not in idx:
                    idx[key] = {"term": canonical, "definition": definition, "source": f.name}
    return idx


def lookup(term: str) -> dict | None:
    idx = build_index()
    key = term.strip().lower()
    if key in idx:
        return idx[key]
    # fall back to a contains-match on the headword
    for k, v in idx.items():
        if key in k:
            return v
    return None


def search(query: str, limit: int = 12) -> list[dict]:
    q = query.strip().lower()
    hits = []
    for v in build_index().values():
        score = (2 if q in v["term"].lower() else 0) + (1 if q in v["definition"].lower() else 0)
        if score:
            hits.append((score, v))
    seen, out = set(), []
    for _, v in sorted(hits, key=lambda x: -x[0]):
        if v["term"] in seen:
            continue
        seen.add(v["term"])
        out.append(v)
    return out[:limit]


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-glossary")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lookup"); p.add_argument("term", nargs="+")
    p = sub.add_parser("search"); p.add_argument("query", nargs="+"); p.add_argument("--limit", type=int, default=12)
    sub.add_parser("list")
    a = ap.parse_args()

    if a.cmd == "lookup":
        res = lookup(" ".join(a.term))
        if not res:
            print(f"not found: {' '.join(a.term)}  (try: glaw-glossary search <keyword>)"); return 1
        print(f"{res['term']}\n  {res['definition']}\n  — {res['source']}")
        return 0
    if a.cmd == "search":
        res = search(" ".join(a.query), a.limit)
        if not res:
            print("no matches"); return 1
        for v in res:
            print(f"• {v['term']} — {v['definition'][:100]}{'…' if len(v['definition'])>100 else ''}")
        return 0
    for v in sorted(build_index().values(), key=lambda x: x["term"].lower()):
        print(v["term"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
