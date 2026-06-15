#!/usr/bin/env python3
"""Zero-dependency legal publisher: markdown -> local HTML."""
import html
import os
import re
import sys


def md2html(md):
    body = []
    for line in md.splitlines():
        if line.startswith("# "):
            body.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            body.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.strip():
            body.append(f"<p>{html.escape(line)}</p>")
    return "<!doctype html><meta charset='utf-8'>" + "\n".join(body)


def main():
    if len(sys.argv) < 2:
        print("usage: publish_legal.py <md> [--out out.html]")
        return 1
    src = sys.argv[1]
    out = None
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    else:
        out = os.path.splitext(src)[0] + ".html"
    open(out, "w", encoding="utf-8").write(md2html(open(src, encoding="utf-8").read()))
    print(f"PUBLISHED_LOCAL {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
