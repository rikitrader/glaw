#!/usr/bin/env python3
"""Zero-dependency form fill-package generator."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def flatten(prefix: str, value, out: dict) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            flatten(f"{prefix}.{k}" if prefix else str(k), v, out)
    elif isinstance(value, list):
        for i, v in enumerate(value, 1):
            flatten(f"{prefix}.{i}", v, out)
    else:
        out[prefix] = "" if value is None else str(value)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-fill-form")
    ap.add_argument("--form", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    fields: dict[str, str] = {}
    flatten("", data, fields)
    pkg = {"form": args.form, "mode": "manual-entry-fill-package", "fields": fields,
           "review_required": True}
    base = Path(args.out)
    base.parent.mkdir(parents=True, exist_ok=True)
    base.with_suffix(".fill.json").write_text(json.dumps(pkg, indent=2), encoding="utf-8")
    base.with_suffix(".fill.txt").write_text(
        "\n".join(f"[ ] {k}: {fields[k]}" for k in sorted(fields)) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {base.with_suffix('.fill.json')}")
    print(f"wrote {base.with_suffix('.fill.txt')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
