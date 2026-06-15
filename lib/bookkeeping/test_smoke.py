#!/usr/bin/env python3
"""Smoke test for the GLAW bookkeeping engine (glaw_engine + runner).

Deterministic only — no LLM, no network, no OCR. Exercises the path that must
never silently break: parse a CSV statement → dedupe → account-map → Golden-Rule
balance verify → export hledger / beancount / json.

Run from the repository checkout:
    python3 lib/bookkeeping/test_smoke.py
Exit 0 = healthy.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
ENV = {**os.environ, "PYTHONPATH": str(HERE)}


def _run(args: list[str]) -> str:
    p = subprocess.run([sys.executable, str(HERE / "runner.py"), *args],
                       capture_output=True, text=True, env=ENV)
    if p.returncode != 0:
        raise AssertionError(f"runner exited {p.returncode}\nSTDERR:\n{p.stderr}")
    return p.stdout


def main() -> int:
    # imports resolve under the renamed package
    from glaw_engine.export.ledger import to_hledger, to_beancount        # noqa: F401
    from glaw_engine.enrichment.account_mapper import AccountMapper        # noqa: F401
    from glaw_engine.transaction_deduplicator import Deduplicator          # noqa: F401
    from glaw_engine.hybrid.orchestrator import smart_ingest               # noqa: F401

    d = Path(tempfile.mkdtemp(prefix="glaw-bk-smoke-"))
    csv = d / "stmt.csv"
    csv.write_text(
        "Date,Description,Amount\n"
        "2026-01-04,LP CAPITAL CALL,500000.00\n"
        "2026-01-09,SHELL FUEL,-200.00\n"
        "2026-01-09,SHELL FUEL,-200.00\n",   # exact dup of the row above (same date)
        encoding="utf-8",
    )
    coa = d / "coa.json"
    coa.write_text(json.dumps({
        "default": "Expenses:Uncategorized",
        "rules": [
            {"pattern": "CAPITAL CALL", "account": "Equity:LP:Contributions"},
            {"pattern": "FUEL", "account": "Expenses:Auto:Fuel"},
        ],
    }), encoding="utf-8")

    # 1) CSV -> hledger, account-mapped (full account paths pass through)
    hl = _run([str(csv), "--map", str(coa), "--format", "hledger"])
    assert "Equity:LP:Contributions" in hl, "CAPITAL CALL not mapped to Equity"
    assert "Expenses:Auto:Fuel" in hl, "FUEL not mapped to Expenses:Auto:Fuel"
    assert "Assets:Bank:Checking" in hl and "500000" in hl, "ledger bank posting missing"

    # 2) idempotent dedup: the exact-dup FUEL row collapses → 2 unique tx, not 3
    js = json.loads(_run([str(csv), "--format", "json"]))
    assert js["transactions"] == 2, f"dedup failed: expected 2 unique tx, got {js['transactions']}"

    # 3) Golden-Rule balance verify on a clean (no-dup) statement: 0 + 500000 - 200 = 499800
    clean = d / "clean.csv"
    clean.write_text(
        "Date,Description,Amount\n"
        "2026-01-04,LP CAPITAL CALL,500000.00\n"
        "2026-01-09,SHELL FUEL,-200.00\n",
        encoding="utf-8",
    )
    jv = json.loads(_run([str(clean), "--open", "0", "--close", "499800", "--format", "json"]))
    status = jv["audit"][0]["balance_status"]
    assert status == "verified", f"Golden Rule should verify, got {status!r}"
    # and a wrong closing balance must flag a discrepancy (the check actually checks)
    jd = json.loads(_run([str(clean), "--open", "0", "--close", "999999", "--format", "json"]))
    assert jd["audit"][0]["balance_status"] == "discrepancy", "Golden Rule failed to catch a bad balance"

    # 4) beancount export renders both postings
    bc = _run([str(clean), "--map", str(coa), "--format", "beancount"])
    assert 'txn ""' in bc and "Equity:LP:Contributions" in bc, "beancount export malformed"

    print("OK: bookkeeping engine smoke passed "
          "(parse + dedup + map + Golden-Rule verify + hledger/beancount/json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
