#!/usr/bin/env python3
"""Zero-dependency draft publisher: markdown files -> local HTML directory."""
import html
import os
import re
import sys


def md2html(md):
    lines = ["<!doctype html><meta charset='utf-8'>"]
    for line in md.splitlines():
        if line.startswith("# "):
            lines.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            lines.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.strip():
            lines.append(f"<p>{html.escape(line)}</p>")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print("usage: publish_drafts_to_drive.py <outdir> <file.md> [...]")
        return 1
    outdir, files = sys.argv[1], sys.argv[2:]
    os.makedirs(outdir, exist_ok=True)
    for f in files:
        if not os.path.exists(f):
            print("skip (missing):", f)
            continue
        name = re.sub(r"^\d+[-_]?", "", os.path.splitext(os.path.basename(f))[0]).replace("-", " ").title()
        out = os.path.join(outdir, re.sub(r"[^A-Za-z0-9._-]+", "-", name) + ".html")
        open(out, "w", encoding="utf-8").write(md2html(open(f, encoding="utf-8").read()))
        print("PUBLISHED_LOCAL", name, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
