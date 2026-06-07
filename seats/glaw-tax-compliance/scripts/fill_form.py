#!/usr/bin/env python3
"""Fill an IRS AcroForm PDF from a JSON map of {field_name: value}.

Build the map from inspect_fields.py output against the SAME downloaded form — field
names are revision-specific. Text fields take strings; checkboxes/radios take one of the
`states` values shown by inspect_fields.py (e.g. "/1", "/Yes").

The output is NOT flattened and NOT signed — the taxpayer must review every entry and
sign. This tool only pre-populates; it never transmits anything to the IRS.

Usage:
    python3 fill_form.py BLANK.pdf MAP.json OUT.pdf
"""
import sys
import json
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    blank, mapfile, out = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(mapfile, encoding="utf-8") as f:
        values = json.load(f)

    reader = PdfReader(blank)
    writer = PdfWriter()
    writer.append(reader)

    # Make filled values render in all PDF viewers.
    try:
        writer._root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)
    except Exception:
        pass

    filled = 0
    for page in writer.pages:
        try:
            writer.update_page_form_field_values(page, values, auto_regenerate=False)
        except Exception:
            continue
    # report which requested fields actually exist on the form
    present = set((reader.get_fields() or {}).keys())
    for k in values:
        if k in present:
            filled += 1
        else:
            print(f"WARN  field not found on form: {k!r}", file=sys.stderr)

    with open(out, "wb") as f:
        writer.write(f)
    print(f"OK    wrote {out}  ({filled}/{len(values)} mapped fields matched the form)")
    print("NOTE  review every entry and SIGN before filing — nothing was transmitted.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
