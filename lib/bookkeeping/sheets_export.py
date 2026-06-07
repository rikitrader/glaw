#!/usr/bin/env python3
"""Google Sheets exporter for GLAW bookkeeping.

Creates a categorized workbook from parsed transactions using the user's
authorized-user creds at ~/.gcp/token.json (scopes: spreadsheets + drive).

Tabs:
  * Transactions — one row per tx, with the mapped account/category.
  * Summary      — total + count per category (a mini trial-balance view).
"""
from __future__ import annotations

import os
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = os.path.expanduser("~/.gcp/token.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]


def _svc():
    if not Path(TOKEN).exists():
        raise RuntimeError(f"No Google creds at {TOKEN}")
    creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def export(transactions, *, title: str, matter: str | None = None,
           default_currency: str = "USD") -> str:
    """Create a spreadsheet and return its URL."""
    svc = _svc()

    tx_header = ["Date", "Description", "Amount", "Currency",
                 "Account / Category", "Source", "Hash"]
    tx_rows = []
    cat_total: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    cat_count: dict[str, int] = defaultdict(int)
    for tx in transactions:
        acct = tx.category or "Uncategorized"
        amt = tx.amount if tx.amount is not None else Decimal("0")
        tx_rows.append([
            tx.booking_date.isoformat() if tx.booking_date else "",
            tx.description or "",
            float(amt),
            tx.currency or default_currency,
            acct,
            tx.source_method,
            tx.transaction_hash,
        ])
        cat_total[acct] += amt
        cat_count[acct] += 1

    sum_header = ["Category", "Transactions", "Net Amount"]
    sum_rows = [[c, cat_count[c], float(cat_total[c])]
                for c in sorted(cat_total, key=lambda k: cat_total[k])]
    net = float(sum(cat_total.values()))
    sum_rows.append(["— NET —", len(tx_rows), net])

    meta_line = [f"GLAW Bookkeeping  |  matter: {matter or '(none)'}  |  "
                 f"{len(tx_rows)} transactions  |  NOT tax/accounting advice — "
                 "attorney/CPA work-product for licensed review."]

    ss = svc.spreadsheets().create(body={
        "properties": {"title": title},
        "sheets": [
            {"properties": {"sheetId": 0, "title": "Transactions"}},
            {"properties": {"sheetId": 1, "title": "Summary"}},
        ],
    }).execute()
    sid = ss["spreadsheetId"]

    svc.spreadsheets().values().batchUpdate(spreadsheetId=sid, body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "Transactions!A1", "values": [meta_line, tx_header] + tx_rows},
            {"range": "Summary!A1", "values": [sum_header] + sum_rows},
        ],
    }).execute()

    # Bold + freeze header rows, format both sheets.
    reqs = []
    for shid, header_row in ((0, 1), (1, 0)):  # Transactions header is row 2 (idx1)
        reqs.append({"repeatCell": {
            "range": {"sheetId": shid, "startRowIndex": header_row,
                      "endRowIndex": header_row + 1},
            "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
            "fields": "userEnteredFormat.textFormat.bold"}})
        reqs.append({"updateSheetProperties": {
            "properties": {"sheetId": shid,
                           "gridProperties": {"frozenRowCount": header_row + 1}},
            "fields": "gridProperties.frozenRowCount"}})
    svc.spreadsheets().batchUpdate(spreadsheetId=sid, body={"requests": reqs}).execute()

    return f"https://docs.google.com/spreadsheets/d/{sid}/edit"
