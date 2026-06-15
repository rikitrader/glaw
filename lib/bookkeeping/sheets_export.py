#!/usr/bin/env python3
"""CSV exporter for GLAW bookkeeping in zero-dependency mode."""
from __future__ import annotations

import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path


def export(transactions, *, title: str, matter: str | None = None,
           default_currency: str = "USD") -> str:
    """Write transactions and summary CSV files, return the transaction CSV path."""
    base = Path(title.replace("/", "-").replace(" ", "_"))
    tx_path = base.with_suffix(".transactions.csv")
    summary_path = base.with_suffix(".summary.csv")
    cat_total: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    cat_count: dict[str, int] = defaultdict(int)
    with tx_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Description", "Amount", "Currency", "Account / Category", "Source", "Hash"])
        for tx in transactions:
            acct = tx.category or "Uncategorized"
            amt = tx.amount if tx.amount is not None else Decimal("0")
            w.writerow([
                tx.booking_date.isoformat() if tx.booking_date else "",
                tx.description or "",
                str(amt),
                tx.currency or default_currency,
                acct,
                tx.source_method,
                tx.transaction_hash,
            ])
            cat_total[acct] += amt
            cat_count[acct] += 1
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Category", "Transactions", "Net Amount"])
        for cat in sorted(cat_total, key=lambda k: cat_total[k]):
            w.writerow([cat, cat_count[cat], str(cat_total[cat])])
        w.writerow(["NET", sum(cat_count.values()), str(sum(cat_total.values()))])
    return str(tx_path)
