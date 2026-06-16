#!/usr/bin/env bash
# golden_profile_test.sh - every executable profile has a source-backed path to chief_approved.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"

python3 - "$ROOT" <<'PY'
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
home = Path(os.environ["GLAW_HOME"])
sys.path.insert(0, str(root / "lib"))
from glaw_profiles import ADVERSARIAL_PROFILES, COUNCIL_PROFILES, GOVERNMENT_ADVERSARY_LENSES, TRACKS, profile_for_track


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def run(*args: str, ok: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        [str(root / "bin" / args[0]), *args[1:]],
        cwd=str(root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proc.returncode not in ok:
        raise AssertionError(
            f"{' '.join(args)} exited {proc.returncode}, expected {ok}\n{proc.stdout}"
        )
    return proc


TRACK_BY_PROFILE = {
    "accounting": "accounting",
    "accounting-tax": "accounting-tax",
    "tax": "tax",
    "litigation": "litigation",
    "corp-build": "corp-build",
    "contract-review": "contract-review",
    "investigation": "investigation",
    "sec-reporting": "sec-reporting",
    "hybrid": "hybrid",
}

TRACK_VALUES = {
    "accounting": {
        "bank_statement_sources": "bank.csv",
        "books_status": "source statements and draft ledger",
        "accounting_periods": "2026",
        "reports_needed": "trial balance; balance sheet; bank reconciliation",
    },
    "accounting-tax": {
        "bank_statement_sources": "bank.csv",
        "tax_years": "2026",
        "entity_tax_type": "C-corp",
        "books_status": "source statements and draft ledger",
        "irs_forms_needed": "1120",
    },
    "tax": {
        "tax_years": "2026",
        "taxpayer_type": "C-corp",
        "tax_forms_needed": "1120; 941",
        "source_records": "returns; GL export; bank.csv",
        "positions_or_issues": "books-to-return tie-out",
        "filing_or_exam_deadlines": "2026-09-15 extended return due",
    },
    "litigation": {
        "claims_or_defenses": "breach of contract defense",
        "forum": "federal district court",
        "relief_requested": "dismissal or settlement authority",
        "evidence_sources": "contract; payment ledger",
    },
    "corp-build": {
        "entity_type": "Delaware C-corp",
        "owners": "Founder; investor",
        "capitalization": "10,000,000 authorized common shares",
        "tax_elections": "review 83(b) and S-election availability",
        "filings_needed": "charter; bylaws; board consent",
    },
    "contract-review": {
        "contract_type": "services agreement",
        "counterparty": "Vendor LLC",
        "governing_law": "Delaware",
        "review_standard": "enterprise risk review",
    },
    "investigation": {
        "targets": "payment diversion suspect",
        "suspected_conduct": "invoice redirection",
        "evidence_sources": "bank.csv; email export",
        "reporting_path": "civil recovery and regulator referral analysis",
    },
    "sec-reporting": {
        "filer_status": "accelerated filer",
        "period_end": "2026-06-30",
        "forms_needed": "10-Q; 8-K if triggered",
        "audited_financial_sources": "trial balance; bank reconciliation",
        "xbrl_scope": "financial statements and notes",
    },
    "hybrid": {
        "tracks_in_scope": "corp-build; tax; litigation",
        "sequencing": "structure first, then tax review, then litigation readiness",
        "shared_evidence_sources": "bank.csv; charter; contract",
    },
}


def set_intake(track: str) -> None:
    universal = {
        "workflow_track": track,
        "client_names": "Golden Client Inc.",
        "parties": "Golden Client Inc.; regulator; counterparty",
        "jurisdiction": "Federal; Delaware; Florida",
        "goal": f"golden {track} matter clears all quality gates",
        "source_documents": "bank.csv; source package",
        "deadlines": "2026-09-15 verify filing deadline",
        "facts_timeline": "2026-01-01 source package received",
        "open_questions": "none for golden fixture",
        "conflicts_parties": "Golden Client Inc.; regulator; counterparty",
        "authorized_scope": "review and draft only; no filing without human authority",
    }
    for key, value in universal.items():
        run("glaw-intake", "set", key, value)
    for key in TRACKS[track]:
        run("glaw-intake", "set", f"track_specific.{key}", TRACK_VALUES[track][key])
    run("glaw-intake", "complete", "--by", "Jordan Lee, intake counsel")


def write_accounting_inputs(matter: Path) -> tuple[Path, Path, Path]:
    work = matter / "workpapers"
    work.mkdir(exist_ok=True)
    ledger = work / "ledger-input.json"
    rec = work / "bank-rec-input.json"
    tax = work / "tax-tieout-input.json"
    ledger.write_text(json.dumps({
        "rows": [{
            "booking_date": "2026-01-01",
            "description": "capital deposit",
            "normalized_description": "CAPITAL DEPOSIT",
            "amount": "100.00",
            "currency": "USD",
            "category": "Equity:Owner:Contributions",
            "transaction_hash": "golden-fixture-001",
            "source_method": "deterministic",
        }],
        "audit": [{"source": "evidence/bank.csv", "balance_status": "verified"}],
    }, indent=2) + "\n", encoding="utf-8")
    rec.write_text(json.dumps({
        "matched": 1,
        "book_only": [],
        "bank_only": [],
        "sum_book": "100.00",
        "sum_bank": "100.00",
        "unreconciled_difference": "0.00",
        "reconciled": True,
    }, indent=2) + "\n", encoding="utf-8")
    tax.write_text(json.dumps({
        "provision_ties": True,
        "internal": {"consistent": True},
    }, indent=2) + "\n", encoding="utf-8")
    return ledger, rec, tax


def run_profile(profile: str) -> None:
    track = TRACK_BY_PROFILE[profile]
    if profile_for_track(track) != profile:
        raise AssertionError(f"track {track} maps to {profile_for_track(track)}, not {profile}")
    name = f"Golden {profile}"
    run("glaw", "matter", "new", name)
    slug = slugify(name)
    matter = home / "matters" / slug
    evidence = matter / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "bank.csv").write_text(
        "date,description,amount\n2026-01-01,capital deposit,100.00\n",
        encoding="utf-8",
    )

    set_intake(track)
    run("glaw-ethics", "record-conflicts", "--status", "cleared",
        "--notes", "golden fixture conflict search clear", "--source", "SRC-0001 source package reviewed")
    run("glaw-ethics", "draft-engagement", "--scope", "review and draft only",
        "--responsible-professional", "Alex Rivera, licensed attorney",
        "--source", "SRC-0001 authorized scope reviewed")
    run("glaw-ethics", "complete")
    run("glaw", "stage", "strategy")

    run("glaw-red-flags", "complete")
    for role in COUNCIL_PROFILES[profile]:
        run("glaw-council", "record", "--profile", "auto", "--role", role,
            "--decision", "approve", "--evidence", "SRC-0001 source package reviewed",
            "--notes", f"{role} source-backed golden approval conclusion")
    run("glaw-council", "complete", "--profile", "auto")

    for lens in ADVERSARIAL_PROFILES[profile]:
        run("glaw-adversarial", "record", "--profile", "auto", "--lens", lens,
            "--decision", "survive",
            "--attack", f"SRC-0001 {lens} challenged the packet and found no fatal defect",
            "--evidence", "SRC-0001 source package reviewed")
    run("glaw-adversarial", "complete", "--profile", "auto")

    run("glaw-citation-corpus", "capture", "--id", f"CORP-{profile.upper()}-0001",
        "--source-url", "https://www.irs.gov/",
        "--text", "GLAW workflow source evidence rule supports source-backed licensed review.",
        "--segment", "supports source-backed licensed review")
    run("glaw-citation-gate", "record", "--id", f"C-{profile.upper()}-0001",
        "--proposition", "The golden fixture is source-backed and held for licensed review",
        "--authority", "GLAW workflow source-evidence rule",
        "--status", "verified", "--source-url", "https://www.irs.gov/",
        "--reviewer", "legal-research",
        "--support-summary", "The workflow rule supports keeping the fixture source-backed and subject to licensed review.",
        "--corpus-id", f"CORP-{profile.upper()}-0001")
    run("glaw-citation-gate", "complete")

    report = matter / "golden-report.md"
    report.write_text(f"""# Golden {profile} Report

Owner: GLAW {profile} bench
Report voice: senior {profile} quality-control report.
Findings: The fixture ties every material conclusion to source evidence.
Evidence: SRC-0001 source package.
Red flags: none.
Sign-off conditions: licensed professional and human-authority review before any binding act.

Attorney work-product - not legal advice. Prepared for licensed review.
""", encoding="utf-8")

    if profile in {"accounting", "accounting-tax", "tax", "sec-reporting"}:
        ledger, rec, tax = write_accounting_inputs(matter)
        args = [
            "glaw-accounting-control", "--matter", slug, "--profile", profile,
            "--source", "SRC-0001 source package, ledger, bank reconciliation, and tie-out reviewed",
            "--ledger", str(ledger), "--bank-rec", str(rec),
        ]
        if profile in {"accounting-tax", "tax"}:
            args.extend(["--tax-tieout", str(tax)])
        run(*args)

    run("glaw-final-packet", "build", "--profile", "auto", "--matter", slug)
    run("glaw-chief-decision", "--matter", slug,
        "--chief", "GLAW Chief Counsel", "--score", "95", "--grade", "A",
        "--decision", "PROCEED", "--risks", "none",
        "--conditions", "licensed signer final review; no filing without human authority",
        "--rationale", "SRC-0001 all golden profile gates clear and source manifests tie out",
        "--approve-final")
    run("glaw", "stage", "file")

    packet = json.loads((matter / "final_packet.json").read_text(encoding="utf-8"))
    decisions = [
        json.loads(line)
        for line in (matter / "decisions.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    approved = [row for row in decisions if row.get("final_gate") == "approved"]
    if packet.get("status") != "ready" or packet.get("workflow_profile") != profile or not approved:
        raise AssertionError(f"{profile} did not reach ready/chief_approved")
    if not any(json.loads(line).get("event") == "chief_approved" for line in (matter / "timeline.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()):
        raise AssertionError(f"{profile} missing chief_approved event")
    if (matter / ".stage").read_text(encoding="utf-8").strip() != "file":
        raise AssertionError(f"{profile} did not clear file stage")
    print(f"  ✓ golden {profile} reaches chief_approved and file stage")


profiles = sorted(COUNCIL_PROFILES)
missing = sorted(set(COUNCIL_PROFILES) ^ set(ADVERSARIAL_PROFILES))
if missing:
    raise AssertionError(f"profile sets differ: {missing}")
for profile in profiles:
    if profile not in TRACK_BY_PROFILE:
        raise AssertionError(f"no golden track mapping for profile {profile}")
    if not (set(ADVERSARIAL_PROFILES[profile]) & GOVERNMENT_ADVERSARY_LENSES):
        raise AssertionError(f"{profile} lacks a government/regulatory/litigation adversary lens")
    run_profile(profile)
print()
print(f"0 failures - {len(profiles)} passed, 0 failed")
PY
rc=$?
rm -rf "$TMP"
[ "$rc" = 0 ] && { echo "ALL PASS"; exit 0; } || { echo "FAILURES"; exit "$rc"; }
