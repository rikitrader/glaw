#!/usr/bin/env python3
"""Zero-dependency comment-review helper.

Reads a local JSON export of comments instead of calling Google Drive.
Expected shape: [{"doc": "...", "author": "...", "content": "...", "quoted": "..."}]
"""
import json
import re
import sys

SUBSTANCE = re.compile(r"\b(par value|shares?|vest|cliff|FMV|tax|QSBS|1202|83\(?b\)?|deadline|indemnif|liabilit|governing law)\b", re.I)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: review_comments.py comments.json")
        return 1
    comments = json.load(open(sys.argv[1], encoding="utf-8"))
    for c in comments:
        text = (c.get("content", "") + " " + c.get("quoted", ""))
        verdict = "CAREFUL-REWRITE" if SUBSTANCE.search(text) else "ACCEPT-able"
        print(f"{c.get('doc', 'document')}: [{c.get('author', 'unknown')}] {c.get('content', '')}")
        print(f"  -> {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
