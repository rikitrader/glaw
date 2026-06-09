#!/usr/bin/env python3
"""GLAW Form 990 family — annual-return gating (990-N / 990-EZ / 990 / 990-PF), the 990-T
unrelated-business-income-tax (UBIT) computation, and the public-support-test screen.

Gating (annual information return):
  * Private foundation (any size)        → Form 990-PF.
  * Gross receipts normally ≤ $50,000     → Form 990-N (e-Postcard).
  * Gross receipts < $200,000 AND total assets < $500,000 → Form 990-EZ (optional full 990).
  * Otherwise                             → full Form 990.
UBIT (Form 990-T, §511–513): net unrelated business taxable income = gross UBI − directly
connected deductions − the $1,000 specific deduction (§512(b)(12)); tax at 21% for
corporate-form exempt orgs (trust-form uses trust rates — FLAGGED). Each unrelated trade or
business is silo'd under §512(a)(6) (no cross-activity loss offset) — this engine takes the
already-silo'd net; do the per-silo split upstream.
Public-support test (§509(a)(1)/170(b)(1)(A)(vi) one-third support): public support ÷ total
support ≥ 33⅓% keeps public-charity status (10%-facts-and-circumstances fallback FLAGGED).

[VERIFY] Thresholds ($50k/$200k/$500k, $1,000 specific deduction) and the 21% rate are current
but confirm against the filing-year 990/990-T instructions. DRAFT for a CPA to sign.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
UBIT_RATE = Decimal("0.21")                  # [VERIFY] corporate-form exempt org
SPECIFIC_DEDUCTION = Decimal("1000")         # §512(b)(12)


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def gate_return(*, gross_receipts, total_assets, is_private_foundation) -> str:
    if is_private_foundation:
        return "990-PF"
    gr, ta = _dec(gross_receipts), _dec(total_assets)
    if gr <= Decimal("50000"):
        return "990-N (e-Postcard)"
    if gr < Decimal("200000") and ta < Decimal("500000"):
        return "990-EZ"
    return "990 (full)"


def ubit(*, gross_ubi, directly_connected_deductions, entity_form="corporation") -> dict:
    net = _dec(gross_ubi) - _dec(directly_connected_deductions) - SPECIFIC_DEDUCTION
    net = max(Decimal("0"), net)
    rate_note = "21% corporate rate" if entity_form == "corporation" else "trust rate [VERIFY — use §1(e) trust brackets]"
    tax = net * UBIT_RATE if entity_form == "corporation" else net * UBIT_RATE  # trust rate flagged, not modeled
    return {"net_ubti": str(_q(net)), "ubit_tax": str(_q(tax)), "ubit_rate_basis": rate_note}


def public_support_pct(*, public_support, total_support) -> dict:
    tot = _dec(total_support)
    pct = (Decimal("0") if tot == 0 else (_dec(public_support) / tot * Decimal("100")))
    status = ("public charity (≥33⅓%)" if pct >= Decimal("33.3333")
              else "10%-facts-&-circumstances FALLBACK or tipping toward PF [FLAG]")
    return {"public_support_pct": str(pct.quantize(Decimal("0.01"))), "support_status": status}


def form_990(*, gross_receipts="0", total_assets="0", is_private_foundation=False,
             gross_ubi="0", directly_connected_deductions="0", entity_form="corporation",
             public_support="0", total_support="0", year="2025") -> dict:
    out = {
        "filing_year": str(year),
        "required_annual_return": gate_return(gross_receipts=gross_receipts, total_assets=total_assets,
                                              is_private_foundation=is_private_foundation),
        "gross_receipts": str(_q(_dec(gross_receipts))),
        "total_assets": str(_q(_dec(total_assets))),
    }
    if _dec(gross_ubi) > 0:
        out["ubit"] = ubit(gross_ubi=gross_ubi, directly_connected_deductions=directly_connected_deductions,
                           entity_form=entity_form)
    if _dec(total_support) > 0:
        out["public_support_test"] = public_support_pct(public_support=public_support, total_support=total_support)
    out["_verify"] = ("gating thresholds + UBIT rate are year-sensitive; §512(a)(6) silos UBI per trade/business "
                      "(no cross-offset) — split upstream; 1023/1024 exemption application is a separate filing.")
    return out


def render_text(d: dict) -> str:
    lines = ["=" * 60, f"FORM 990 FAMILY — DRAFT — filing year {d['filing_year']}", "-" * 60,
             f"  gross receipts                  {_dec(d['gross_receipts']):>16,.2f}",
             f"  total assets                    {_dec(d['total_assets']):>16,.2f}",
             f"  ► REQUIRED ANNUAL RETURN: {d['required_annual_return']}"]
    if "ubit" in d:
        u = d["ubit"]
        lines += ["-" * 60, "  990-T UBIT:",
                  f"    net UBTI                      {_dec(u['net_ubti']):>16,.2f}",
                  f"    UBIT tax ({u['ubit_rate_basis']})",
                  f"    UBIT tax                      {_dec(u['ubit_tax']):>16,.2f}"]
    if "public_support_test" in d:
        p = d["public_support_test"]
        lines += ["-" * 60, f"  public support: {p['public_support_pct']}% → {p['support_status']}"]
    lines += ["=" * 60, f"  ⚠ VERIFY: {d['_verify']}"]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-form990", description="Form 990 family DRAFT: gating + 990-T UBIT + support test.")
    for f in ("gross-receipts", "total-assets", "gross-ubi", "directly-connected-deductions",
              "public-support", "total-support"):
        ap.add_argument(f"--{f}", default="0")
    ap.add_argument("--private-foundation", action="store_true", help="force 990-PF gating")
    ap.add_argument("--entity-form", default="corporation", choices=["corporation", "trust"])
    ap.add_argument("--year", default="2025")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = form_990(gross_receipts=a.gross_receipts, total_assets=a.total_assets,
                 is_private_foundation=a.private_foundation, gross_ubi=a.gross_ubi,
                 directly_connected_deductions=a.directly_connected_deductions,
                 entity_form=a.entity_form, public_support=a.public_support,
                 total_support=a.total_support, year=a.year)
    print(json.dumps(d, indent=2) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
