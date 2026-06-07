#!/usr/bin/env python3
"""Fill an IRS fillable PDF (AcroForm) from a JSON field map — the agent's form-filler.
Usage: fill_form.py <blank_form.pdf> <data.json> <out.pdf>
  data.json: { "exact AcroForm field name": "value", ... }
             (checkbox/radio: use the on-state from inspect_fields.py, e.g. "/1" or "/Yes")
Sets NeedAppearances so viewers render the values. Reports any data keys that did
not match a real field (typos) and any required-looking blank fields left empty."""
import sys, json
import pypdf
from pypdf.generic import NameObject, BooleanObject

def main():
    if len(sys.argv) != 4:
        print("usage: fill_form.py <blank_form.pdf> <data.json> <out.pdf>"); sys.exit(1)
    src, data_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    data = json.load(open(data_path))
    reader = pypdf.PdfReader(src)
    fields = reader.get_fields() or {}
    real = set(fields.keys())

    unknown = [k for k in data if k not in real]
    if unknown:
        print("⚠️  data keys not found in form (check exact field names via inspect_fields.py):")
        for k in unknown: print(f"     - {k!r}")

    writer = pypdf.PdfWriter()
    writer.append(reader)
    for page in writer.pages:
        writer.update_page_form_field_values(page, {k: v for k, v in data.items() if k in real},
                                             auto_regenerate=False)
    # make values visible in all viewers
    try:
        writer.set_need_appearances_writer(True)
    except Exception:
        root = writer._root_object
        if "/AcroForm" in root:
            root["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)

    with open(out, "wb") as fh:
        writer.write(fh)

    filled = [k for k in data if k in real]
    blanks = [k for k in real if not (fields[k].get("/V") or data.get(k))]
    print(f"✅ filled {len(filled)}/{len(real)} fields -> {out}")
    if blanks:
        print(f"ℹ️  {len(blanks)} fields left blank — confirm none are required:")
        for k in blanks[:40]: print(f"     - {k}")
        if len(blanks) > 40: print(f"     … +{len(blanks)-40} more")

if __name__ == "__main__":
    main()
