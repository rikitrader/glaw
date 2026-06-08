#!/usr/bin/env python3
"""GLAW management dashboard — the KPI pack, computed from the posted ledger.

Reads the ledger statements and computes the metrics a CFO/board actually watch:
profitability (gross/net margin), liquidity (current/quick ratio, working capital),
efficiency (DSO/DPO), leverage (debt/equity), and cash (burn, runway). Current vs
non-current is classified by account-name keyword (a documented heuristic, flagged in
the output) since a flat chart of accounts carries no current/non-current tag.
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import statements as S      # noqa: E402
import ledger as L          # noqa: E402

_CUR_ASSET = ("bank", "cash", "receivable", ":ar", "inventory", "prepaid")
_CUR_LIAB = ("payable", ":ap", "accrued", "deferred revenue", "card", "short", "tax payable")
_COGS = ("cogs", "cost of goods", "cost of sales")


def _has(acct: str, kws) -> bool:
    a = acct.lower()
    return any(k in a for k in kws)


def _ratio(n: Decimal, d: Decimal):
    return (n / d) if d else None


def _r2(x):
    return None if x is None else Decimal(x).quantize(Decimal("0.01"))


def compute(book: str, *, as_of: str | None = None, days: int = 365,
            prior_cash: Decimal | None = None, chart: str | None = None) -> dict:
    led = L.Ledger(book)
    postings = [{"account": p["account"], "amount": p["amount"], "id": p["id"]}
                for p in led.postings(as_of)]
    bal = S.balances_from_postings(postings)
    s = S.build(postings=postings)
    pl, bs = s["profit_loss"], s["balance_sheet"]
    rev, exp, ni = pl["revenue_total"], pl["expense_total"], pl["net_income"]

    cash = sum((b for a, b in bal.items() if _has(a, ("bank", "cash"))), Decimal("0"))
    ar = sum((b for a, b in bal.items() if _has(a, ("receivable", ":ar"))), Decimal("0"))
    ap = sum((-b for a, b in bal.items() if _has(a, ("payable", ":ap"))), Decimal("0"))
    inventory = sum((b for a, b in bal.items() if "inventory" in a.lower()), Decimal("0"))
    cogs = sum((r["amount"] for r in pl["expenses"] if _has(r["account"], _COGS)), Decimal("0"))
    gross_profit = rev - cogs if cogs else None

    # current vs non-current: exact via chart tags when provided, else keyword heuristic
    if chart is not None:
        import coa_tags as T
        ov = T.load_chart_tags(chart)
        cur_assets = sum((b for a, b in bal.items()
                          if T.classify(a, ov)["type"] == "asset" and T.classify(a, ov)["current"]), Decimal("0"))
        cur_liab = sum((-b for a, b in bal.items()
                        if T.classify(a, ov)["type"] == "liability" and T.classify(a, ov)["current"]), Decimal("0"))
        tag_mode = f"chart:{chart}"
    else:
        cur_assets = sum((b for a, b in bal.items()
                          if a.split(":", 1)[0] == "Assets" and _has(a, _CUR_ASSET)), Decimal("0"))
        cur_liab = sum((-b for a, b in bal.items()
                        if a.split(":", 1)[0] == "Liabilities" and _has(a, _CUR_LIAB)), Decimal("0"))
        tag_mode = "keyword-heuristic"
    total_liab = bs["liabilities_total"]
    equity = bs["equity_total"]      # already includes current-period net income

    burn = -ni if ni < 0 else Decimal("0")
    months = Decimal(days) / Decimal("30")
    monthly_burn = (burn / months) if (burn > 0 and months) else Decimal("0")

    kpis = {
        "gross_margin": _r2(_ratio(gross_profit, rev) and gross_profit / rev * 100) if gross_profit is not None else None,
        "net_margin_pct": _r2(_ratio(ni, rev) and ni / rev * 100) if rev else None,
        "current_ratio": _r2(_ratio(cur_assets, cur_liab)),
        "quick_ratio": _r2(_ratio(cur_assets - inventory, cur_liab)),
        "working_capital": _r2(cur_assets - cur_liab),
        "dso_days": _r2(_ratio(ar, rev) and ar / rev * days) if rev else None,
        "dpo_days": _r2(_ratio(ap, cogs) and ap / cogs * days) if cogs else None,
        "debt_to_equity": _r2(_ratio(total_liab, equity)),
        "cash": _r2(cash),
        "monthly_burn": _r2(monthly_burn) if monthly_burn else None,
        "runway_months": _r2(_ratio(cash, monthly_burn)) if monthly_burn else None,
    }
    inputs = {"revenue": _r2(rev), "expenses": _r2(exp), "net_income": _r2(ni),
              "cogs": _r2(cogs), "cash": _r2(cash), "ar": _r2(ar), "ap": _r2(ap),
              "inventory": _r2(inventory), "current_assets": _r2(cur_assets),
              "current_liabilities": _r2(cur_liab), "total_liabilities": _r2(total_liab),
              "equity": _r2(equity)}
    note = ("current/non-current from chart tags (exact)" if chart is not None
            else "current/non-current classified by account-name keyword (heuristic)")
    return {"book": book, "as_of": as_of, "days": days, "kpis": kpis, "inputs": inputs,
            "classification": tag_mode, "note": note}


def render_text(d: dict) -> str:
    k = d["kpis"]
    def fmt(v, suf=""):
        return "n/a" if v is None else f"{v:,.2f}{suf}"
    o = ["=" * 56, f"MANAGEMENT DASHBOARD — {d['book']}" + (f"  (as of {d['as_of']})" if d['as_of'] else ""),
         "-" * 56,
         "  PROFITABILITY",
         f"    gross margin        {fmt(k['gross_margin'], '%')}",
         f"    net margin          {fmt(k['net_margin_pct'], '%')}",
         "  LIQUIDITY",
         f"    current ratio       {fmt(k['current_ratio'])}",
         f"    quick ratio         {fmt(k['quick_ratio'])}",
         f"    working capital     {fmt(k['working_capital'])}",
         "  EFFICIENCY",
         f"    DSO (days)          {fmt(k['dso_days'])}",
         f"    DPO (days)          {fmt(k['dpo_days'])}",
         "  LEVERAGE",
         f"    debt / equity       {fmt(k['debt_to_equity'])}",
         "  CASH",
         f"    cash                {fmt(k['cash'])}",
         f"    monthly burn        {fmt(k['monthly_burn'])}",
         f"    runway (months)     {fmt(k['runway_months'])}",
         "-" * 56,
         f"  note: {d['note']}",
         "=" * 56]
    return "\n".join(o)


def main() -> int:
    import argparse, json
    ap = argparse.ArgumentParser(prog="glaw-dashboard")
    ap.add_argument("--book", required=True)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--days", type=int, default=365, help="period length for DSO/DPO/burn (default 365)")
    ap.add_argument("--chart", default=None, help="chart tags name for exact current/non-current")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = compute(a.book, as_of=a.as_of, days=a.days, chart=a.chart)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
