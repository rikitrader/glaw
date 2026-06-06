#!/usr/bin/env python3
"""GAP 3 — reusable: publish matter draft .md files to a Drive folder as Helvetica,
single-spaced Google Docs (so the loop's finalize step can publish 29/30 + any updated docs
without a manual post-step). Uses ~/.gcp/token.json (drive scope).

Usage: publish_drafts_to_drive.py <folderId> <file1.md> [file2.md ...]
"""
import sys, os, re, html
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

import os as _os
_cssp=_os.path.expanduser("~/.claude/skills/glaw/lib/forms-library/glaw-document-style.css")
CSS=open(_cssp).read() if _os.path.exists(_cssp) else "body{font-family:'Times New Roman',serif;font-size:10pt;line-height:1.15;text-align:justify;}"

def md2html(md):
    L=md.split("\n"); o=[f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"]; i=0
    def il(t):
        t=html.escape(t); t=re.sub(r"\*\*([^*]+)\*\*",r"<b>\1</b>",t); return t.replace("[ ]","☐").replace("[x]","☑")
    while i<len(L):
        ln=L[i]
        if not ln.strip(): i+=1; continue
        if re.match(r"^---+\s*$",ln): o.append("<hr>"); i+=1; continue   # separator (was the infinite-loop trap)
        m=re.match(r"^(#{1,6})\s+(.*)",ln)
        if m: lv=min(len(m.group(1)),3); o.append(f"<h{lv}>{il(m.group(2))}</h{lv}>"); i+=1; continue
        if ln.startswith(">"):
            buf=[]
            while i<len(L) and L[i].startswith(">"): buf.append(il(re.sub(r"^>\s?","",L[i]))); i+=1
            o.append("<div class='b'>"+"<br>".join(buf)+"</div>"); continue
        if "|" in ln and i+1<len(L) and re.match(r"^\s*\|?[\s:|-]+\|?\s*$",L[i+1]) and "-" in L[i+1]:
            cell=lambda r:[c.strip() for c in r.strip().strip("|").split("|")]
            h=cell(ln); i+=2; rows=[]
            while i<len(L) and "|" in L[i] and L[i].strip(): rows.append(cell(L[i])); i+=1
            o.append("<table><tr>"+"".join(f"<th>{il(c)}</th>" for c in h)+"</tr>"+
                     "".join("<tr>"+"".join(f"<td>{il(c)}</td>" for c in r)+"</tr>" for r in rows)+"</table>"); continue
        if re.match(r"^\s*([-*]|\d+\.)\s+",ln):
            buf=[]
            while i<len(L) and re.match(r"^\s*([-*]|\d+\.)\s+",L[i]): buf.append(il(re.sub(r"^\s*([-*]|\d+\.)\s+","",L[i]))); i+=1
            o.append("<ul>"+"".join(f"<li>{x}</li>" for x in buf)+"</ul>"); continue
        buf=[]
        while i<len(L) and L[i].strip() and not re.match(r"^(#|>|\s*[-*]|\s*\d+\.)",L[i]): buf.append(L[i]); i+=1
        if buf: o.append("<p>"+il(" ".join(buf))+"</p>")
        else: i+=1   # no-progress guard: always advance
    o.append("</body></html>"); return "".join(o)

def main():
    if len(sys.argv) < 3:
        print("usage: publish_drafts_to_drive.py <folderId> <file.md> [...]"); sys.exit(1)
    folder=sys.argv[1]; files=sys.argv[2:]
    tok=os.path.expanduser("~/.gcp/token.json")
    c=Credentials.from_authorized_user_file(tok)
    if not c.valid: c.refresh(Request()); open(tok,"w").write(c.to_json())
    d=build("drive","v3",credentials=c)
    for f in files:
        if not os.path.exists(f): print("skip (missing):",f); continue
        name=re.sub(r"^\d+[-_]?","",os.path.splitext(os.path.basename(f))[0]).replace("-"," ").title()
        r=d.files().create(body={"name":name,"parents":[folder],"mimeType":"application/vnd.google-apps.document"},
            media_body=MediaInMemoryUpload(md2html(open(f).read()).encode(),mimetype="text/html"),
            fields="id,webViewLink").execute()
        print("PUBLISHED",name,r["webViewLink"])

if __name__ == "__main__":
    main()
