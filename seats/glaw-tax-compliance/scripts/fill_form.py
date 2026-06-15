#!/usr/bin/env python3
"""Zero-dependency IRS form fill-package generator.

This does not mutate official PDF binaries. It writes a deterministic JSON field
payload and a review checklist that can be entered into the official IRS PDF,
efile system, or tax software.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(path: str | None) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _flatten(prefix: str, value, out: dict) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            _flatten(f"{prefix}.{k}" if prefix else str(k), v, out)
    elif isinstance(value, list):
        for i, v in enumerate(value, 1):
            _flatten(f"{prefix}.{i}", v, out)
    else:
        out[prefix] = "" if value is None else str(value)


def build_package(form: str, data: dict) -> dict:
    fields: dict[str, str] = {}
    _flatten("", data, fields)
    return {
        "form": form,
        "mode": "manual-entry-fill-package",
        "field_count": len(fields),
        "fields": fields,
        "review_required": True,
        "disclaimer": "Prepared as attorney/CPA work-product for licensed review; not legal or tax advice.",
    }


def render_checklist(pkg: dict) -> str:
    lines = [
        f"IRS FORM FILL CHECKLIST — {pkg['form']}",
        "=" * 72,
        pkg["disclaimer"],
        "",
    ]
    for key in sorted(pkg["fields"]):
        lines.append(f"[ ] {key}: {pkg['fields'][key]}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-fill-form")
    ap.add_argument("--form", required=True, help="IRS form name, e.g. 1120, 1040, 941")
    ap.add_argument("--data", required=True, help="JSON return/form data")
    ap.add_argument("--out", required=True, help="output base path, without extension")
    args = ap.parse_args()
    pkg = build_package(args.form, _load(args.data))
    base = Path(args.out)
    base.parent.mkdir(parents=True, exist_ok=True)
    json_path = base.with_suffix(".fill.json")
    txt_path = base.with_suffix(".fill.txt")
    json_path.write_text(json.dumps(pkg, indent=2, default=str), encoding="utf-8")
    txt_path.write_text(render_checklist(pkg), encoding="utf-8")
    print(f"wrote {json_path}")
    print(f"wrote {txt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
