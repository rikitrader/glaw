#!/usr/bin/env bash
# court_case_test.sh — federal/Florida routing, packet, receipt, and authority boundaries.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PYTHONPATH="$ROOT/lib" python3 - "$ROOT" "$TMP" <<'PY'
from __future__ import annotations

import hashlib
import json
import os
import sys
from copy import deepcopy
from pathlib import Path

root = Path(sys.argv[1]).resolve()
tmp = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(root / "lib"))

from glaw_court import create_handoff, live_submit, prepare_packet, record_receipt, record_service, route_case, service_handoff

passed = 0


def ok(condition: bool, label: str) -> None:
    global passed
    if not condition:
        raise AssertionError(label)
    passed += 1
    print(f"  ✓ {label}")


def checks():
    return {
        name: {"status": "pass", "source_id": f"SRC-{index:04d} current authority"}
        for index, name in enumerate(("personal_jurisdiction", "venue", "standing", "limitations", "pre_suit"), start=1)
    }


def amount(value: int):
    return {"value": value, "exclusive_of_interest_costs_fees": True, "source_id": "SRC-0010 damages evidence"}


base = {
    "forum_request": "federal",
    "case_kind": "ordinary_civil",
    "court": {"state": "Florida", "county": "Orange", "federal_district": "mdfl", "division": "Orlando"},
    "amount_in_controversy": amount(100000),
    "claims": [{"id": "title-vii", "federal_question": True, "statutory_basis": "42 U.S.C. § 2000e", "source_id": "SRC-0011 verified claim"}],
    "parties": {
        "plaintiffs": [{"name": "Alice", "entity_type": "individual", "domicile": "Florida", "source_id": "SRC-0012 domicile evidence"}],
        "defendants": [{"name": "Acme", "entity_type": "corporation", "state_of_incorporation": "Delaware", "principal_place_of_business": "Georgia", "source_id": "SRC-0013 entity evidence"}],
    },
    "jurisdiction_checks": checks(),
}

federal = route_case(base)
ok(federal["status"] == "pass" and federal["selected"]["court_code"] == "mdfl", "verified federal-question case routes to M.D. Florida")

unverified = deepcopy(base)
unverified["court"]["federal_district"] = "sdfl"
review = route_case(unverified)
ok(review["status"] == "review" and "lacks a current verified local-rule pack" in " ".join(review["selected"]["failures"]), "unverified district local rules force review")

diversity = deepcopy(base)
diversity["claims"] = []
diversity["parties"]["defendants"] = [{
    "name": "Nested LLC",
    "entity_type": "llc",
    "source_id": "SRC-0013 LLC evidence",
    "members": [{"name": "Florida Member", "entity_type": "individual", "domicile": "Florida", "source_id": "SRC-0014 member domicile"}],
}]
blocked = route_case(diversity)
ok(blocked["status"] == "block" and "complete diversity fails" in " ".join(blocked["candidates"][0]["basis_analysis"]["diversity_failures"]), "recursive LLC citizenship blocks incomplete diversity")

for value, division in ((8000, "small_claims"), (50000, "county_civil"), (50001, "circuit_civil")):
    state_case = deepcopy(base)
    state_case["forum_request"] = "florida"
    state_case["claims"] = []
    state_case["amount_in_controversy"] = amount(value)
    routed = route_case(state_case)
    ok(routed["status"] == "pass" and routed["selected"]["division"] == division and routed["selected"]["judicial_circuit"] == 9, f"Florida ${value:,} routes to {division}")

bad_county = deepcopy(base)
bad_county["forum_request"] = "florida"
bad_county["court"]["county"] = "Imaginary"
ok(route_case(bad_county)["status"] == "block", "unknown Florida county fails closed")

