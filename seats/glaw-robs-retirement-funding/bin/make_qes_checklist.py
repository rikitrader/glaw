#!/usr/bin/env python3
"""Render the QES-issuance checklist template to Google-Doc-ready HTML (inline styles).

Zero dependency (stdlib only) so it runs identically under Codex or Claude Code. It does NOT touch Google
itself — it emits an HTML file; the agent then imports it to Google Docs with the user's ~/.gcp/token.json:

    python3 bin/make_qes_checklist.py --company "Acme Roofing Inc." --out /tmp/qes.html
    # then (agent, with Drive scope): import /tmp/qes.html as a native Google Doc.

Google Docs HTML import ignores <style> blocks + CSS page-breaks, so all styling here is INLINE.
Attorney/CPA work-product — not legal/tax advice; the agent never files.
"""
import argparse
import html
import os
import re

TPL = os.path.join(os.path.dirname(__file__), "..", "references", "templates", "qes-issuance-checklist.md")

BODY = "font-family:'Times New Roman',serif;font-size:12pt;color:#000;line-height:1.4;"
H1 = "font-family:Arial,sans-serif;font-size:18pt;text-align:center;margin-bottom:6pt;"
H2 = "font-family:Arial,sans-serif;font-size:13pt;border-bottom:1px solid #000;margin-top:16pt;"
NOTE = "border:1px solid #888;background:#f4f4f4;padding:8px;font-size:10pt;"
TBL = "border-collapse:collapse;width:100%;font-size:11pt;"


def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def render(md, company):
    out = [f"<!doctype html><meta charset='utf-8'><div style=\"{BODY}\">"]
    lines = md.splitlines()
    i = 0
    in_note = False
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("# "):
            title = inline(ln[2:])
            if company:
                title += f"<br><span style='font-size:12pt;'>{html.escape(company)}</span>"
            out.append(f"<h1 style=\"{H1}\">{title}</h1>")
        elif ln.startswith("## "):
            out.append(f"<h2 style=\"{H2}\">{inline(ln[3:])}</h2>")
        elif ln.startswith(">"):
            # accumulate blockquote lines into one note box
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").rstrip())
                i += 1
            out.append(f"<p style=\"{NOTE}\">" + "<br>".join(inline(b) for b in buf if b) + "</p>")
            continue
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i]); i += 1
            cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            cells = [r for r in cells if not all(set(c) <= set("-: ") for c in r)]  # drop separator row
            out.append(f"<table border='1' cellspacing='0' cellpadding='6' style=\"{TBL}\">")
            for ri, r in enumerate(cells):
                tag = "th" if ri == 0 else "td"
                bg = " style='background:#eee;'" if ri == 0 else ""
                out.append("<tr>" + "".join(f"<{tag} align='left'{bg}>{inline(c)}</{tag}>" for c in r) + "</tr>")
            out.append("</table>")
            continue
        elif ln.strip().startswith("- "):
            out.append(f"<p style='margin:2pt 0;'>{inline(ln.strip()[2:])}</p>")
        elif ln.strip():
            out.append(f"<p>{inline(ln.strip())}</p>")
        i += 1
    out.append("</div>")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description="Render the QES-issuance checklist to Google-Doc-ready HTML")
    p.add_argument("--company", default="", help="company name to stamp under the title")
    p.add_argument("--out", default="/tmp/qes-issuance-checklist.html")
    p.add_argument("--template", default=TPL)
    args = p.parse_args()
    md = open(args.template, encoding="utf-8").read()
    open(args.out, "w", encoding="utf-8").write(render(md, args.company))
    print("HTML written:", args.out)
    print("Next (agent, needs Drive scope): import as a native Google Doc via ~/.gcp/token.json —")
    print('  files().create(body={"name": "QES Issuance Checklist", '
          '"mimeType":"application/vnd.google-apps.document"}, media_body=<out.html as text/html>)')


if __name__ == "__main__":
    main()
