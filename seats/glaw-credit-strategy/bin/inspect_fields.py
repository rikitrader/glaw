#!/usr/bin/env python3
"""Source-only notice for PDF field inspection."""
import sys


def main() -> int:
    print("PDF field inspection is handled by reviewer workflow in source-only mode.", file=sys.stderr)
    print("Use the generated fill package plus official form instructions for reviewer entry.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
