#!/usr/bin/env python3
"""Source-input tests for Sheets URLs, CSV alias output, and PDF/OCR failures."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))


def test_google_sheet_url_conversion():
    import runner
    url = "https://docs.google.com/spreadsheets/d/abc123/edit#gid=456"
    assert runner._google_sheet_csv_url(url) == (
        "https://docs.google.com/spreadsheets/d/abc123/export?format=csv&gid=456"
    )
    print("  ✓ sheets: edit URL converts to CSV export URL")


def test_csv_url_download_and_ingest():
    import runner

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return b"date,description,amount\n2026-01-01,Deposit,100.00\n"

    calls = []
    real_urlopen = runner.urllib.request.urlopen
    try:
        def fake_urlopen(req, timeout):
            calls.append((req.full_url, timeout, dict(req.header_items())))
            return Response()

        runner.urllib.request.urlopen = fake_urlopen
        path = runner._download_sheet_or_csv("https://example.com/sheet.csv", google_auth="none")
        assert path.exists() and "Deposit" in path.read_text(encoding="utf-8")
        assert calls and calls[0][0] == "https://example.com/sheet.csv"
    finally:
        runner.urllib.request.urlopen = real_urlopen
    print("  ✓ sheets: CSV URL downloads through stdlib urllib without network sockets")


def test_gcloud_auth_header_path():
    import runner
    calls: list[list[str]] = []

    class Proc:
        returncode = 0
        stdout = "TOKEN\n"

    real_run = runner.subprocess.run
    try:
        def fake_run(args, **_kwargs):
            calls.append(args)
            return Proc()
        runner.subprocess.run = fake_run
        assert runner._gcloud_token() == "TOKEN"
        assert calls and calls[0][:2] == ["gcloud", "auth"]
    finally:
        runner.subprocess.run = real_run
    print("  ✓ sheets: gcloud token path is wired without Google SDKs")


def test_csv_format_alias():
    sample = Path(tempfile.mkdtemp(prefix="glaw-csv-alias-")) / "bank.csv"
    sample.write_text("date,description,amount\n2026-01-01,Deposit,100.00\n", encoding="utf-8")
    out_dir = Path(tempfile.mkdtemp(prefix="glaw-csv-export-"))
    env = {**os.environ, "GLAW": str(ROOT), "GLAW_EXPORT_DIR": str(out_dir),
           "PYTHONPATH": f"{HERE}:{ROOT}"}
    proc = subprocess.run(
        [str(ROOT / "bin/glaw-bank-ingest"), str(sample), "--format", "csv", "--sheet-title", "glaw-source-test"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0, proc.stderr
    out_path = Path(proc.stdout.strip().splitlines()[-1])
    assert out_path.exists() and "Deposit" in out_path.read_text(encoding="utf-8")
    print("  ✓ output: --format csv writes local CSV export")


def test_bad_pdf_clean_error():
    bad = Path(tempfile.mkdtemp(prefix="glaw-bad-pdf-")) / "bad.pdf"
    bad.write_text("%PDF-1.4", encoding="utf-8")
    env = {**os.environ, "GLAW": str(ROOT), "PYTHONPATH": f"{HERE}:{ROOT}"}
    proc = subprocess.run(
        [str(ROOT / "bin/glaw-bank-ingest"), str(bad), "--format", "json"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 2
    assert "ERROR:" in proc.stderr and "Traceback" not in proc.stderr
    print("  ✓ pdf: invalid PDF fails cleanly without traceback")


def main() -> int:
    test_google_sheet_url_conversion()
    test_csv_url_download_and_ingest()
    test_gcloud_auth_header_path()
    test_csv_format_alias()
    test_bad_pdf_clean_error()
    print("OK: source input tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
