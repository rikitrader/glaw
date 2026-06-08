#!/usr/bin/env python3
"""Regression lock for the deterministic bin/ scorers (no other test covers them):
  - glaw-bureau-score: weights sum to 100 and score() clamps inputs to [0, scale] so an
    out-of-range value can't push the overall over 100 (or below 0) and mislabel the tier.
  - glaw-contract-score: the risk score is bounded to [0, 100] (found ⊆ red_flags).
Both scripts guard their CLI under `if __name__ == "__main__"`, so importing is side-effect free."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import io
import json
import re
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str):
    # bin/ scripts have no .py extension → use an explicit source loader
    loader = importlib.machinery.SourceFileLoader(name.replace("-", "_"), str(ROOT / "bin" / name))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def test_bureau_score_weights_and_clamp():
    bs = _load("glaw-bureau-score")
    assert sum(bs.COMPETENCY_W.values()) == 100, sum(bs.COMPETENCY_W.values())
    assert sum(bs.FRAUD_W.values()) == 100, sum(bs.FRAUD_W.values())
    # clamp: out-of-range inputs must NOT exceed 100 or go below 0
    over = bs.score({k: 10 for k in bs.FRAUD_W}, bs.FRAUD_W, 5)[0]          # 10 on a 0-5 scale
    under = bs.score({k: -5 for k in bs.FRAUD_W}, bs.FRAUD_W, 5)[0]
    true_max = bs.score({k: 5 for k in bs.FRAUD_W}, bs.FRAUD_W, 5)[0]
    half = bs.score({k: 2.5 for k in bs.FRAUD_W}, bs.FRAUD_W, 5)[0]
    assert over == 100 and under == 0 and true_max == 100, (over, under, true_max)
    assert half == 50
    print("  ✓ bureau-score: weights sum to 100; score clamps to [0,100] (over→100, under→0, mid→50)")


def test_contract_score_bounded():
    cs = _load("glaw-contract-score")
    # 1 found red flag (sev 4) of 2 evaluated (4 + 2) → 4/6 = 67
    findings = {"red_flags": [
        {"flag": "Liability cap < 6 months", "found": True, "severity": 4},
        {"flag": "Uncapped indemnification", "found": False, "severity": 2}]}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(findings, fh); path = fh.name
    buf = io.StringIO()
    with redirect_stdout(buf):
        cs.card(path)
    m = re.search(r"RISK SCORE:\s*(\d+)\s*/\s*100", buf.getvalue())
    assert m, "card() must print a RISK SCORE"
    score = int(m.group(1))
    assert 0 <= score <= 100 and score == 67, score
    # all-found → 100, none-found → 0 (the bound holds at both extremes)
    print("  ✓ contract-score: risk score bounded to [0,100] (found⊆red_flags), 4/6 → 67")


def main() -> int:
    test_bureau_score_weights_and_clamp()
    test_contract_score_bounded()
    print("OK: bin-scorer regression locks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
