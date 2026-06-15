#!/usr/bin/env python3
"""Zero-dependency placeholder for PDF form filling."""
import sys


def main() -> int:
    print("PDF form filling is unavailable in absolute zero-third-party-package mode.", file=sys.stderr)
    print("Use the generated field map as a manual fill checklist.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
