#!/usr/bin/env python3
"""Smoke test for JE forensics + Benford. Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import je_test as J          # noqa: E402


def test_benford():
    # a log-uniform set conforms; an all-leading-9 set does not
    conforming = [Decimal(str(round(10 ** (((i * 0.013) % 3) + 1), 2))) for i in range(400)]
    b = J.benford(conforming)
    assert b["sufficient_data"] and b["mad"] < 0.012, (b["mad"], b["conformity"])
    bad = J.benford([Decimal("900") for _ in range(100)])      # every amount leads with 9
    assert bad["conformity"] == "nonconformity" and bad["mad"] > 0.05
    # digit shares sum to ~1 and expected matches Benford
    assert abs(sum(r["observed"] for r in b["digits"]) - 1.0) < 0.01
    assert abs(J.BENFORD[1] - 0.30103) < 1e-4                  # P(1) = 30.1%
    print("  ✓ benford: log-uniform conforms (MAD<0.012), all-9s nonconforms, P(1)=30.1%")


def test_je_flags():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-je-")
    import importlib
    import ledger as L
    importlib.reload(L)
    importlib.reload(J)
    led = L.Ledger("co")
    # 50,000 round-dollar entry booked on Saturday 2026-06-06
    led.post({"date": "2026-06-06", "memo": "big round", "source": "manual",
              "lines": [{"account": "Expenses:Consulting", "debit": 50000},
                        {"account": "Assets:Bank:Checking", "credit": 50000}]})
    s = J.scan("co")
    f = s["findings"][0]
    for r in ("round-dollar", "weekend", "large", "manual"):
        assert r in f["reasons"], (r, f["reasons"])
    assert s["flagged"] == 1
    print("  ✓ je-test: 50k Saturday entry flags round-dollar + weekend + large + manual")


def main() -> int:
    test_benford()
    test_je_flags()
    print("OK: JE forensics + Benford smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
