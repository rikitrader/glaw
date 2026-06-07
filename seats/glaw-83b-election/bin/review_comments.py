#!/usr/bin/env python3
"""GLAW comment-review loop. Lists every open comment on every Google Doc in a Drive folder and
triages each ACCEPT vs CAREFUL-REWRITE, so GLAW can advise. Uses ~/.gcp/token.json (drive scope).

Usage:
  review_comments.py <folderId>            # report all open comments + triage
  review_comments.py <folderId> --reply    # also post a GLAW advisory reply on each open comment

Triage heuristic (substance-aware): a comment touching legal/tax operative terms is flagged
CAREFUL-REWRITE (escalate to owning seat); pure typo/clarity/formatting is ACCEPT-able.
NOTE: tracked-change *suggestions* (strikethrough) need a documents-scoped token to read their
text; this reads COMMENTS (incl. quotedFileContent), which the drive scope already covers."""
import os, sys, re
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SUBSTANCE = re.compile(r"\b(par value|shares?|vest|cliff|FMV|fair market|price|consideration|tax|"
    r"QSBS|1202|83\(?b\)?|deadline|indemnif|liabilit|class of stock|preferred|authorized|EIN|"
    r"jurisdiction|Delaware|repurchase|forfeit|warrant|represent|covenant|governing law)\b", re.I)

def creds():
    tok = os.path.expanduser("~/.gcp/token.json")
    c = Credentials.from_authorized_user_file(tok)
    if not c.valid: c.refresh(Request()); open(tok,"w").write(c.to_json())
    return c

def client():
    return build("drive","v3",credentials=creds())

def has_docs_scope():
    return "https://www.googleapis.com/auth/documents" in (creds().scopes or [])

def review_suggestions(file_id, name, do_reply=False):
    """Read tracked-change suggestions via the Docs API (needs documents scope)."""
    from googleapiclient.discovery import build as _b
    docs = _b("docs","v1",credentials=creds())
    doc = docs.documents().get(documentId=file_id,
              suggestionsViewMode="SUGGESTIONS_INLINE").execute()
    sugg = 0
    for el in doc.get("body",{}).get("content",[]):
        para = el.get("paragraph")
        if not para: continue
        for r in para.get("elements",[]):
            t = r.get("textRun")
            if not t: continue
            ins = t.get("suggestedInsertionIds")
            dele = t.get("suggestedDeletionIds")
            if ins or dele:
                sugg += 1
                kind = "INSERT" if ins else "DELETE (strike-through)"
                txt = t.get("content","").strip()
                verdict = ("CAREFUL-REWRITE (escalate to owning seat)"
                           if SUBSTANCE.search(txt) else "ACCEPT-able (clarity/typo)")
                print(f"  ~ [{kind}] {txt[:90]!r}")
                print(f"      → GLAW triage: {verdict}")
    return sugg

def main():
    if len(sys.argv) < 2:
        print("usage: review_comments.py <folderId> [--reply]"); sys.exit(1)
    folder, do_reply = sys.argv[1], ("--reply" in sys.argv)
    do_route = ("--route" in sys.argv)   # GAP 4: emit fix-tasks for CAREFUL-REWRITE comments
    routes = []
    d = client()
    docs_scope = has_docs_scope()
    print(f"Docs scope: {'ON — reading comments + suggestions' if docs_scope else 'OFF — comments only (run reauth_docs_scope.py to add)'}")
    files = d.files().list(q=f"'{folder}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false",
                           fields="files(id,name)").execute()["files"]
    total = 0
    for f in files:
        try:
            cs = d.comments().list(fileId=f["id"], fields="comments(id,content,author/displayName,resolved,quotedFileContent/value,replies(content))",
                                   includeDeleted=False).execute().get("comments", [])
        except Exception as e:
            print(f"  ! {f['name']}: {e}"); continue
        openc = [c for c in cs if not c.get("resolved")]
        if not openc: continue
        print(f"\n=== {f['name']} ({len(openc)} open) ===")
        for c in openc:
            total += 1
            quoted = (c.get("quotedFileContent") or {}).get("value","")
            verdict = "CAREFUL-REWRITE (escalate to owning seat)" if SUBSTANCE.search(c["content"]+" "+quoted) else "ACCEPT-able (clarity/typo)"
            print(f"  • [{c['author']['displayName']}] {c['content']!r}")
            if quoted: print(f"      on: {quoted[:90]!r}")
            print(f"      → GLAW triage: {verdict}")
            if do_route and "CAREFUL" in verdict:
                routes.append({"doc": f["name"], "comment": c["content"],
                               "on": quoted[:120], "action": "route to owning seat for careful rewrite + cite check"})
            if do_reply:
                msg = ("GLAW advisory: this comment changes operative legal/tax terms — do NOT accept blindly; "
                       "routing to the owning seat for a careful rewrite and citation check."
                       if "CAREFUL" in verdict else
                       "GLAW advisory: clarity/typo only — safe to accept.")
                d.replies().create(fileId=f["id"], commentId=c["id"], fields="id",
                                   body={"content": msg}).execute()
        if docs_scope:
            try:
                n = review_suggestions(f["id"], f["name"], do_reply)
                if n: print(f"  ({n} tracked-change suggestion(s) reviewed)")
            except Exception as e:
                print(f"  ! suggestions read failed: {e}")
    print(f"\nTotal open comments: {total}")
    if do_route:
        import json as _j
        print("\n=== FIX-TASKS (route to /glaw-chief-counsel remediation) ===")
        print(_j.dumps(routes, indent=2) if routes else "  (no CAREFUL-REWRITE comments to route)")

if __name__ == "__main__":
    main()
