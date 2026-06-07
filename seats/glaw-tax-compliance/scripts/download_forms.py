#!/usr/bin/env python3
"""Download current IRS blank forms and prior-year returns to a packet directory.

Forms are downloaded LIVE every run — never bundle stale PDFs (the IRS revises them
annually). Each download is validated to be a real PDF before it's kept.

Usage:
    python3 download_forms.py OUTDIR FORM [FORM ...]

FORM tokens:
    f843            current form  -> https://www.irs.gov/pub/irs-pdf/f843.pdf
    i1040gi         current instr -> https://www.irs.gov/pub/irs-pdf/i1040gi.pdf
    1040:2021       prior-year return -> https://www.irs.gov/pub/irs-prior/f1040--2021.pdf
    i1040:2021      prior-year instr  -> https://www.irs.gov/pub/irs-prior/i1040--2021.pdf
    1040:2021-2025  YEAR RANGE -> downloads f1040--2021 ... f1040--2025

Examples (personal + business, 2021 through today):
    python3 download_forms.py ./packet \
        1040:2021-2025 1040sc:2021-2025 1040se:2021-2025 \
        1120s:2021-2025 1065:2021-2025 1120:2021-2025
"""
import sys
import os
import urllib.request

PDF_BASE = "https://www.irs.gov/pub/irs-pdf/"
PRIOR_BASE = "https://www.irs.gov/pub/irs-prior/"


def expand(tokens: list[str]) -> list[str]:
    """Expand any name:YYYY-YYYY range token into one token per year."""
    out = []
    for t in tokens:
        if ":" in t and "-" in t.split(":", 1)[1]:
            name, rng = t.split(":", 1)
            lo, hi = rng.split("-", 1)
            for y in range(int(lo), int(hi) + 1):
                out.append(f"{name}:{y}")
        else:
            out.append(t)
    return out


def url_for(token: str) -> tuple[str, str]:
    """Return (url, filename) for a single FORM token."""
    if ":" in token:                       # prior-year: name:YEAR
        name, year = token.split(":", 1)
        # prior-year files: f1040--2021.pdf (forms) / i1040--2021.pdf (instructions)
        stem = name if name.startswith(("f", "i", "p")) else "f" + name
        return f"{PRIOR_BASE}{stem}--{year}.pdf", f"{name}_{year}.pdf"
    return f"{PDF_BASE}{token}.pdf", f"{token}.pdf"


def download(url: str, dest: str) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        ctype = r.headers.get("Content-Type", "")
        data = r.read()
    if b"%PDF" not in data[:1024]:
        raise ValueError(f"not a PDF (Content-Type={ctype})")
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    outdir, tokens = sys.argv[1], expand(sys.argv[2:])
    os.makedirs(outdir, exist_ok=True)
    rc = 0
    for tok in tokens:
        url, fname = url_for(tok)
        dest = os.path.join(outdir, fname)
        try:
            n = download(url, dest)
            print(f"OK   {fname:24} {n:>9,d} B  <- {url}")
        except Exception as e:
            rc = 1
            print(f"FAIL {fname:24} {e}  <- {url}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