matter = tmp / "matter"
matter.mkdir()
gate_evidence = {}
for name in ("citations_verified", "adversarial_clear", "writing_clear", "final_packet_ready", "chief_approved"):
    path = matter / f"{name}.json"
    path.write_text(json.dumps({"status": "pass", "name": name}) + "\n", encoding="utf-8")
    gate_evidence[name] = {"status": "pass", "artifact": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

documents = []
for role, filename in (("complaint", "complaint.pdf"), ("civil_cover_sheet", "js44.pdf"), ("summons", "summons.pdf"), ("corporate_disclosure", "rule-7.1.pdf")):
    path = matter / filename
    path.write_bytes((role + " final PDF fixture").encode())
    documents.append({"role": role, "path": filename})
case_data = deepcopy(base)
case_data["gate_evidence"] = gate_evidence
case_data["documents"] = documents
case_path = matter / "case.json"
case_path.write_text(json.dumps(case_data, indent=2) + "\n", encoding="utf-8")

packet = prepare_packet(case_path, matter / "filing")
ok(packet["status"] == "ready_for_human_filing" and not packet["failures"], "source-backed checksum packet becomes ready for human filing")
packet_path = Path(packet["manifest_path"])

handoff = create_handoff(packet_path, matter / "filing" / "handoff.json")
ok(handoff["status"] == "ready_for_human_operator" and handoff["platform"] == "CM/ECF", "manual CM/ECF handoff validates unchanged artifacts")

premature_service = service_handoff(packet_path, matter / "filing" / "premature-service-handoff.json")
ok(premature_service["status"] == "blocked", "service handoff blocks until an official filing receipt is recorded")

denied = live_submit(packet_path, "", "")
ok(denied["status"] == "blocked" and denied["submitted"] is False, "live submission without human authority is blocked")
authorized_but_unconnected = live_submit(packet_path, "Licensed filer", "ADMIN")
ok(authorized_but_unconnected["status"] == "blocked" and authorized_but_unconnected["submitted"] is False and authorized_but_unconnected.get("human_authority") == "Licensed filer", "human authority cannot bypass missing court connector")

receipt_artifact = matter / "filing" / "official-receipt.pdf"
receipt_artifact.write_bytes(b"official court receipt fixture")
receipt_data = {
    "case_number": "6:26-cv-00001",
    "court": "M.D. Fla.",
    "filed_at": "2026-08-13T15:30:00-04:00",
    "filed_by": "Licensed filer",
    "receipt_artifact": receipt_artifact.name,
}
receipt_path = matter / "filing" / "receipt.json"
receipt_path.write_text(json.dumps(receipt_data) + "\n", encoding="utf-8")
recorded = record_receipt(packet_path, receipt_path, "Docket clerk")
ok(recorded["status"] == "recorded" and recorded["receipt_sha256"], "official filing receipt creates a hashed docket event")

service = service_handoff(packet_path, matter / "filing" / "service-handoff.json")
ok(service["status"] == "ready_for_human_operator", "service workflow creates preparation-only handoff")
proof_artifact = matter / "filing" / "proof-of-service.pdf"
proof_artifact.write_bytes(b"proof of service fixture")
proof_path = matter / "filing" / "service.json"
proof_path.write_text(json.dumps({
    "defendant": "Acme",
    "served_at": "2026-08-20",
    "method": "personal service",
    "server": "Authorized process server",
    "proof_artifact": proof_artifact.name,
}) + "\n", encoding="utf-8")
service_record = record_service(packet_path, proof_path, "Docket clerk")
ok(service_record["status"] == "recorded" and service_record["candidate_answer_date"] == "2026-09-10" and service_record["deadline_status"] == "review_required", "actual service proof drives a review-required candidate answer date")

tampered = matter / "complaint.pdf"
tampered.write_bytes(b"changed after packet")
blocked_handoff = create_handoff(packet_path, matter / "filing" / "tampered-handoff.json")
ok(blocked_handoff["status"] == "blocked", "post-packet document tamper blocks filing handoff")

print(f"\n0 failures — {passed} passed, 0 failed")
PY
