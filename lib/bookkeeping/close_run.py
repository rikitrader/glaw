#!/usr/bin/env python3
"""GLAW scheduled close — run the whole period close non-interactively (cron-safe).

Executes the deterministic close pipeline on a ledger book and writes a dated close
package, with a single hard gate: the books-doctor must pass. Exit code reflects the
gate (0 = closed/bulletproof, 1 = problems found) so a cron job alerts on failure.

Pipeline:
  (optional) ingest new statements  →  ⛔ books-doctor gate  →  statements  →
  comparative (if --period)  →  dashboard  →  narrative  →  (optional) lock period.
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
from calendar import monthrange
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L            # noqa: E402
import statements as S        # noqa: E402
import books_doctor as BD     # noqa: E402
import dashboard as DASH      # noqa: E402
import narrative as NARR      # noqa: E402

LEDGER_BIN = str(Path(__file__).resolve().parents[2] / "bin" / "glaw-ledger")


def _capture(fn, *a, **k):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = fn(*a, **k)
    return rc, buf.getvalue()


def _period_end(period: str) -> str:
    y, m = (int(x) for x in period.split("-")[:2])
    return date(y, m, monthrange(y, m)[1]).isoformat()


def run_close(book: str, *, period: str | None = None, as_of: str | None = None,
              out_dir: str | None = None, lock: bool = False, entity: str = "the Company",
              ingest: str | None = None, chart: str | None = None, mapfile: str | None = None,
              post_subledgers: bool = False) -> dict:
    log: list[str] = []
    artifacts: dict[str, str] = {}

    # 0a — auto-post the period's registered subledger entries (depreciation, deferred rev, loans)
    if post_subledgers:
        import subledger as SUB
        through = as_of or (_period_end(period) if period else date.today().isoformat())
        sr = SUB.post_due(book, through)
        log.append(f"subledgers: {sr['posted']} entries posted through {sr['through']}")

    # 0 — optional ingest of new statements (reuses the tested glaw-ledger rebuild)
    if ingest:
        cmd = [LEDGER_BIN, "--book", book, "rebuild", ingest]
        if chart:
            cmd += ["--chart", chart]
        if mapfile:
            cmd += ["--map", mapfile]
        r = subprocess.run(cmd, capture_output=True, text=True)
        log.append(f"ingest: {r.stdout.strip().splitlines()[0] if r.stdout.strip() else 'no output'}")

    # 1 — the gate (hard)
    BD.FAIL = 0
    BD.WARN = 0
    gate_rc, gate_out = _capture(BD.run_ledger, book, as_of=as_of)
    artifacts["books-doctor.txt"] = gate_out
    gate_passed = gate_rc == 0
    log.append(f"gate: {'BULLETPROOF' if gate_passed else 'PROBLEMS FOUND'} "
               f"(failures {BD.FAIL}, warnings {BD.WARN})")

    # 2 — statements
    postings = [{"account": p["account"], "amount": p["amount"], "id": p["id"]}
                for p in L.Ledger(book).postings(as_of)]
    s = S.build(postings=postings)
    artifacts["statements.txt"] = S.render_text(s)

    # 3 — comparative (needs a period)
    if period:
        import comparative as COMP
        artifacts["comparative.txt"] = COMP.render_text(COMP.comparative(book, period))

    # 4 — dashboard
    artifacts["dashboard.txt"] = DASH.render_text(DASH.compute(book, as_of=as_of))

    # 5 — narrative
    artifacts["narrative.md"] = NARR.generate(book, period=period, as_of=as_of, entity=entity)

    # 6 — lock (only if the gate passed)
    locked_through = None
    if lock and gate_passed:
        through = as_of or (_period_end(period) if period else date.today().isoformat())
        locked_through = L.Ledger(book).lock(through)["locked_through"]
        log.append(f"locked through {locked_through}")
    elif lock and not gate_passed:
        log.append("NOT locked — gate failed")

    summary = {"book": book, "period": period, "as_of": as_of,
               "gate_passed": gate_passed, "failures": BD.FAIL, "warnings": BD.WARN,
               "net_income": str(s["profit_loss"]["net_income"]),
               "trial_balance_balanced": s["trial_balance"]["balanced"],
               "locked_through": locked_through, "log": log,
               "artifacts": list(artifacts.keys())}

    # write the package
    if out_dir:
        tag = period or as_of or "latest"
        d = Path(out_dir) / f"{book}-{tag}"
        d.mkdir(parents=True, exist_ok=True)
        for name, content in artifacts.items():
            (d / name).write_text(content)
        (d / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
        summary["package_dir"] = str(d)
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-close-run",
                                 description="Run the period close non-interactively (cron-safe).")
    ap.add_argument("--book", required=True)
    ap.add_argument("--period", default=None, help="reporting month YYYY-MM (adds comparative + locks month-end)")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--out", default=None, help="write the close package to this directory")
    ap.add_argument("--lock", action="store_true", help="lock the period if the gate passes")
    ap.add_argument("--entity", default="the Company")
    ap.add_argument("--ingest", default=None, help="rebuild from new statements (dir or file) before closing")
    ap.add_argument("--post-subledgers", action="store_true", help="auto-post registered subledger entries for the period")
    ap.add_argument("--chart", default=None)
    ap.add_argument("--map", dest="mapfile", default=None)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    res = run_close(a.book, period=a.period, as_of=a.as_of, out_dir=a.out, lock=a.lock,
                    entity=a.entity, ingest=a.ingest, chart=a.chart, mapfile=a.mapfile,
                    post_subledgers=a.post_subledgers)
    if a.format == "json":
        print(json.dumps(res, indent=2, default=str))
    else:
        print("=" * 56)
        print(f"SCHEDULED CLOSE — {res['book']}" + (f"  {res['period']}" if res['period'] else ""))
        print("-" * 56)
        for line in res["log"]:
            print(f"  {line}")
        print(f"  net income: {res['net_income']}   TB balanced: {res['trial_balance_balanced']}")
        if res.get("package_dir"):
            print(f"  package: {res['package_dir']}")
        print("-" * 56)
        print("  ✅ CLOSE PASSED" if res["gate_passed"] else "  ❌ CLOSE FAILED — books not bulletproof")
        print("=" * 56)
    return 0 if res["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
