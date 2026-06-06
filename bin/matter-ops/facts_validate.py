#!/usr/bin/env python3
"""GLAW autonomous evidence validator — the state machine that decides RUN vs WAIT.
Implements the evidence-gathering contract: validate each of the 8 facts, detect
contradictions / weak support, score confidence, and emit a final state:
  READY      -> all facts present + format-valid + no contradictions -> live loop is authorized
  BLOCKED    -> required evidence missing (often human/external-only) -> gather, do NOT run the loop
  FAILED     -> a contradiction prevents validation -> resolve before anything else
DRAFTING-CLEAN is NOT a terminal state here; this gate exists to push toward BULLETPROOF.
Zero spend, deterministic. Run after every new piece of evidence is added.

Usage: facts_validate.py <slug> [--json]
"""
import sys, os, json, re, datetime as dt

# acquire: "external" = an AI cannot manufacture it (decision/appraisal/filing); "internal" = derivable from records.
SPEC = {
  "issuance_date":   {"label": "Founder-stock issuance date",        "acquire": "external (counsel decision)"},
  "cap_table":       {"label": "Cap table (founders/shares/pool)",   "acquire": "external (founder+counsel)"},
  "gross_assets":    {"label": "Gross-assets balance sheet @ issuance","acquire": "external (CPA)"},
  "ip_valuation":    {"label": "Third-party IP valuation",            "acquire": "external (independent appraiser)"},
  "ein_hq":          {"label": "EIN + HQ address",                    "acquire": "external (filed SS-4)"},
  "controlled_group":{"label": "§52/§448(c) controlled-group",        "acquire": "external (CPA)"},
  "residence_state": {"label": "State of residence + marital",        "acquire": "external (founder)"},
  "valuation_409a":  {"label": "409A valuation",                      "acquire": "external (409A appraiser)"},
}
def num(s):
    m = re.search(r"[\d,]+(?:\.\d+)?", str(s).replace("$", ""))
    return float(m.group(0).replace(",", "")) if m else None

def validate(d):
    res = {}
    for k, meta in SPEC.items():
        v = (d.get(k) or "").strip()
        status, notes = "MISSING", []
        if v and not any(t in v.upper() for t in ("[VERIFY", "TBD", "????")):
            status = "PRESENT"
            # per-fact format checks
            if k == "issuance_date":
                m = re.search(r"(\d{4})-(\d{2})-(\d{2})", v)
                if not m: status, notes = "WEAK", ["no parseable YYYY-MM-DD date"]
                else:
                    try:
                        date = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                        if date <= dt.date(2025, 7, 4):
                            status, notes = "CONTRADICTION", ["date is on/before 2025-07-04 -> OBBBA QSBS regime not available"]
                        else:
                            status = "VERIFIED"
                    except Exception:
                        status, notes = "WEAK", ["invalid date"]
            elif k == "ein_hq":
                status = "VERIFIED" if re.search(r"\b\d{2}-\d{7}\b", v) else "WEAK"
                if status == "WEAK": notes = ["no EIN in NN-NNNNNNN format"]
            elif k in ("gross_assets", "ip_valuation", "valuation_409a"):
                status = "VERIFIED" if num(v) is not None else "WEAK"
                if status == "WEAK": notes = ["no dollar figure found"]
            else:
                status = "VERIFIED"
        res[k] = {"label": meta["label"], "acquire": meta["acquire"], "value": v, "status": status, "notes": notes}
    return res

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    slug = sys.argv[1]
    as_json = "--json" in sys.argv
    # Respect $GLAW_HOME (matches bin/glaw + facts_gate.py); default to ~/.glaw.
    glaw_home = os.environ.get("GLAW_HOME") or os.path.expanduser("~/.glaw")
    p = os.path.join(glaw_home, "matters", slug, "facts.json")
    d = json.load(open(p)) if os.path.exists(p) else {}
    res = validate(d)

    contradictions = [k for k, r in res.items() if r["status"] == "CONTRADICTION"]
    missing = [k for k, r in res.items() if r["status"] == "MISSING"]
    weak = [k for k, r in res.items() if r["status"] == "WEAK"]
    verified = [k for k, r in res.items() if r["status"] == "VERIFIED"]
    # cross-fact contradiction: IP valuation must not exceed gross assets total
    ga, ip = num(d.get("gross_assets")), num(d.get("ip_valuation"))
    cross = []
    if ga is not None and ip is not None and ip > ga:
        cross.append("ip_valuation > gross_assets total — internally inconsistent")
        contradictions.append("ip_valuation~gross_assets")

    confidence = round(len(verified) / len(SPEC), 2)
    # Launch-guard vocabulary (fail-closed): only LAUNCH_AUTHORIZED enables the Chief loop.
    if contradictions:        state, launch = "FAILED",  "FACT_CONFLICT"
    elif missing:             state, launch = "BLOCKED", "FACT_INCOMPLETE"
    elif weak:                state, launch = "BLOCKED", "FACT_VALIDATION_PENDING"
    else:                     state, launch = "READY",   "LAUNCH_AUTHORIZED"

    next_actions = []
    if state == "READY":
        next_actions.append("AUTO-RUN AUTHORIZED: launch /glaw-chief-counsel (it will reach BULLETPROOF, not DRAFTING-CLEAN).")
    else:
        for k in missing + weak:
            next_actions.append(f"ACQUIRE {k}: {res[k]['label']} — {res[k]['acquire']}")
        for c in cross: next_actions.append("RESOLVE contradiction: " + c)
        for k in contradictions:
            if k in res: next_actions.append(f"RESOLVE {k}: {'; '.join(res[k]['notes'])}")

    BLOCKED_MSG = ("LAUNCH BLOCKED: FACT-INCOMPLETE MATTER. COMPLETE AND VERIFY ALL 8 REQUIRED FACTS "
                   "BEFORE CHIEF LOOP ACTIVATION.")
    report = {"slug": slug, "state": state, "launch_status": launch, "confidence": confidence,
              "collected": len(SPEC) - len(missing), "verified": len(verified), "of": len(SPEC),
              "contradictions": len(contradictions), "missing": len(missing),
              "facts": res, "cross_checks": cross, "next_actions": next_actions,
              "blocked_message": None if launch == "LAUNCH_AUTHORIZED" else BLOCKED_MSG}
    if as_json:
        print(json.dumps(report, indent=2)); sys.exit(0 if launch == "LAUNCH_AUTHORIZED" else 1)
    print(f"=== CHIEF LOOP LAUNCH GUARD — {slug} ===")
    print(f"LAUNCH_STATUS: {launch}   STATE: {state}   CONFIDENCE: {confidence}")
    print(f"COLLECTED: {len(SPEC)-len(missing)}/8   VERIFIED: {len(verified)}/8   CONTRADICTIONS: {len(contradictions)}\n")
    for k, r in res.items():
        print(f"  [{r['status']:13}] {k}: {r['value'] or '—'}")
        for n in r["notes"]: print(f"        ! {n}")
        if r['status'] in ('MISSING','WEAK'): print(f"        source: {r['acquire']}")
    for c in cross: print(f"  ! CROSS: {c}")
    print("\nNEXT ACTIONS (autonomous recovery — gather, do NOT launch):")
    for a in next_actions: print(f"  - {a}")
    if launch != "LAUNCH_AUTHORIZED":
        print(f"\n{BLOCKED_MSG}")
    sys.exit(0 if launch == "LAUNCH_AUTHORIZED" else 1)

if __name__ == "__main__":
    main()
