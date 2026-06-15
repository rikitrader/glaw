#!/usr/bin/env python3
"""Build a text filing-dossier checklist from a manifest, with no PDF packages."""
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: assemble_dossier.py MANIFEST.json OUT.txt", file=sys.stderr)
        return 2
    manifest, out = Path(sys.argv[1]), Path(sys.argv[2])
    data = json.loads(manifest.read_text(encoding="utf-8"))
    lines = [
        data.get("title", "IRS Filing Packet"),
        "=" * len(data.get("title", "IRS Filing Packet")),
        "",
        f"Taxpayer: {data.get('taxpayer', '')}",
        f"Prepared: {data.get('prepared', '')}",
        "",
        "Contents:",
    ]
    for i, item in enumerate(data.get("items", []), 1):
        lines.append(f"{i}. {item.get('label', item.get('file', ''))}")
        if item.get("file"):
            lines.append(f"   File: {item['file']}")
        if item.get("mail_to"):
            lines.append(f"   Mail to: {item['mail_to']}")
        if item.get("notes"):
            lines.append(f"   Notes: {item['notes']}")
    lines.append("")
    lines.append("Checklist:")
    for item in data.get("checklist", []):
        lines.append(f"[ ] {item}")
    if data.get("mailing"):
        lines.extend(["", f"Mailing: {data['mailing']}"])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote zero-dependency dossier checklist -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
