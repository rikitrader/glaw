#!/usr/bin/env python3
"""Zero-dependency placeholder for IRS PDF filling.

GLAW does not import reporting-disabled PDF helper/text checklist renderer or install packages. Use the JSON map this
workflow produces as a review checklist, then fill the IRS PDF manually in a PDF
viewer or IRS system.
"""
import sys


def main() -> int:
    print("PDF form filling is unavailable in absolute zero-third-party-package mode.", file=sys.stderr)
    print("Use a JSON/text fill guide and manually enter values into the official PDF.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
