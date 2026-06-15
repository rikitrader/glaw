#!/usr/bin/env python3
"""Zero-dependency placeholder for PDF field inspection."""
import sys


def main() -> int:
    print("PDF field inspection is unavailable in absolute zero-third-party-package mode.", file=sys.stderr)
    print("Use a PDF viewer's field list or the official form instructions manually.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
