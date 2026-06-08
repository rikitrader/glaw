#!/usr/bin/env python3
"""PR14 — ASC 740 income-tax footnote: rate reconciliation + FIN 48 UTP rollforward. No GL."""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import tax_footnote as TF   # noqa: E402


def test_rate_reconciliation():
    rr = TF.rate_reconciliation(1000000, 21, items=[
        {"label": "State taxes, net", "amount": 30000},
        {"label": "Nondeductible expenses", "amount": 5000},
        {"label": "Tax credits", "amount": -15000}])
    assert rr["statutory_tax"] == "210000.00"
    assert rr["total_provision"] == "230000.00"
    assert rr["effective_rate_pct"] == "23.00"
    # the table starts at statutory and ends at the effective rate
    assert rr["reconciliation"][0]["label"] == "Tax at statutory rate"
    assert rr["reconciliation"][-1]["pct"] == "23.00"
    print("  ✓ footnote: statutory 210k → +state +nondeductible −credits → provision 230k, ETR 23%")


def test_utp_rollforward():
    u = TF.utp_rollforward(100000, additions_current=40000, additions_prior=10000,
                           settlements=20000, lapses=5000)
    assert u["ending_balance"] == "125000.00"               # 100 + 40 + 10 − 20 − 5
    # a full lapse/settlement can zero it out
    u2 = TF.utp_rollforward(50000, settlements=30000, lapses=20000)
    assert u2["ending_balance"] == "0.00"
    print("  ✓ footnote: FIN 48 UTB rollforward (beginning + additions − settlements − lapses)")


def main() -> int:
    test_rate_reconciliation(); test_utp_rollforward()
    print("OK: ASC 740 tax footnote (PR14) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
