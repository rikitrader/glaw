#!/usr/bin/env python3
"""
409A Valuation Engine — self-contained, stdlib-only.

Transparent, explainable, auditable. Every module records its inputs, the
formula applied, and its result into an audit trail so any number can be traced.

Usage:
    python3 valuation_engine.py audit      --intake intake.json
    python3 valuation_engine.py value      --intake intake.json [--out outdir]
    python3 valuation_engine.py compliance --intake intake.json
    python3 valuation_engine.py validate   --intake intake.json
    python3 valuation_engine.py all        --intake intake.json [--out outdir]

`all` runs audit -> value -> compliance and writes audit_log.json + results.json.

NOT tax/legal/appraisal advice. A 409A safe harbor requires an independent
qualified appraiser. This produces a rigorous draft valuation + audit trail.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date, datetime

VERSION = "1.0.0"


# --------------------------------------------------------------------------- #
# Audit trail                                                                  #
# --------------------------------------------------------------------------- #
class Audit:
    """Accumulates a reproducible record of every step."""

    def __init__(self):
        self.entries = []
        self.warnings = []

    def record(self, module, formula, inputs, result):
        self.entries.append(
            {
                "module": module,
                "formula": formula,
                "inputs": inputs,
                "result": result,
            }
        )

    def warn(self, msg):
        self.warnings.append(msg)

    def dump(self, valuation_date):
        return {
            "engine_version": VERSION,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "valuation_date": valuation_date,
            "warnings": self.warnings,
            "steps": self.entries,
        }


# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #
def g(d, path, default=None):
    """Safe nested get: g(intake, 'financials.cash', 0)."""
    cur = d
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur if cur is not None else default


def percentile(values, p):
    """Linear-interpolation percentile (no numpy). p in [0,100]."""
    if not values:
        return None
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * (p / 100.0)
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return s[int(k)]
    return s[lo] * (hi - k) + s[hi] * (k - lo)


def mean(values):
    return sum(values) / len(values) if values else None


def money(x):
    return round(x, 2) if x is not None else None


# --------------------------------------------------------------------------- #
# Cap table audit                                                              #
# --------------------------------------------------------------------------- #
def cap_table(intake, audit):
    sh = intake.get("shares", {}) or {}
    common = sh.get("common", 0) or 0
    options = sh.get("option_pool", 0) or 0
    warrants = sh.get("warrants", 0) or 0

    preferred_series = sh.get("preferred", []) or []
    pref_shares = sum((s.get("shares", 0) or 0) for s in preferred_series)

    # SAFEs / notes convert to shares; if share count unknown, flag.
    safe_shares = 0
    for instr in (sh.get("safes", []) or []) + (sh.get("convertible_notes", []) or []):
        s = instr.get("as_converted_shares")
        if s is None:
            audit.warn(
                f"Convertible '{instr.get('name','?')}' has no as_converted_shares; "
                "excluded from fully-diluted count. Conversion will shift the waterfall."
            )
        else:
            safe_shares += s

    fully_diluted = common + options + warrants + pref_shares + safe_shares

    flags = []
    if fully_diluted <= 0:
        flags.append("Fully-diluted share count is zero or undefined.")
    if common <= 0:
        flags.append("No common shares found — common FMV cannot be computed.")
    for s in preferred_series:
        if s.get("liquidation_multiple") is None:
            flags.append(f"Preferred '{s.get('name','?')}' missing liquidation_multiple.")
        if s.get("participating") is None:
            flags.append(f"Preferred '{s.get('name','?')}' missing participating flag.")

    result = {
        "common": common,
        "options": options,
        "warrants": warrants,
        "preferred_shares": pref_shares,
        "convertible_shares": safe_shares,
        "fully_diluted": fully_diluted,
        "flags": flags,
    }
    for f in flags:
        audit.warn("CAP-TABLE: " + f)
    audit.record(
        "cap_table",
        "fully_diluted = common + options + warrants + preferred + convertibles",
        {"common": common, "options": options, "warrants": warrants,
         "preferred": pref_shares, "convertibles": safe_shares},
        result,
    )
    return result


# --------------------------------------------------------------------------- #
# DCF (income approach)                                                         #
# --------------------------------------------------------------------------- #
def dcf(intake, audit):
    fin = intake.get("financials", {}) or {}
    fc = intake.get("forecasts", {}) or {}
    rev = fc.get("revenue") or []
    if not rev:
        audit.warn("DCF: no forecast revenue provided; income approach skipped.")
        return None

    n = len(rev)
    opex_pct = fc.get("opex_pct", 0.7)            # operating expense as % of revenue
    tax_rate = fin.get("tax_rate", 0.21)
    capex = fc.get("capex") or [0] * n
    deprec = fc.get("depreciation") or [0] * n
    nwc = fc.get("working_capital_change") or [0] * n
    r = fc.get("discount_rate", 0.25)
    gterm = fc.get("terminal_growth", 0.03)

    def pad(lst):
        return (lst + [lst[-1] if lst else 0] * n)[:n]

    capex, deprec, nwc = pad(capex), pad(deprec), pad(nwc)

    fcfs, pvs, years = [], [], []
    for i in range(n):
        revenue = rev[i]
        ebit = revenue * (1 - opex_pct) - deprec[i]
        nopat = ebit * (1 - tax_rate)
        fcf = nopat + deprec[i] - capex[i] - nwc[i]
        pv = fcf / ((1 + r) ** (i + 1))
        fcfs.append(money(fcf))
        pvs.append(money(pv))
        years.append({
            "year": i + 1, "revenue": revenue, "ebit": money(ebit),
            "nopat": money(nopat), "fcf": money(fcf), "pv": money(pv),
        })

    # Gordon-growth terminal value off the final-year FCF.
    last_fcf = fcfs[-1]
    if r <= gterm:
        audit.warn("DCF: discount rate <= terminal growth; terminal value invalid, set to 0.")
        tv = 0.0
    else:
        tv = last_fcf * (1 + gterm) / (r - gterm)
    pv_tv = tv / ((1 + r) ** n)

    ev = sum(pvs) + pv_tv
    result = {
        "years": years,
        "terminal_value": money(tv),
        "pv_terminal_value": money(pv_tv),
        "sum_pv_fcf": money(sum(pvs)),
        "enterprise_value": money(ev),
        "discount_rate": r,
        "terminal_growth": gterm,
    }
    audit.record(
        "dcf",
        "FCF=NOPAT+Dep-CapEx-dNWC; PV=FCF/(1+r)^n; TV=FCF_n*(1+g)/(r-g); EV=SUM(PV)+PV(TV)",
        {"discount_rate": r, "terminal_growth": gterm, "tax_rate": tax_rate,
         "opex_pct": opex_pct, "years": n},
        {"enterprise_value": result["enterprise_value"]},
    )
    return result


# --------------------------------------------------------------------------- #
# Market comparables                                                            #
# --------------------------------------------------------------------------- #
def comps(intake, audit):
    comp_in = intake.get("comparables", {}) or {}
    peers = comp_in.get("peers") or []
    if not peers:
        audit.warn("COMPS: no comparable companies provided; market approach skipped.")
        return None

    ev_rev = [p["ev"] / p["revenue"] for p in peers
              if p.get("ev") and p.get("revenue")]
    ev_ebitda = [p["ev"] / p["ebitda"] for p in peers
                 if p.get("ev") and p.get("ebitda") and p["ebitda"] > 0]

    def stats(xs):
        if not xs:
            return None
        return {
            "mean": round(mean(xs), 2),
            "median": round(percentile(xs, 50), 2),
            "q1": round(percentile(xs, 25), 2),
            "q3": round(percentile(xs, 75), 2),
            "low": round(min(xs), 2),
            "high": round(max(xs), 2),
        }

    rev_stats = stats(ev_rev)
    ebitda_stats = stats(ev_ebitda)

    # Apply the recommended (median, conservative) multiple to the subject.
    fc = intake.get("forecasts", {}) or {}
    subj_rev = (fc.get("revenue") or [None])[0] or g(intake, "financials.revenue", [None])[-1]
    subj_ebitda = (fc.get("ebitda") or [None])[0] or g(intake, "financials.ebitda", [None])[-1]

    implied = []
    if rev_stats and subj_rev:
        implied.append(("EV/Revenue", rev_stats["median"], rev_stats["median"] * subj_rev))
    if ebitda_stats and subj_ebitda and subj_ebitda > 0:
        implied.append(("EV/EBITDA", ebitda_stats["median"], ebitda_stats["median"] * subj_ebitda))

    ev = mean([v for _, _, v in implied]) if implied else None
    result = {
        "ev_revenue": rev_stats,
        "ev_ebitda": ebitda_stats,
        "recommended_multiples": [
            {"metric": m, "multiple": mult, "implied_ev": money(val)}
            for m, mult, val in implied
        ],
        "enterprise_value": money(ev),
    }
    audit.record(
        "comps",
        "multiple = median(peer EV/metric); implied_EV = multiple * subject_metric",
        {"n_peers": len(peers), "subject_revenue": subj_rev, "subject_ebitda": subj_ebitda},
        {"enterprise_value": result["enterprise_value"]},
    )
    return result


# --------------------------------------------------------------------------- #
# VC method                                                                     #
# --------------------------------------------------------------------------- #
def vc_method(intake, audit):
    fc = intake.get("forecasts", {}) or {}
    vc = intake.get("vc_method", {}) or {}
    proj_rev = vc.get("exit_year_revenue") or (fc.get("revenue") or [None])[-1]
    if not proj_rev:
        audit.warn("VC: no exit-year revenue; VC method skipped.")
        return None

    exit_multiple = vc.get("exit_multiple", 5.0)
    target_return = vc.get("target_return", 10.0)
    investment = vc.get("investment", 0) or 0

    exit_value = proj_rev * exit_multiple
    post_money = exit_value / target_return
    pre_money = post_money - investment

    result = {
        "exit_year_revenue": proj_rev,
        "exit_multiple": exit_multiple,
        "exit_value": money(exit_value),
        "target_return": target_return,
        "post_money": money(post_money),
        "investment": investment,
        "pre_money": money(pre_money),
    }
    audit.record(
        "vc_method",
        "ExitValue=Rev*Multiple; PostMoney=ExitValue/TargetReturn; PreMoney=PostMoney-Investment",
        {"exit_multiple": exit_multiple, "target_return": target_return,
         "investment": investment},
        {"post_money": result["post_money"], "pre_money": result["pre_money"]},
    )
    return result


# --------------------------------------------------------------------------- #
# PWERM                                                                         #
# --------------------------------------------------------------------------- #
def pwerm(intake, audit):
    scen = intake.get("pwerm", {}).get("scenarios") if intake.get("pwerm") else None
    if not scen:
        audit.warn("PWERM: no scenarios provided; PWERM skipped.")
        return None

    r = g(intake, "forecasts.discount_rate", 0.25)
    total_p = sum(s.get("probability", 0) for s in scen)
    if abs(total_p - 1.0) > 1e-6 and total_p > 0:
        audit.warn(f"PWERM: probabilities sum to {total_p:.3f}; normalized to 1.0.")

    rows, weighted = [], 0.0
    for s in scen:
        p = (s.get("probability", 0) / total_p) if total_p else 0
        ev = s.get("exit_value", 0) or 0
        t = s.get("time_to_exit", 0) or 0
        pv = ev / ((1 + r) ** t) if t else ev
        contrib = p * pv
        weighted += contrib
        rows.append({
            "scenario": s.get("name", "?"), "probability": round(p, 4),
            "exit_value": money(ev), "time_to_exit": t,
            "present_value": money(pv), "weighted_contribution": money(contrib),
        })

    result = {
        "scenarios": rows,
        "discount_rate": r,
        "probability_weighted_equity_value": money(weighted),
    }
    audit.record(
        "pwerm",
        "PV=ExitValue/(1+r)^t; PWERM=SUM(probability * PV)",
        {"discount_rate": r, "n_scenarios": len(scen)},
        {"probability_weighted_equity_value": result["probability_weighted_equity_value"]},
    )
    return result


# --------------------------------------------------------------------------- #
# Priced round basis                                                           #
# --------------------------------------------------------------------------- #
def priced_round_basis(intake, cap, audit):
    """Use the most recent priced round as an observable equity-value anchor.

    A 409A should not mechanically equal the last preferred round, but the round
    is a required cross-check and can be the only valuation basis in a sparse
    early-stage file. Prefer explicit post-money. If absent, infer post-money
    from price per share times fully diluted shares.
    """
    rounds = intake.get("financing_rounds", []) or []
    priced = [r for r in rounds if r.get("post_money") or r.get("price_per_share")]
    if not priced:
        audit.warn("ROUND: no priced financing round with post_money or price_per_share; skipped.")
        return None

    rnd = priced[-1]
    if rnd.get("post_money"):
        equity_value = rnd.get("post_money")
        basis = "post_money"
    else:
        equity_value = rnd.get("price_per_share") * (cap.get("fully_diluted") or 0)
        basis = "price_per_share * fully_diluted_shares"
        if not equity_value:
            audit.warn("ROUND: could not infer post-money because fully-diluted shares are missing.")
            return None

    result = {
        "round": rnd.get("round"),
        "date": rnd.get("date"),
        "basis": basis,
        "price_per_share": rnd.get("price_per_share"),
        "amount": rnd.get("amount"),
        "equity_value": money(equity_value),
    }
    audit.record(
        "priced_round_basis",
        "EquityValue = latest priced round post_money, or price_per_share * fully_diluted_shares",
        {"round": rnd.get("round"), "basis": basis, "fully_diluted": cap.get("fully_diluted")},
        {"equity_value": result["equity_value"]},
    )
    return result


# --------------------------------------------------------------------------- #
# Reconciliation: enterprise -> equity value                                   #
# --------------------------------------------------------------------------- #
def reconcile(intake, dcf_r, comps_r, vc_r, pwerm_r, round_r, audit):
    fin = intake.get("financials", {}) or {}
    cash = fin.get("cash", 0) or 0
    debt = fin.get("debt", 0) or 0
    net_debt = debt - cash

    w = (intake.get("weights") or {})
    parts = []
    if dcf_r:
        parts.append(("dcf", w.get("dcf", 0.4), dcf_r["enterprise_value"]))
    if comps_r and comps_r.get("enterprise_value"):
        parts.append(("comps", w.get("comps", 0.4), comps_r["enterprise_value"]))
    if vc_r:
        # VC produces pre-money equity; convert to an EV-equivalent for blending.
        parts.append(("vc", w.get("vc", 0.2), vc_r["pre_money"] + net_debt))
    if round_r:
        # A priced round is an equity-value anchor. Convert to EV-equivalent for blending.
        parts.append(("round", w.get("round", 0.2), round_r["equity_value"] + net_debt))

    if not parts:
        audit.warn("RECONCILE: no approach produced a value.")
        return None

    wsum = sum(p[1] for p in parts)
    blended_ev = sum((p[1] / wsum) * p[2] for p in parts) if wsum else mean([p[2] for p in parts])
    equity_value = blended_ev - net_debt

    floor = (fin.get("cash", 0) or 0) - (fin.get("debt", 0) or 0)
    if equity_value < 0:
        audit.warn(f"RECONCILE: equity value negative ({money(equity_value)}); "
                   f"using asset floor {money(max(floor,0))}.")
        equity_value = max(floor, 0.0)

    # Divergence check vs PWERM
    divergence = None
    if pwerm_r and pwerm_r["probability_weighted_equity_value"]:
        pw = pwerm_r["probability_weighted_equity_value"]
        if equity_value:
            divergence = round(abs(equity_value - pw) / equity_value, 3)
            if divergence > 0.40:
                audit.warn(f"RECONCILE: reconciled vs PWERM diverge {divergence*100:.0f}% (>40%).")

    result = {
        "weights_used": {p[0]: round(p[1] / wsum, 3) for p in parts} if wsum else {},
        "approach_evs": {p[0]: p[2] for p in parts},
        "net_debt": money(net_debt),
        "blended_enterprise_value": money(blended_ev),
        "equity_value": money(equity_value),
        "pwerm_divergence": divergence,
    }
    audit.record(
        "reconcile",
        "EV=weighted_avg(approaches); EquityValue=EV-NetDebt; NetDebt=Debt-Cash",
        {"net_debt": money(net_debt), "weights": result["weights_used"]},
        {"equity_value": result["equity_value"]},
    )
    return result


# --------------------------------------------------------------------------- #
# Waterfall allocation                                                          #
# --------------------------------------------------------------------------- #
def waterfall(intake, equity_value, cap, audit):
    """Single-exit liquidation waterfall WITH the conversion test.

    Non-participating preferred convert to common when their as-converted value
    beats their preference. Because each conversion changes the common per-share
    that drives the others, the decision is iterated to a fixed point. Participating
    preferred take preference + pro-rata participation, capped where a
    participation_cap is set (capped excess redistributes to common).
    """
    sh = intake.get("shares", {}) or {}
    preferred = sh.get("preferred", []) or []
    common_shares = cap["common"] + cap["options"] + cap["warrants"]
    fd = cap["fully_diluted"]
    series = sorted(preferred, key=lambda s: s.get("seniority", 0), reverse=True)

    def pref_of(s):
        return (s.get("invested", 0) or 0) * (s.get("liquidation_multiple", 1.0) or 1.0)

    non_part = [s for s in series if not s.get("participating")]
    part = [s for s in series if s.get("participating")]
    name_of = lambda s: s.get("name", "?")
    shares_of = lambda s: s.get("shares", 0) or 0

    converting = set()  # names of non-participating series that convert to common

    def allocate(conv):
        """Run the stack for a given conversion set; return common per-share + pref payouts."""
        remaining = equity_value
        pref_paid = {}
        for s in series:                       # 1. liq prefs, senior->junior, non-converting only
            if name_of(s) in conv:
                continue                        # converted -> waives preference, joins common
            paid = min(pref_of(s), max(remaining, 0))
            remaining -= paid
            pref_paid[name_of(s)] = paid
        residual = max(remaining, 0)
        pool = common_shares + sum(shares_of(s) for s in part) \
            + sum(shares_of(s) for s in non_part if name_of(s) in conv)
        per_share = residual / pool if pool else 0.0
        return per_share, pref_paid, residual

    for _ in range(len(non_part) + 2):         # 2. iterate conversion to a fixed point
        per_share, _, _ = allocate(converting)
        changed = False
        for s in non_part:
            as_conv, pref = shares_of(s) * per_share, pref_of(s)
            if name_of(s) not in converting and as_conv > pref:
                converting.add(name_of(s)); changed = True
            elif name_of(s) in converting and as_conv < pref:
                converting.discard(name_of(s)); changed = True
        if not changed:
            break

    per_share, pref_paid_map, residual = allocate(converting)

    rows, pref_paid_total = [], 0.0
    for s in series:
        if name_of(s) in converting:
            rows.append({"series": name_of(s), "type": "converted_to_common",
                         "shares": shares_of(s), "paid": money(shares_of(s) * per_share)})
        else:
            paid = pref_paid_map.get(name_of(s), 0.0)
            pref_paid_total += paid
            rows.append({"series": name_of(s), "type": "liquidation_pref",
                         "claim": money(pref_of(s)), "paid": money(paid),
                         "participating": bool(s.get("participating"))})

    part_paid, capped_excess = 0.0, 0.0        # 3. participation (capped; excess -> common)
    for s in part:
        gross = shares_of(s) * per_share
        cap_mult = s.get("participation_cap")
        if cap_mult:
            total_cap = (s.get("invested", 0) or 0) * cap_mult
            already = pref_paid_map.get(name_of(s), 0.0)
            capped = min(gross, max(total_cap - already, 0))
            capped_excess += gross - capped
            gross = capped
        part_paid += gross
        rows.append({"series": name_of(s), "type": "participation", "paid": money(gross)})

    converted_paid = sum(shares_of(s) * per_share
                         for s in non_part if name_of(s) in converting)
    common_paid = common_shares * per_share + capped_excess
    rows.append({"series": "Common (+options/warrants)", "type": "residual_common",
                 "shares": common_shares, "paid": money(common_paid),
                 "per_share": money(per_share)})

    result = {
        "equity_value": money(equity_value),
        "preferred_preferences_paid": money(pref_paid_total),
        "participation_paid": money(part_paid),
        "converted_to_common": [name_of(s) for s in non_part if name_of(s) in converting],
        "value_to_converted_preferred": money(converted_paid),
        "value_to_common": money(common_paid),
        "common_per_share": money(per_share),
        "common_shares": common_shares,
        "fully_diluted": fd,
        "rows": rows,
    }
    audit.record(
        "waterfall",
        "senior->junior prefs; non-participating preferred convert when as-converted>preference "
        "(fixed-point); participation capped, excess to common",
        {"equity_value": money(equity_value), "converted": result["converted_to_common"]},
        {"value_to_common": result["value_to_common"]},
    )
    return result


# --------------------------------------------------------------------------- #
# Common FMV                                                                    #
# --------------------------------------------------------------------------- #
def common_fmv(equity_value, wf, audit):
    # Value to common already nets out preferences, participation, and any
    # preferred that converted to common in the waterfall.
    common_equity = wf["value_to_common"]
    fd_common = wf["common_shares"]
    fmv = common_equity / fd_common if fd_common else 0
    result = {
        "common_equity_value": money(common_equity),
        "fully_diluted_common": fd_common,
        "fmv_marketable": money(fmv),
    }
    audit.record(
        "common_fmv",
        "CommonEquity=Waterfall value_to_common; FMV=CommonEquity/FDCommon",
        {"value_to_common": money(common_equity), "fd_common": fd_common},
        {"fmv_marketable": result["fmv_marketable"]},
    )
    return result


# --------------------------------------------------------------------------- #
# DLOM                                                                          #
# --------------------------------------------------------------------------- #
def dlom(intake, audit):
    profile = intake.get("dlom_profile", {}) or {}
    # Score 0..1 toward higher discount.
    score = 0.0
    stage = (profile.get("stage") or "early").lower()
    stage_map = {"late": 0.0, "growth": 0.4, "early": 0.8, "seed": 1.0, "pre-seed": 1.0}
    score += 0.35 * stage_map.get(stage, 0.8)

    revenue = profile.get("annual_revenue", 0) or 0
    score += 0.20 * (0.0 if revenue > 50e6 else 0.5 if revenue > 5e6 else 1.0)

    funded = profile.get("recently_funded", False)
    score += 0.15 * (0.0 if funded else 1.0)

    horizon = profile.get("liquidity_horizon_years", 4)
    score += 0.15 * (0.0 if horizon <= 1 else 0.5 if horizon <= 3 else 1.0)

    exit_prob = profile.get("exit_probability", 0.5)
    score += 0.15 * (1.0 - max(0.0, min(1.0, exit_prob)))

    # Map score (0..1) onto the 10%..35% band.
    pct = 0.10 + score * (0.35 - 0.10)
    # Snap to nearest 5% step for a defensible round figure.
    band = round(pct / 0.05) * 0.05
    band = max(0.10, min(0.35, band))

    result = {"score": round(score, 3), "raw_dlom": round(pct, 4), "recommended_dlom": round(band, 2)}
    audit.record(
        "dlom",
        "weighted score of stage/revenue/funding/horizon/exit -> map to 10-35% band",
        {"stage": stage, "revenue": revenue, "funded": funded,
         "horizon": horizon, "exit_probability": exit_prob},
        {"recommended_dlom": result["recommended_dlom"]},
    )
    return result


# --------------------------------------------------------------------------- #
# OPM (Option Pricing Method) — Black-Scholes allocation + backsolve            #
# --------------------------------------------------------------------------- #
def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def bs_call(S, K, T, r, sigma):
    """Black-Scholes European call — the optionality the single-point waterfall ignores."""
    if K <= 0:
        return S
    if S <= 0 or T <= 0 or sigma <= 0:
        return max(S - K, 0.0)
    d1 = (math.log(S / K) + (r + sigma * sigma / 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)


def _opm_params(intake, sigma, years, rate):
    o = intake.get("opm", {}) or {}
    return (
        sigma if sigma is not None else o.get("sigma", 0.60),
        years if years is not None else o.get("years", 4.0),
        rate if rate is not None else o.get("rate", 0.04),
    )


def opm(intake, equity_value, cap, audit, dlom_pct=0.0, sigma=None, years=None, rate=None):
    """Single-breakpoint early-stage OPM: common is a call struck at the aggregate
    liquidation preference, allocated pro-rata over fully-diluted shares. Treats
    volatility/time-to-liquidity explicitly (the waterfall's blind spot). A
    qualified appraiser refines breakpoints for the full stack."""
    sh = intake.get("shares", {}) or {}
    preferred = sh.get("preferred", []) or []
    L = sum((s.get("invested", 0) or 0) * (s.get("liquidation_multiple", 1.0) or 1.0)
            for s in preferred)
    fd = cap["fully_diluted"]
    common_shares = cap["common"] + cap["options"] + cap["warrants"]
    sigma, years, rate = _opm_params(intake, sigma, years, rate)

    upside = bs_call(equity_value, L, years, rate, sigma)        # common call above pref
    pref_value = equity_value - upside
    common_value = upside * (common_shares / fd) if fd else 0
    fmv_marketable = common_value / common_shares if common_shares else 0
    fmv_409a = fmv_marketable * (1 - dlom_pct)

    result = {
        "aggregate_liquidation_pref": money(L),
        "sigma": sigma, "years": years, "rate": rate,
        "preferred_value": money(pref_value),
        "common_upside_call": money(upside),
        "common_value": money(common_value),
        "fmv_marketable": money(fmv_marketable),
        "dlom": dlom_pct,
        "fmv_409a": money(fmv_409a),
    }
    audit.record(
        "opm",
        "common = BS_call(E, aggregate_pref, T, r, sigma) * common/FD; FMV409A = FMV*(1-DLOM)",
        {"equity": money(equity_value), "L": money(L), "sigma": sigma, "years": years, "rate": rate},
        {"fmv_marketable": result["fmv_marketable"], "fmv_409a": result["fmv_409a"]},
    )
    return result


def opm_backsolve(intake, cap, audit, sigma=None, years=None, rate=None):
    """Backsolve total equity value from the most recent priced round: find E such
    that the OPM value allocated to that series equals the amount invested. Bisection."""
    rounds = intake.get("financing_rounds", []) or []
    priced = [r for r in rounds if r.get("price_per_share") and r.get("amount")]
    if not priced:
        audit.warn("BACKSOLVE: no priced financing round; skipped.")
        return None
    rnd = priced[-1]                                            # most recent priced round
    sh = intake.get("shares", {}) or {}
    preferred = sh.get("preferred", []) or []
    L = sum((s.get("invested", 0) or 0) * (s.get("liquidation_multiple", 1.0) or 1.0)
            for s in preferred)
    fd = cap["fully_diluted"]
    sigma, years, rate = _opm_params(intake, sigma, years, rate)

    # Match the round to its series (by name) to get that series' shares + pref.
    target_name = rnd.get("round")
    series = next((s for s in preferred if s.get("name") == target_name), None)
    if not series:
        series = preferred[-1] if preferred else None
    if not series:
        audit.warn("BACKSOLVE: no preferred series to match the round; skipped.")
        return None
    s_shares = series.get("shares", 0) or 0
    s_pref = (series.get("invested", 0) or 0) * (series.get("liquidation_multiple", 1.0) or 1.0)
    invested = rnd.get("amount")

    def series_value(E):
        upside = bs_call(E, L, years, rate, sigma)
        pref_value = E - upside
        pref_share = (s_pref / L) if L else 0
        return pref_value * pref_share + upside * (s_shares / fd if fd else 0)

    lo, hi = 1.0, max(invested * 1000, 1e9)                     # bisection bracket
    for _ in range(200):
        mid = (lo + hi) / 2
        if series_value(mid) < invested:
            lo = mid
        else:
            hi = mid
    E = (lo + hi) / 2
    result = {
        "round": target_name, "invested": invested,
        "matched_series": series.get("name"),
        "backsolved_equity_value": money(E),
        "implied_post_money": rnd.get("post_money"),
    }
    audit.record(
        "opm_backsolve",
        "solve E so OPM value to the priced series == amount invested (bisection)",
        {"round": target_name, "invested": invested, "sigma": sigma, "years": years},
        {"backsolved_equity_value": result["backsolved_equity_value"]},
    )
    return result


# --------------------------------------------------------------------------- #
# Strike price                                                                  #
# --------------------------------------------------------------------------- #
def strike(fmv_marketable, dlom_pct, audit):
    sp = fmv_marketable * (1 - dlom_pct)
    result = {
        "fmv_marketable": money(fmv_marketable),
        "dlom": dlom_pct,
        "strike_price": money(sp),
    }
    audit.record(
        "strike",
        "StrikePrice = FMV_marketable * (1 - DLOM)",
        {"fmv": money(fmv_marketable), "dlom": dlom_pct},
        {"strike_price": result["strike_price"]},
    )
    return result


# --------------------------------------------------------------------------- #
# Sensitivity analysis                                                         #
# --------------------------------------------------------------------------- #
def sensitivity_analysis(fmv_marketable, dlom_pct, audit):
    """Show how the recommended strike moves under common reviewer stresses."""
    equity_cases = [("downside", 0.85), ("base", 1.00), ("upside", 1.15)]
    dlom_cases = [
        ("low_dlom", max(0.0, dlom_pct - 0.05)),
        ("base_dlom", dlom_pct),
        ("high_dlom", min(0.50, dlom_pct + 0.05)),
    ]
    rows = []
    for ev_name, ev_factor in equity_cases:
        stressed_fmv = fmv_marketable * ev_factor
        for dl_name, stressed_dlom in dlom_cases:
            rows.append({
                "equity_case": ev_name,
                "equity_factor": ev_factor,
                "dlom_case": dl_name,
                "dlom": round(stressed_dlom, 4),
                "marketable_fmv": money(stressed_fmv),
                "strike": money(stressed_fmv * (1 - stressed_dlom)),
            })
    audit.record(
        "sensitivity",
        "strike = stressed_marketable_FMV * (1 - stressed_DLOM), across +/-15% equity and +/-5% DLOM",
        {"base_fmv": money(fmv_marketable), "base_dlom": dlom_pct},
        {"n_cases": len(rows)},
    )
    return {"base_fmv": money(fmv_marketable), "base_dlom": dlom_pct, "rows": rows}


# --------------------------------------------------------------------------- #
# Compliance                                                                    #
# --------------------------------------------------------------------------- #
def compliance(intake, audit):
    triggers = []
    val_date = g(intake, "entity.valuation_date") or g(intake, "valuation_date")
    last_val = g(intake, "compliance.last_valuation_date")
    if last_val:
        try:
            d0 = datetime.fromisoformat(last_val).date()
            ref = datetime.fromisoformat(val_date).date() if val_date else date.today()
            months = (ref.year - d0.year) * 12 + (ref.month - d0.month)
            if months >= 12:
                triggers.append(f"Prior 409A is {months} months old (>12).")
        except ValueError:
            audit.warn("COMPLIANCE: could not parse last_valuation_date.")

    ev = intake.get("material_events", {}) or {}
    checks = {
        "new_financing": "New financing round closed.",
        "ma_activity": "M&A activity / acquisition offer.",
        "material_contracts": "Material new contracts signed.",
        "major_revenue_change": "Major change in revenue trajectory.",
        "debt_restructuring": "Debt restructuring occurred.",
    }
    for key, msg in checks.items():
        if ev.get(key):
            triggers.append(msg)

    status = "REVALUATION REQUIRED" if triggers else "VALID"
    result = {"status": status, "triggers": triggers}
    audit.record(
        "compliance",
        "flag if >12 months OR new financing/M&A/material contract/revenue change/debt restructuring",
        {"last_valuation_date": last_val, "events": ev},
        {"status": status},
    )
    return result


# --------------------------------------------------------------------------- #
# Legal / appraiser audit gate                                                  #
# --------------------------------------------------------------------------- #
def legal_audit(intake, audit):
    """Reviewer-control checklist for counsel, auditor, board, and appraiser."""
    review = intake.get("review_controls", {}) or {}
    checks = [
        ("appraiser_engaged", "Qualified independent appraiser engaged or assigned."),
        ("valuation_method_reasonable", "Reasonable valuation method documented for private-company FMV."),
        ("valuation_freshness_confirmed", "Valuation is within 12 months and refreshed for material information."),
        ("cap_table_source_attached", "Source cap table / charter / financing docs attached."),
        ("board_approval_planned", "Board approval process and grant timing documented."),
        ("option_grant_dates_confirmed", "Option grant dates confirmed after valuation date."),
        ("option_exercise_price_fmv_on_grant_date", "Option exercise price is no less than FMV on grant date."),
        ("average_price_period_controls", "Average-price grants, if any, satisfy 30-day recipient/share/irrevocability controls or are marked N/A."),
        ("option_modification_reviewed", "Option repricing, term extension, transfer, and deferred-gain features reviewed."),
        ("dividend_equivalent_rights_reviewed", "Dividend-equivalent rights on options reviewed for exercise-price reduction risk."),
        ("rsu_documents_reviewed", "RSU plan, award, employment, severance, and change-in-control documents reviewed."),
        ("rsu_short_term_deferral_checked", "RSU short-term deferral structure and retirement/good-reason/non-compete vesting reviewed."),
        ("rsu_payment_schedule_409a_compliant", "RSU payment timing, event definitions, and six-month specified-employee delay reviewed."),
        ("release_timing_reviewed", "Release-condition timing reviewed so employee cannot control payment year."),
        ("material_events_reviewed", "Material events reviewed through issuance date."),
        ("legal_counsel_review_required", "Licensed counsel review required before reliance."),
        ("auditor_review_required", "ASC 718/820 auditor review considered where financial statements require it."),
    ]
    missing = [label for key, label in checks if not review.get(key)]
    status = "READY FOR APPRAISER/COUNSEL REVIEW" if not missing else "REVIEW ITEMS OPEN"
    result = {
        "status": status,
        "missing_controls": missing,
        "controls": {key: bool(review.get(key)) for key, _ in checks},
    }
    if missing:
        audit.warn("LEGAL-AUDIT: open controls before reliance: " + "; ".join(missing))
    audit.record(
        "legal_audit",
        "review_controls must evidence Skadden/Practical Law 409A award pitfalls plus appraiser, cap-table, board, material-event, counsel, and auditor gates",
        result["controls"],
        {"status": status, "open_items": len(missing)},
    )
    return result


# --------------------------------------------------------------------------- #
# Orchestration                                                                 #
# --------------------------------------------------------------------------- #
def run_value(intake, audit):
    cap = cap_table(intake, audit)
    dcf_r = dcf(intake, audit)
    comps_r = comps(intake, audit)
    vc_r = vc_method(intake, audit)
    pwerm_r = pwerm(intake, audit)
    round_r = priced_round_basis(intake, cap, audit)
    rec = reconcile(intake, dcf_r, comps_r, vc_r, pwerm_r, round_r, audit)

    out = {
        "cap_table": cap, "dcf": dcf_r, "comps": comps_r,
        "vc_method": vc_r, "pwerm": pwerm_r, "priced_round": round_r,
        "reconciliation": rec,
    }
    if not rec:
        return out

    eq = rec["equity_value"]
    wf = waterfall(intake, eq, cap, audit)
    fmv = common_fmv(eq, wf, audit)
    dl = dlom(intake, audit)
    sp = strike(fmv["fmv_marketable"], dl["recommended_dlom"], audit)
    sens = sensitivity_analysis(fmv["fmv_marketable"], dl["recommended_dlom"], audit)
    legal = legal_audit(intake, audit)

    # OPM cross-check: an option-pricing allocation of the SAME equity value, and a
    # backsolve from the last priced round. Divergence between the waterfall FMV and
    # the OPM FMV is itself a RED finding to reconcile (Step 4 of the orchestrator).
    opm_r = opm(intake, eq, cap, audit, dlom_pct=dl["recommended_dlom"])
    backsolve_r = opm_backsolve(intake, cap, audit)
    if opm_r and fmv["fmv_marketable"]:
        gap = abs(opm_r["fmv_marketable"] - fmv["fmv_marketable"]) / fmv["fmv_marketable"]
        opm_r["divergence_vs_waterfall"] = round(gap, 3)
        if gap > 0.40:
            audit.warn(f"OPM: OPM vs waterfall FMV diverge {gap*100:.0f}% (>40%) — reconcile.")

    out.update({
        "waterfall": wf, "common_fmv": fmv, "dlom": dl, "strike": sp,
        "sensitivity": sens, "legal_audit": legal,
        "opm": opm_r, "opm_backsolve": backsolve_r,
        "headline": {
            "enterprise_value": rec["blended_enterprise_value"],
            "equity_value": eq,
            "common_fmv_marketable": fmv["fmv_marketable"],
            "opm_fmv_marketable": opm_r["fmv_marketable"] if opm_r else None,
            "dlom": dl["recommended_dlom"],
            "recommended_409a_strike": sp["strike_price"],
        },
    })
    return out


# --------------------------------------------------------------------------- #
# Intake validation (preflight)                                                 #
# --------------------------------------------------------------------------- #
def validate(intake):
    """Return (errors, warnings). Errors block; warnings inform. Mirrors
    references/intake-schema.md validation rules."""
    errors, warnings = [], []

    # Hard gate: at least one valuation basis must exist.
    has_dcf = bool(g(intake, "forecasts.revenue"))
    has_comps = bool(g(intake, "comparables.peers"))
    has_round = any(
        r.get("post_money") or r.get("price_per_share")
        for r in (intake.get("financing_rounds", []) or [])
    )
    if not (has_dcf or has_comps or has_round):
        errors.append("No valuation basis: need forecasts.revenue, comparables.peers, "
                      "or a priced financing round with post_money or price_per_share.")

    # DCF coherence.
    r = g(intake, "forecasts.discount_rate", 0.25)
    gt = g(intake, "forecasts.terminal_growth", 0.03)
    if has_dcf and r <= gt:
        warnings.append(f"discount_rate ({r}) <= terminal_growth ({gt}); terminal value -> 0.")

    # Shares present for FMV.
    if not g(intake, "shares.common"):
        warnings.append("shares.common missing/zero — common FMV cannot be computed.")

    # Convertibles without share counts.
    for instr in (g(intake, "shares.safes", []) or []) + (g(intake, "shares.convertible_notes", []) or []):
        if instr.get("as_converted_shares") is None:
            warnings.append(f"Convertible '{instr.get('name','?')}' lacks as_converted_shares "
                            "(excluded from fully-diluted).")

    # Preferred term completeness.
    for s in (g(intake, "shares.preferred", []) or []):
        for field in ("liquidation_multiple", "participating", "invested", "shares"):
            if s.get(field) is None:
                warnings.append(f"Preferred '{s.get('name','?')}' missing {field}.")

    # PWERM probabilities.
    scen = g(intake, "pwerm.scenarios")
    if scen:
        total = sum(x.get("probability", 0) for x in scen)
        if abs(total - 1.0) > 1e-6:
            warnings.append(f"PWERM probabilities sum to {total:.3f} (will be normalized).")

    # Dates parseable.
    for path in ("entity.valuation_date", "compliance.last_valuation_date"):
        v = g(intake, path)
        if v:
            try:
                datetime.fromisoformat(v)
            except ValueError:
                warnings.append(f"{path} ('{v}') is not ISO format (YYYY-MM-DD).")

    # Professional reliance controls.
    controls = intake.get("review_controls", {}) or {}
    if not controls:
        warnings.append("review_controls missing — legal/appraiser/auditor reliance gate will remain open.")

    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description="409A Valuation Engine")
    ap.add_argument("command", choices=["audit", "value", "compliance", "validate", "all"])
    ap.add_argument("--intake", required=True)
    ap.add_argument("--out", default=".")
    args = ap.parse_args()

    with open(args.intake) as f:
        intake = json.load(f)

    audit = Audit()
    val_date = g(intake, "entity.valuation_date") or g(intake, "valuation_date") \
        or date.today().isoformat()

    # Always preflight; surface blocking errors before any math runs.
    errors, warnings = validate(intake)
    for w in warnings:
        audit.warn("VALIDATE: " + w)
    if args.command == "validate":
        print(json.dumps({"errors": errors, "warnings": warnings}, indent=2))
        sys.exit(1 if errors else 0)
    if errors:
        print(json.dumps({"errors": errors,
                          "message": "Intake failed validation — fix errors before valuing."},
                         indent=2))
        sys.exit(2)

    results = {}
    if args.command == "audit":
        results["cap_table"] = cap_table(intake, audit)
    if args.command in ("value", "all"):
        results.update(run_value(intake, audit))
    if args.command in ("compliance", "all"):
        results["compliance"] = compliance(intake, audit)

    audit_log = audit.dump(val_date)
    print(json.dumps({"results": results, "audit": audit_log}, indent=2, default=str))

    if args.command == "all":
        import os
        os.makedirs(args.out, exist_ok=True)
        with open(os.path.join(args.out, "results.json"), "w") as f:
            json.dump(results, f, indent=2, default=str)
        with open(os.path.join(args.out, "audit_log.json"), "w") as f:
            json.dump(audit_log, f, indent=2, default=str)
        print(f"\nWrote {args.out}/results.json and {args.out}/audit_log.json", file=sys.stderr)


if __name__ == "__main__":
    main()
