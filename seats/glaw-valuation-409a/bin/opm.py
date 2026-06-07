#!/usr/bin/env python3
"""OPM (Option Pricing Method) common-stock allocation for §409A — real Black-Scholes math, not hand-waving.
Allocates equity value across a simplified preferred/common stack so the common FMV (and the 409A strike)
is a defensible NUMBER an appraiser can review. Early-stage simplification: one aggregate liquidation
preference breakpoint + as-converted upside. A qualified appraiser refines breakpoints for the full stack.

Usage:
  opm.py --equity 15000000 --pref 15000000 --fd-shares 10000000 --common-shares 8000000 \
         --sigma 0.60 --years 4 --rate 0.04 --dlom 0.30
  opm.py --backsolve-price 1.50 --pref-shares 10000000 ...   # backsolve equity from last round price
"""
import sys, math, argparse

def norm_cdf(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def bs_call(S, K, T, r, sigma):
    if K <= 0: return S
    if S <= 0 or T <= 0 or sigma <= 0: return max(S - K, 0.0)
    d1 = (math.log(S / K) + (r + sigma * sigma / 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--equity", type=float, help="total equity (enterprise) value")
    p.add_argument("--pref", type=float, default=0.0, help="aggregate liquidation preference ($)")
    p.add_argument("--fd-shares", type=float, required=True)
    p.add_argument("--common-shares", type=float, required=True)
    p.add_argument("--sigma", type=float, default=0.60, help="volatility (0.5-0.9 early-stage)")
    p.add_argument("--years", type=float, default=4.0, help="time to liquidity")
    p.add_argument("--rate", type=float, default=0.04, help="risk-free rate")
    p.add_argument("--dlom", type=float, default=0.30, help="discount for lack of marketability (0.2-0.4 early)")
    p.add_argument("--backsolve-price", type=float, help="last-round price/preferred share -> backsolve equity")
    p.add_argument("--pref-shares", type=float, help="preferred shares (for backsolve)")
    a = p.parse_args()

    E = a.equity
    note = ""
    if a.backsolve_price and a.pref_shares:
        # crude backsolve: equity such that preferred per-share (as-converted upside) ~ round price.
        # Practical proxy: E ≈ price × fully-diluted shares (post-money), refined by appraiser.
        E = a.backsolve_price * a.fd_shares
        note = f"(backsolved: {a.backsolve_price}/sh × {a.fd_shares:.0f} FD = post-money proxy)"
    if not E:
        print("ERROR: provide --equity or (--backsolve-price + --pref-shares)"); sys.exit(2)

    # Tranche above the liquidation preference is the common upside (as-converted, pro-rata).
    upside = bs_call(E, a.pref, a.years, a.rate, a.sigma)
    pref_value = E - upside
    common_value_marketable = upside * (a.common_shares / a.fd_shares)
    common_ps_marketable = common_value_marketable / a.common_shares if a.common_shares else 0
    common_ps_409a = common_ps_marketable * (1 - a.dlom)

    audit_risk = "Low" if a.dlom <= 0.35 and a.sigma <= 0.9 else "Medium"
    print("# OPM COMMON-STOCK ALLOCATION (§409A)  " + note)
    print(f"Inputs: equity=${E:,.0f}  liq-pref=${a.pref:,.0f}  FD={a.fd_shares:,.0f}  common={a.common_shares:,.0f}")
    print(f"        sigma={a.sigma}  T={a.years}y  r={a.rate}  DLOM={a.dlom:.0%}")
    print("-" * 64)
    print(f"Preferred/liq-pref value : ${pref_value:,.0f}")
    print(f"Common upside (BS call)  : ${upside:,.0f}")
    print(f"Common value (pro-rata)  : ${common_value_marketable:,.0f}")
    print(f"Common /sh (marketable)  : ${common_ps_marketable:,.4f}")
    print(f"DLOM applied             : -{a.dlom:.0%}")
    print("=" * 64)
    print(f"409A FMV per common share: ${common_ps_409a:,.4f}")
    print(f"RECOMMENDED STRIKE PRICE : ${common_ps_409a:,.4f}")
    print(f"IRS 409A audit risk flag : {audit_risk}  (verify DLOM + sigma with appraiser)")
    print("\n> DRAFT model — a QUALIFIED INDEPENDENT APPRAISER must review breakpoints, sigma, DLOM, and sign for the safe harbor.")

if __name__ == "__main__":
    main()
