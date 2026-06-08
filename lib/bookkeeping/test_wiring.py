#!/usr/bin/env python3
"""Regression lock for the orchestrator-wiring fix: /glaw-accounting (the division lead the
main /glaw pipeline routes accounting work to) must route to the full finance subsystem.
The glaw-doctor ref-gate only proves names *resolve* if referenced — this asserts the lead
actually references them, so dropping the wiring fails CI. Stdlib only."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]   # lib/bookkeeping/ -> lib/ -> glaw/


def test_accounting_routes_to_finance_subsystem():
    txt = (ROOT / "accounting" / "SKILL.md").read_text(encoding="utf-8")
    required = ["/glaw-ledger", "/glaw-controller", "/glaw-cfo", "/glaw-audit",
                "/glaw-reconstruct", "/glaw-close"]
    missing = [s for s in required if s not in txt]
    assert not missing, f"/glaw-accounting lost routing to: {missing} (orchestrator-wiring regression)"
    print("  ✓ wiring: /glaw-accounting routes to ledger/controller/cfo/audit/reconstruct/close")


def main() -> int:
    test_accounting_routes_to_finance_subsystem()
    print("OK: orchestrator-wiring regression lock passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
