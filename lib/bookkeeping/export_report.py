#!/usr/bin/env python3
"""GLAW export — a styled, printable financial report from the ledger.

Combines the statements, indirect cash flow, dashboard KPIs, and the MD&A narrative into
one self-contained, branded HTML document. Optionally writes the trial balance to a local
CSV. Every number comes from the posted ledger.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import statements as S        # noqa: E402
import ledger as L            # noqa: E402
import dashboard as DASH      # noqa: E402
import narrative as NARR      # noqa: E402
import cashflow_cli as CF     # noqa: E402

_CSS = """
:root{--navy:#1A3FA0;--gold:#C9A227;--ink:#0d1b2e;--rule:#d8dee9}
*{box-sizing:border-box}body{font:14px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:var(--ink);margin:0;background:#fff}
.wrap{max-width:860px;margin:0 auto;padding:48px 40px}
header{border-bottom:3px solid var(--navy);padding-bottom:16px;margin-bottom:28px}
header .stamp{color:var(--navy);font-weight:700;letter-spacing:.12em;text-transform:uppercase;font-size:12px}
h1{font-size:26px;margin:6px 0 2px}.sub{color:#5b6573;font-size:13px}
h2{color:var(--navy);border-bottom:1px solid var(--rule);padding-bottom:6px;margin-top:34px;font-size:18px}
h3{color:var(--ink);font-size:15px;margin-top:20px}
pre{background:#f6f8fc;border:1px solid var(--rule);border-radius:6px;padding:14px 16px;overflow:auto;font:12px/1.45 SFMono-Regular,Menlo,Consolas,monospace}
table{border-collapse:collapse;width:100%;margin:10px 0}td,th{border:1px solid var(--rule);padding:6px 10px;text-align:left}
th{background:#f0f3fa;color:var(--navy)}td.n{text-align:right;font-variant-numeric:tabular-nums}
.kpi{display:grid;grid-template-columns:repeat(2,1fr);gap:0}
footer{margin-top:40px;border-top:1px solid var(--rule);padding-top:14px;color:#5b6573;font-size:11px}
@media print{.wrap{padding:0}body{font-size:12px}.noprint{display:none}}
"""


def _md_to_html(md: str) -> str:
    out, in_list = [], False
    for line in md.splitlines():
        s = line.rstrip()
        if s.startswith("### "):
            if in_list: out.append("</ul>"); in_list = False
            out.append(f"<h3>{html.escape(s[4:])}</h3>")
        elif s.startswith("## "):
            if in_list: out.append("</ul>"); in_list = False
            out.append(f"<h2>{html.escape(s[3:])}</h2>")
        elif s.startswith("# "):
            continue   # the document title is rendered in the header
        elif s.startswith("- "):
            if not in_list: out.append("<ul>"); in_list = True
            out.append(f"<li>{_inline(s[2:])}</li>")
        elif not s:
            if in_list: out.append("</ul>"); in_list = False
        elif s.startswith("---"):
            continue
        else:
            if in_list: out.append("</ul>"); in_list = False
            out.append(f"<p>{_inline(s)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def _inline(t: str) -> str:
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t


def _kpi_table(kpis: dict) -> str:
    label = {"gross_margin": "Gross margin %", "net_margin_pct": "Net margin %",
             "current_ratio": "Current ratio", "quick_ratio": "Quick ratio",
             "working_capital": "Working capital", "dso_days": "DSO (days)",
             "dpo_days": "DPO (days)", "debt_to_equity": "Debt / equity",
             "cash": "Cash", "runway_months": "Runway (months)"}
    rows = "".join(f"<tr><th>{label[k]}</th><td class='n'>{'n/a' if kpis.get(k) is None else kpis[k]}</td></tr>"
                   for k in label if k in kpis)
    return f"<table>{rows}</table>"


def generate_html(book: str, *, period: str | None = None, as_of: str | None = None,
                  entity: str = "the Company", chart: str | None = None) -> str:
    postings = [{"account": p["account"], "amount": p["amount"], "id": p["id"]}
                for p in L.Ledger(book).postings(as_of)]
    s = S.build(postings=postings)
    stmts = S.render_text(s)
    cf = CF.compute(book, period=period, chart=chart) if (period or as_of is None) else None
    cf_txt = CF.render_text(cf) if cf else ""
    dash = DASH.compute(book, as_of=as_of, chart=chart)
    narr = NARR.generate(book, period=period, as_of=as_of, entity=entity)
    title = f"{entity} — Financial Report" + (f" ({period})" if period else "")
    body = [
        "<h2>Financial statements</h2>", f"<pre>{html.escape(stmts)}</pre>",
    ]
    if cf_txt:
        body += ["<h2>Statement of cash flows (indirect)</h2>", f"<pre>{html.escape(cf_txt)}</pre>"]
    body += ["<h2>Key performance indicators</h2>", _kpi_table(dash["kpis"]),
             "<h2>Management discussion &amp; notes</h2>", _md_to_html(narr)]
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>{html.escape(title)}</title><style>{_CSS}</style></head><body><div class="wrap">
<header><div class="stamp">GLAW · Financial Report</div>
<h1>{html.escape(entity)}</h1>
<div class="sub">{html.escape(('Period ' + period) if period else ('As of ' + as_of if as_of else 'Cumulative'))} · prepared from the posted general ledger</div></header>
{''.join(body)}
<footer>Not legal, tax, or accounting advice. Prepared for review and sign-off by a licensed CPA / attorney.
Generated by GLAW from the double-entry general ledger; every figure traces to a posted journal entry.</footer>
</div></body></html>"""


def push_gsheet(book: str, title: str) -> str:
    """Write the trial balance to a local CSV in zero-dependency mode."""
    tb = S.trial_balance(L.Ledger(book).balances())
    out = Path(title.replace("/", "-").replace(" ", "_")).with_suffix(".trial_balance.csv")
    out.write_text("Account,Debit,Credit\n" + "\n".join(
        f"{r['account']},{r['debit']},{r['credit']}" for r in tb["rows"]) + "\n", encoding="utf-8")
    return str(out)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-export")
    ap.add_argument("--book", required=True)
    ap.add_argument("--period", default=None)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--entity", default="the Company")
    ap.add_argument("--chart", default=None)
    ap.add_argument("--out", default=None, help="write HTML here (else stdout)")
    ap.add_argument("--gsheet", action="store_true", help="also write the trial balance to local CSV")
    a = ap.parse_args()
    htmldoc = generate_html(a.book, period=a.period, as_of=a.as_of, entity=a.entity, chart=a.chart)
    if a.out:
        Path(a.out).write_text(htmldoc)
        print(f"wrote {a.out}  ({len(htmldoc):,} bytes) — open and print to PDF")
    else:
        print(htmldoc)
    if a.gsheet:
        print("gsheet: " + push_gsheet(a.book, f"{a.entity} — Financial Report"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
