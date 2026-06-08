#!/usr/bin/env python3
"""Tamper-evidence tests for the hash-CHAINED ledger. Proves the GL detects not just an edit
to a retained entry, but a DELETION, an INSERTION, and a CURRENCY tamper — the gaps the old
independent-per-entry hash missed. Temp GLAW_HOME; no network."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _fresh():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-tamper-")
    import importlib
    import ledger as L
    importlib.reload(L)
    led = L.Ledger("t")
    for i in range(1, 5):
        led.post({"date": f"2026-01-0{i}", "memo": f"e{i}", "currency": "USD",
                  "lines": [{"account": "Assets:Bank:Checking", "debit": 100},
                            {"account": "Income:Sales", "credit": 100}]})
    return L, led


def _lines(led):
    return led.path.read_text().splitlines()


def _write(led, lines):
    led.path.write_text("\n".join(lines) + "\n")


def test_clean_book_passes():
    L, led = _fresh()
    assert L.verify_integrity(led.entries()) == [], "a clean chained book must verify"
    # the hash must be full SHA-256 (256-bit) — a 64-bit truncation is the weak link
    assert len(led.entries()[0]["entry_hash"]) == 64, "entry hash must be full 256-bit (64 hex)"
    print("  ✓ tamper: clean book verifies; entry hash is full 256-bit (64 hex)")


def test_legacy_short_hash_still_verifies():
    import hashlib
    import json as _json
    L, led = _fresh()
    # synthesize a pre-chain legacy entry with a 16-hex hash (the old scheme)
    e = {"id": 99, "date": "2026-02-01", "memo": "legacy",
         "lines": [{"account": "Assets:Bank:Checking", "debit": "5", "credit": "0", "memo": ""},
                   {"account": "Income:Sales", "debit": "0", "credit": "5", "memo": ""}]}
    e["entry_hash"] = hashlib.sha256(_json.dumps(
        {k: e[k] for k in ("id", "date", "memo", "lines")}, sort_keys=True, default=str
    ).encode()).hexdigest()[:16]
    led.path.write_text(_json.dumps(e) + "\n"); led._entries_cache = None
    assert L.verify_integrity(led.entries()) == [], "a legacy 16-hex entry must still self-verify"
    print("  ✓ tamper: legacy 16-hex entries still verify (recomputed at their stored length)")


def test_detects_field_and_currency_edit():
    L, led = _fresh()
    lines = _lines(led)
    e = json.loads(lines[1]); e["lines"][0]["debit"] = "999"      # edit an amount
    lines[1] = json.dumps(e); _write(led, lines)
    probs = L.verify_integrity(led.entries())
    assert any("tamper" in r for _, r in probs), probs
    # currency tamper (the field the OLD hash missed)
    L, led = _fresh()
    lines = _lines(led)
    e = json.loads(lines[1]); e["currency"] = "EUR"
    lines[1] = json.dumps(e); _write(led, lines)
    probs = L.verify_integrity(led.entries())
    assert any("currency" in r or "tamper" in r for _, r in probs), probs
    print("  ✓ tamper: an amount edit AND a currency change are both detected")


def test_detects_deletion():
    L, led = _fresh()
    lines = _lines(led)
    del lines[2]                                                  # delete entry #3
    _write(led, lines)
    probs = L.verify_integrity(led.entries())
    assert any("chain break" in r for _, r in probs), probs
    print("  ✓ tamper: a DELETED entry breaks the chain (was invisible before)")


def test_detects_insertion_and_reorder():
    L, led = _fresh()
    lines = _lines(led)
    lines.insert(2, lines[1])                                     # duplicate/insert a line
    _write(led, lines)
    assert any("chain break" in r for _, r in L.verify_integrity(led.entries()))
    L, led = _fresh()
    lines = _lines(led)
    lines[1], lines[2] = lines[2], lines[1]                       # reorder
    _write(led, lines)
    assert any("chain break" in r for _, r in L.verify_integrity(led.entries()))
    print("  ✓ tamper: INSERTION and REORDER both break the chain")


def test_books_doctor_fails_on_tamper():
    L, led = _fresh()
    import importlib
    import books_doctor as BD
    importlib.reload(BD)
    BD.FAIL = 0; BD.WARN = 0
    assert BD.run_ledger("t") == 0, "clean book is bulletproof"
    lines = _lines(led); del lines[2]; _write(led, lines)         # delete an entry
    BD.FAIL = 0; BD.WARN = 0
    assert BD.run_ledger("t") == 1, "books-doctor MUST fail a tampered (deleted-entry) book"
    print("  ✓ tamper: glaw-books-doctor --book fails a deleted-entry book, passes a clean one")


def main() -> int:
    test_clean_book_passes()
    test_legacy_short_hash_still_verifies()
    test_detects_field_and_currency_edit()
    test_detects_deletion()
    test_detects_insertion_and_reorder()
    test_books_doctor_fails_on_tamper()
    print("OK: tamper-evidence (hash-chain) tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
