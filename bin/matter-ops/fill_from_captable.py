#!/usr/bin/env python3
"""GLAW fill-engine — turn a library MASTER ([BRACKET] template) into a corp-filled version.
Substitutes the standard corp tokens and, for option/RSU masters, appends a grant schedule built from the
corp's Carta cap-table EMPLOYEE rows. Deterministic; leaves anything it can't resolve as [VERIFY ...].

Usage:
  fill_from_captable.py <master.md> --company "ROOF10X, Inc." --year 2024 --state Delaware \
    [--strike "[APPRAISED FMV — $1.00 draft]"] [--sheet <captableSheetId>] [--out <out.md>]
"""
import sys, os, re
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def arg(flag, default=None):
    m = re.search(rf'{flag}\s+"([^"]+)"', " ".join(sys.argv)) or re.search(rf'{flag}\s+(\S+)', " ".join(sys.argv))
    return m.group(1) if m else default

def employees(sheet):
    if not sheet: return []
    tok = os.path.expanduser("~/.gcp/token.json")
    c = Credentials.from_authorized_user_file(tok)
    if not c.valid: c.refresh(Request()); open(tok, "w").write(c.to_json())
    s = build("sheets", "v4", credentials=c)
    rows = s.spreadsheets().values().get(spreadsheetId=sheet, range="'Cap Table View'!A1:H200").execute().get("values", [])
    if not rows: return []
    hdr = [h.lower() for h in rows[0]]
    ci = lambda *n: next((i for i, h in enumerate(hdr) if any(x in h for x in n)), None)
    iN, iT, iS = ci("stakeholder", "name"), ci("type"), ci("shares")
    out = []
    for r in rows[1:]:
        if len(r) <= max(iN, iT, iS): continue
        if (r[iT].strip().upper() if iT is not None else "") == "EMPLOYEE":
            out.append((r[iN].strip(), r[iS].strip()))
    return out

def main():
    master = sys.argv[1]
    company = arg("--company", "[COMPANY], Inc.")
    year = arg("--year", "20__")
    state = arg("--state", "Delaware")
    strike = arg("--strike", "[APPRAISED FMV]")
    sheet = arg("--sheet")
    out = arg("--out", master.replace(".md", "") + ".filled.md")
    short = re.sub(r",?\s*(Inc\.|LLC|Corp\.).*$", "", company).strip()
    t = open(master).read()
    t = t.replace("[COMPANY], INC.", company.upper()).replace("[COMPANY]", short.upper())
    t = t.replace("[Company], Inc.", company).replace("[Company]", short)
    t = t.replace("[20__]", str(year)).replace("[APPRAISED FMV]", strike)
    # state: normalize "a Delaware corporation" already says Delaware; replace bracket placeholders
    t = t.replace("[Delaware]", state)
    emps = employees(sheet)
    if emps and re.search(r"option|rsu|grant", master, re.I):
        sched = "\n\n# GRANT SCHEDULE (from cap table — EMPLOYEE rows)\n| Participant | Shares/Units | Strike | Type | Vesting |\n|---|---|---|---|---|\n"
        for n, sh in emps:
            sched += f"| {n} | {sh} | {strike} | [ISO/NSO / RSU] | 25% 1-yr cliff, then 36 mo |\n"
        sched += "*Pool: confirm availability; §422 $100k ISO check at the final strike.*\n"
        t = sched + "\n---\n" + t
    open(out, "w").write(t)
    n_unfilled = len(re.findall(r"\[[A-Za-z]", t))
    print(f"FILLED -> {out}  ({len(emps)} employees from cap table; {n_unfilled} [BRACKETS] remain for counsel)")

if __name__ == "__main__":
    main()
