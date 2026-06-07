#!/usr/bin/env python3
"""Dump an IRS fillable-PDF's AcroForm fields so an agent can build a fill map.
Usage: inspect_fields.py <form.pdf> [out.json]
Prints {field_name: {type, current_value, options}} — checkbox options show the
'on' state to use (e.g. "/1", "/Yes")."""
import sys, json
import pypdf

def main():
    if len(sys.argv) < 2:
        print("usage: inspect_fields.py <form.pdf> [out.json]"); sys.exit(1)
    r = pypdf.PdfReader(sys.argv[1])
    flds = r.get_fields() or {}
    out = {}
    for name, f in flds.items():
        ft = f.get("/FT")
        entry = {"type": {"/Tx": "text", "/Btn": "button/checkbox",
                          "/Ch": "choice", "/Sig": "signature"}.get(str(ft), str(ft)),
                 "current_value": f.get("/V")}
        states = f.get("/_States_")
        if states:
            entry["options"] = list(states)
        out[name] = entry
    js = json.dumps(out, indent=2, default=str)
    if len(sys.argv) > 2:
        open(sys.argv[2], "w").write(js); print(f"wrote {len(out)} fields -> {sys.argv[2]}")
    else:
        print(js)

if __name__ == "__main__":
    main()
