#!/usr/bin/env python3
"""W1 — statute of limitations (§6501 assessment / §6511 refund). No GL."""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import statute_of_limitations as S   # noqa: E402


def test_assessment_3_and_6_year():
    a = S.assessment_sol(due_date="2021-04-15", filed_date="2021-04-15")
    assert a["years"] == 3 and a["assessment_deadline"] == "2024-04-15"
    a6 = S.assessment_sol(due_date="2021-04-15", filed_date="2021-04-15", omission_over_25pct=True)
    assert a6["years"] == 6 and a6["assessment_deadline"] == "2027-04-15"
    print("  ✓ SOL: 3-year general / 6-year >25% omission assessment deadlines")


def test_later_of_clock():
    a = S.assessment_sol(due_date="2021-04-15", filed_date="2022-06-01")  # late-filed
    assert a["assessment_deadline"] == "2025-06-01"                       # clock starts at filing
    print("  ✓ SOL: clock starts at the LATER of due date or filing date")


def test_open_indefinitely():
    assert S.assessment_sol(due_date="2021-04-15", fraud=True)["sol_open_indefinitely"]
    assert S.assessment_sol(due_date="2021-04-15", filed=False)["sol_open_indefinitely"]
    print("  ✓ SOL: fraud and non-filed returns stay open indefinitely")


def test_refund_and_status():
    r = S.refund_sol(filed_date="2021-04-15", paid_date="2023-01-01")
    assert r["refund_deadline"] == "2025-01-01"                           # later of 3-yr-filing / 2-yr-payment
    assert S.status_as_of("2024-04-15", "2025-01-01") == "EXPIRED"
    assert S.status_as_of("2024-04-15", "2024-01-01") == "OPEN"
    print("  ✓ SOL: refund deadline (later of) + OPEN/EXPIRED status as of a date")


def main() -> int:
    test_assessment_3_and_6_year(); test_later_of_clock(); test_open_indefinitely(); test_refund_and_status()
    print("OK: statute of limitations (W1) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
