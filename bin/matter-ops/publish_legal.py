#!/usr/bin/env python3
"""GLAW ENFORCED-STYLE publisher. Renders a markdown template to a Google Doc using the canonical
us-corporate-legal-instrument house style (forms-library/glaw-document-style.css). Use for EVERY template.
Create:  publish_legal.py <md> --folder <id> --name "Title"
Update:  publish_legal.py <md> --update <fileId>      (re-renders an existing doc in place, no dupes)
"""
import sys, os, re, html
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

CSS_PATH = os.path.expanduser("~/.claude/skills/glaw/lib/forms-library/glaw-document-style.css")
CSS = open(CSS_PATH).read() if os.path.exists(CSS_PATH) else ""

def md2html(md):
    L = md.split("\n"); o = [f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"]; i = 0
    def il(t):
        t = html.escape(t)
        t = re.sub(r'"\*\*([^*]+)\*\*"', r'"<span class="defterm">\1</span>"', t)   # "**Term**" -> defined term
        t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
        return t
    while i < len(L):
        ln = L[i]
        if not ln.strip(): i += 1; continue
        if re.match(r"^---+$", ln): o.append("<hr>"); i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)", ln)
        if m: lv = min(len(m.group(1)), 3); o.append(f"<h{lv}>{il(m.group(2))}</h{lv}>"); i += 1; continue
        if ln.startswith(">"):
            b = []
            while i < len(L) and L[i].startswith(">"): b.append(il(re.sub(r"^>\s?", "", L[i]))); i += 1
            o.append("<blockquote>" + "<br>".join(b) + "</blockquote>"); continue
        if "|" in ln and i+1 < len(L) and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", L[i+1]) and "-" in L[i+1]:
            cell = lambda r: [x.strip() for x in r.strip().strip("|").split("|")]
            h = cell(ln); i += 2; rows = []
            while i < len(L) and "|" in L[i] and L[i].strip(): rows.append(cell(L[i])); i += 1
            o.append("<table><tr>" + "".join(f"<th>{il(x)}</th>" for x in h) + "</tr>" +
                     "".join("<tr>" + "".join(f"<td>{il(x)}</td>" for x in r) + "</tr>" for r in rows) + "</table>"); continue
        b = []
        while i < len(L) and L[i].strip() and not re.match(r"^(#|>|\||---)", L[i]): b.append(L[i]); i += 1
        o.append("<p>" + il(" ".join(b)) + "</p>")
    return "".join(o) + "</body></html>"

def client():
    tok = os.path.expanduser("~/.gcp/token.json")
    c = Credentials.from_authorized_user_file(tok)
    if not c.valid: c.refresh(Request()); open(tok, "w").write(c.to_json())
    return build("drive", "v3", credentials=c)

def main():
    md = sys.argv[1]
    args = " ".join(sys.argv)
    upd = re.search(r"--update\s+(\S+)", args)
    fol = re.search(r"--folder\s+(\S+)", args)
    nm = re.search(r'--name\s+"?(.+?)"?\s*(?:--\w+\s|$)', args)
    media = MediaInMemoryUpload(md2html(open(md).read()).encode(), mimetype="text/html")
    d = client()
    if upd:
        r = d.files().update(fileId=upd.group(1), media_body=media, fields="id,webViewLink").execute()
        print("UPDATED", r["webViewLink"])
    elif fol and nm:
        r = d.files().create(body={"name": nm.group(1), "parents": [fol.group(1)],
            "mimeType": "application/vnd.google-apps.document"}, media_body=media, fields="id,webViewLink").execute()
        print("CREATED", r["webViewLink"])
    else:
        print("need --update <id> OR --folder <id> --name \"Title\"")

if __name__ == "__main__":
    main()
