#!/usr/bin/env python3
"""Dump the fillable AcroForm fields of an IRS PDF as JSON.

Field names change between form revisions, so NEVER hardcode them — inspect the
*actual downloaded* form, then build your fill map from this output. For checkboxes,
the `states` list shows the valid "on" values (pass one of those to fill_form.py).

Usage:
    python3 inspect_fields.py FORM.pdf [--values]

Output: JSON array of {name, type, states, value}.
"""
import sys
import json
from pypdf import PdfReader


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    reader = PdfReader(path)
    fields = reader.get_fields() or {}
    out = []
    for name, f in fields.items():
        ftype = f.get("/FT")
        kind = {"/Tx": "text", "/Btn": "checkbox/radio", "/Ch": "choice", "/Sig": "signature"}.get(
            str(ftype), str(ftype))
        states = []
        if str(ftype) == "/Btn":
            # enumerate the export states (the valid "on" values)
            try:
                states = sorted(s for s in f.get("/_States_", []) if s not in ("/Off",))
            except Exception:
                states = []
        out.append({
            "name": name,
            "type": kind,
            "states": states,
            "value": str(f.get("/V")) if f.get("/V") is not None else None,
        })
    print(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\n# {len(out)} fillable fields in {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
