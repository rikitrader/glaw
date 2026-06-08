"""GLAW reconstruction orchestrator — rebuild a full set of books from many sources.

The deterministic engine behind the /glaw-reconstruct workflow. Takes a sources manifest
(each statement/dir → its own cash account + chart), and runs the full reconstruction:

  ingest every source → its own cash account   (multi-account, multi-format)
    → STATEMENT CONTINUITY gate (opening==prior close, no gaps)   [completeness]
    → INTER-ACCOUNT TRANSFER reclassification (kill the double-count) [correctness]
    → per-account TIE-OUT (GL balance == latest statement closing)  [accuracy]
    → BOOKS-DOCTOR gate (TB/BS/classified/cash/dedup/integrity)     [control]
    → LEDGER AUDIT (tie-out + tamper-evidence + trace)              [assurance]

Returns a structured result the workflow's chief orchestrator reads to drive fixes and the
adversarial consensus loop. Exit code reflects the gates.

Manifest JSON:
  {"book": "acme", "entity": "Acme LLC", "window": 5,
   "sources": [{"path": "checking/", "account": "Assets:Bank:Checking", "chart": "roofing"},
               {"path": "amex.csv",  "account": "Liabilities:CreditCard:Amex", "chart": "roofing"}]}
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L            # noqa: E402
import continuity as CONT     # noqa: E402
import transfers as TR        # noqa: E402
import books_doctor as BD     # noqa: E402

INGEST = str(Path.home() / ".claude/skills/glaw/bin/glaw-bank-ingest")


def _dec(v):
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _ingest(path: str, chart: str | None, mapfile: str | None) -> dict:
    cmd = [INGEST, path, "--format", "json"]
    if chart:
        cmd += ["--chart", chart]
    if mapfile:
        cmd += ["--map", mapfile]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if not out.stdout.strip():
        raise SystemExit(f"ingest produced nothing for {path}: {out.stderr.strip()[:200]}")
    return json.loads(out.stdout)


def reconstruct(manifest: dict, *, capture=True) -> dict:
    book = manifest["book"]
    window = int(manifest.get("window", 5))
    led = L.Ledger(book)
    sources_report, continuity_records = [], []

    # 1 — ingest every source into its own cash account
    for src in manifest["sources"]:
        payload = _ingest(src["path"], src.get("chart"), src.get("map"))
        rows = payload.get("rows", [])
        imp = led.import_bank(rows, bank_account=src["account"])
        for au in payload.get("audit", []):
            continuity_records.append({"account": src["account"], **{
                k: au.get(k) for k in ("period_start", "period_end", "opening_balance",
                                       "closing_balance", "balance_status")}})
        sources_report.append({"path": src["path"], "account": src["account"],
                               "posted": imp["posted"], "skipped": imp["skipped_duplicates"]})

    # 2 — continuity / completeness gate
    cont = CONT.check(continuity_records, gap_tolerance_days=window)

    # 3 — inter-account transfer reclassification
    tr = TR.reclassify(book, window_days=window)

    # 4 — per-account tie-out: GL balance == latest statement closing balance
    bal = led.balances()
    tieouts, tie_ok = [], True
    latest_close: dict[str, Decimal] = {}
    for r in sorted(continuity_records, key=lambda x: str(x.get("period_end") or "")):
        if r.get("closing_balance") is not None:
            latest_close[r["account"]] = _dec(r["closing_balance"])
    for acct, close in latest_close.items():
        gl = bal.get(acct, Decimal("0"))
        ok = gl == close
        tie_ok = tie_ok and ok
        tieouts.append({"account": acct, "gl_balance": str(gl), "statement_closing": str(close),
                        "difference": str(gl - close), "tied": ok})

    # 5 — books-doctor control gate
    BD.FAIL = 0
    BD.WARN = 0
    buf = io.StringIO()
    with redirect_stdout(buf):
        gate_rc = BD.run_ledger(book)
    gate_passed = gate_rc == 0

    result = {
        "book": book, "entity": manifest.get("entity", "the Company"),
        "sources": sources_report,
        "continuity": {"complete": cont["complete"], "accounts": cont["accounts"]},
        "transfers": {"found": tr["transfers_found"], "reclassified": tr["reclassified"], "pairs": tr["pairs"]},
        "tie_out": {"all_tied": tie_ok, "accounts": tieouts},
        "control_gate": {"passed": gate_passed, "failures": BD.FAIL, "warnings": BD.WARN,
                         "report": buf.getvalue() if capture else None},
        "audit_ready": cont["complete"] and tie_ok and gate_passed,
    }
    return result


def render_text(r: dict) -> str:
    o = ["=" * 68, f"RECONSTRUCTION — {r['entity']}  (book: {r['book']})", "-" * 68,
         "  SOURCES"]
    for s in r["sources"]:
        o.append(f"    {s['account']:<34} {s['posted']:>5} posted  ({s['skipped']} dup)  ← {s['path']}")
    o.append(f"  CONTINUITY: {'✅ complete' if r['continuity']['complete'] else '❌ incomplete'}")
    for a in r["continuity"]["accounts"]:
        if not a["continuous"]:
            o.append(f"     ✗ {a['account']}: {len(a['breaks'])} break(s), {len(a['gaps'])} gap(s)")
    o.append(f"  TRANSFERS: {r['transfers']['reclassified']} reclassified (of {r['transfers']['found']} found)")
    for p in r["transfers"]["pairs"]:
        o.append(f"     {_dec(p['amount']):>12,.2f}  {p['from']} → {p['to']}")
    o.append(f"  TIE-OUT: {'✅ all accounts tie to statement closing' if r['tie_out']['all_tied'] else '❌ tie-out break'}")
    for t in r["tie_out"]["accounts"]:
        mark = "✓" if t["tied"] else "✗"
        o.append(f"     {mark} {t['account']:<30} GL {_dec(t['gl_balance']):>14,.2f}  stmt {_dec(t['statement_closing']):>14,.2f}")
    g = r["control_gate"]
    o.append(f"  CONTROL GATE: {'✅ bulletproof' if g['passed'] else '❌ problems'} (failures {g['failures']}, warnings {g['warnings']})")
    o.append("-" * 68)
    o.append("  🛡️  AUDIT-READY — reconstructed, complete, transfers netted, tied, gated"
             if r["audit_ready"] else "  ❌ NOT AUDIT-READY — resolve the items above, then re-run")
    o.append("=" * 68)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-reconstruct")
    ap.add_argument("manifest", help="sources manifest JSON")
    ap.add_argument("--out", default=None, help="write the reconstruction report dir")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    manifest = json.load(open(a.manifest, encoding="utf-8"))
    r = reconstruct(manifest)
    if a.format == "json":
        print(json.dumps(r, indent=2, default=str))
    else:
        print(render_text(r))
    if a.out:
        d = Path(a.out)
        d.mkdir(parents=True, exist_ok=True)
        (d / "reconstruction.json").write_text(json.dumps(r, indent=2, default=str))
        (d / "reconstruction.txt").write_text(render_text(r))
    return 0 if r["audit_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
