#!/usr/bin/env python3
"""Smoke test for the invoice/bill extractor. No network; pure-text parsing."""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import invoice_extract as IV   # noqa: E402

SAMPLE = """ACME Roofing Supplies LLC
INVOICE
Invoice #: INV-2026-0457
Date: 2026-05-14
Bill To: Henderson Roofing

Description                 Qty    Unit Price    Amount
Architectural shingles      40     85.00         3,400.00
Underlayment rolls          12     45.00         540.00
Delivery                     1     150.00        150.00

Subtotal                                         4,090.00
Sales Tax (7%)                                   286.30
Total Due                                        4,376.30
"""


def test_parse():
    inv = IV.parse_invoice(SAMPLE)
    assert inv["vendor"] == "ACME Roofing Supplies LLC"
    assert inv["invoice_number"] == "INV-2026-0457"        # not the "INVOICE" header
    assert inv["date"] == "2026-05-14"
    assert Decimal(inv["total"]) == Decimal("4376.30")
    assert Decimal(inv["tax"]) == Decimal("286.30")
    assert len(inv["line_items"]) == 3
    assert Decimal(inv["line_items"][0]["amount"]) == Decimal("3400.00")
    print("  ✓ invoice parse: vendor + INV-2026-0457 + date + 3 line items + tax + total")


def test_draft_je_balances_and_reconciles():
    inv = IV.parse_invoice(SAMPLE)
    je = IV.to_bill_je(inv)
    dr = sum(Decimal(l["debit"]) for l in je["lines"])
    cr = sum(Decimal(l["credit"]) for l in je["lines"])
    assert dr == cr == Decimal("4376.30"), (dr, cr)        # balanced
    assert je["reconciles"] is True                        # items 4,090 + tax 286.30 == total
    # the credit is to AP for the vendor
    ap = [l for l in je["lines"] if l["account"].startswith("Liabilities:AP")]
    assert ap and Decimal(ap[0]["credit"]) == Decimal("4376.30")
    print("  ✓ draft bill JE: Dr expenses+tax / Cr AP, balances to 4,376.30, reconciles")


def test_non_reconciling_is_flagged():
    # line items (100) + tax (10) = 110, but the stated total is 200 → must flag, still balance
    bad = "Vendor X\nInvoice #: A1\nWidget 100.00\nTax 10.00\nTotal Due 200.00\n"
    inv = IV.parse_invoice(bad)
    je = IV.to_bill_je(inv)
    assert je["reconciles"] is False
    assert sum(Decimal(l["debit"]) for l in je["lines"]) == sum(Decimal(l["credit"]) for l in je["lines"])
    assert any("plug" in (l.get("memo", "")) for l in je["lines"])   # the discrepancy is plugged + flagged
    print("  ✓ invoice: a non-reconciling bill is flagged (plug + reconciles=False), entry still balances")


def main() -> int:
    test_parse()
    test_draft_je_balances_and_reconciles()
    test_non_reconciling_is_flagged()
    print("OK: invoice/bill extractor smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
