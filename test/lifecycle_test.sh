#!/usr/bin/env bash
# lifecycle_test.sh — full source-only matter lifecycle gate test.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
INTAKE="$ROOT/bin/glaw-intake"
COUNCIL="$ROOT/bin/glaw-council"
FLAGS="$ROOT/bin/glaw-red-flags"
PACKET="$ROOT/bin/glaw-final-packet"
CHIEF="$ROOT/bin/glaw-chief-decision"
ADVERSARIAL="$ROOT/bin/glaw-adversarial"
ETHICS="$ROOT/bin/glaw-ethics"
CITES="$ROOT/bin/glaw-citation-gate"
DOCKET="$ROOT/bin/glaw-docket-gate"
CONTROL="$ROOT/bin/glaw-accounting-control"

"$GLAW" matter new "Lifecycle Accounting" >/dev/null
SLUG="lifecycle-accounting"
ok "$([ -f "$TMP/matters/$SLUG/intake.json" ] && echo 1 || echo 0)" "matter new creates intake.json"
"$GLAW" timeline-log chief_approved >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && ! grep -q 'chief_approved' "$TMP/matters/$SLUG/timeline.jsonl" && echo 1 || echo 0)" "manual timeline-log refuses reserved chief_approved gate event"
"$GLAW" timeline-log operator_note >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && grep -q 'operator_note' "$TMP/matters/$SLUG/timeline.jsonl" && echo 1 || echo 0)" "manual timeline-log still allows non-gate operator notes"

"$GLAW" stage strategy >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "strategy blocked before intake/conflicts"

"$INTAKE" set workflow_track accounting-tax >/dev/null
"$INTAKE" set client_names 'Acme Inc.' >/dev/null
"$INTAKE" set parties 'Acme Inc.; Bank' >/dev/null
"$INTAKE" set jurisdiction 'Florida' >/dev/null
"$INTAKE" set goal 'reconstruct books and tax package' >/dev/null
"$INTAKE" set source_documents 'bank.csv' >/dev/null
"$INTAKE" set deadlines '2026-09-15 tax filing' >/dev/null
"$INTAKE" set facts_timeline '2026-01-01 opening balance' >/dev/null
"$INTAKE" set open_questions 'none' >/dev/null
"$INTAKE" set conflicts_parties 'Acme Inc.; Bank' >/dev/null
"$INTAKE" set authorized_scope 'review and draft only' >/dev/null
"$INTAKE" set track_specific.bank_statement_sources 'bank.csv' >/dev/null
"$INTAKE" set track_specific.tax_years '2026' >/dev/null
"$INTAKE" set track_specific.entity_tax_type 'C-corp' >/dev/null
"$INTAKE" set track_specific.books_status 'raw statements' >/dev/null
"$INTAKE" set track_specific.irs_forms_needed '1120' >/dev/null
"$INTAKE" complete >/dev/null
"$ETHICS" record-conflicts --status cleared --notes 'no conflict in test fixture' >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "ethics conflicts blocked without source evidence id"
"$ETHICS" record-conflicts --status cleared --notes 'no conflict in test fixture' --source 'SRC-9999 stale intake party list reviewed' >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "ethics conflicts blocked by non-current source evidence id"
mkdir -p "$TMP/matters/$SLUG/evidence"
printf 'date,description,amount\n2026-01-01,capital deposit,100.00\n' > "$TMP/matters/$SLUG/evidence/bank.csv"
"$ETHICS" record-conflicts --status cleared --notes 'no conflict in test fixture' --source 'SRC-0001 intake party list reviewed' >/dev/null
"$ETHICS" draft-engagement --scope 'review and draft only' --responsible-professional 'licensed reviewer' >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "ethics engagement blocked without source evidence id"
"$ETHICS" draft-engagement --scope 'review and draft only' --responsible-professional 'licensed reviewer' --source 'SRC-9999 stale authorized scope reviewed' >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "ethics engagement blocked by non-current source evidence id"
"$ETHICS" draft-engagement --scope 'review and draft only' --responsible-professional 'licensed reviewer' --source 'SRC-0001 authorized scope reviewed' >/dev/null
"$ETHICS" complete >/dev/null
"$GLAW" stage strategy >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "strategy clears after intake/conflicts"

"$FLAGS" add --severity high --owner cfo --source test --finding 'cash tie-out missing' --required-fix 'attach bank reconciliation' >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "red flag add blocked without source evidence id"
"$FLAGS" add --severity high --owner cfo --source "SRC-9999 stale bank statement" --finding 'cash tie-out missing' --required-fix 'attach bank reconciliation' >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "red flag add blocked by non-current source evidence id"
"$FLAGS" add --severity high --owner cfo --source "SRC-0001 bank statement" --finding 'cash tie-out missing' --required-fix 'attach bank reconciliation' >/dev/null
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by open high red flag"
"$FLAGS" resolve RF-0001 --evidence 'bank reconciliation attached' >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "red flag resolution blocked without source evidence id"
"$FLAGS" resolve RF-0001 --evidence 'SRC-9999 bank reconciliation attached' >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "red flag resolution blocked by non-current source evidence id"
"$FLAGS" complete >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "red flags complete blocked while high flag remains open"

"$COUNCIL" record --profile auto --role cfo --decision approve >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "council approve blocked without evidence"
"$COUNCIL" record --profile auto --role cfo --decision approve --evidence "test fixture review basis" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "council approve blocked without source evidence id"
"$COUNCIL" record --profile auto --role cfo --decision approve --evidence "SRC-9999 test fixture review basis" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "council approve blocked without role-specific conclusion"
"$COUNCIL" record --profile auto --role cfo --decision approve --evidence "SRC-9999 test fixture review basis" --notes "cfo source-backed approval conclusion" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "council approve blocked by non-current source evidence id"
for role in cfo irs-audit-agent legal-counsel forensic-audit outside-critic external-reviewer; do
  "$COUNCIL" record --profile auto --role "$role" --decision approve --evidence "SRC-0001 test fixture review basis" --notes "$role source-backed approval conclusion" >/dev/null
done
cp "$TMP/matters/$SLUG/council.jsonl" "$TMP/matters/$SLUG/council.clean.jsonl"
python3 - "$TMP/matters/$SLUG/council.jsonl" <<'PY'
import json, sys
p = sys.argv[1]
rows = [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]
rows[0]["evidence"] = "tampered after review"
open(p, "w", encoding="utf-8").write("\n".join(json.dumps(r) for r in rows) + "\n")
PY
"$COUNCIL" status --profile auto >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "council status blocks tampered review ledger row"
cp "$TMP/matters/$SLUG/council.clean.jsonl" "$TMP/matters/$SLUG/council.jsonl"
"$CHIEF" --chief "GLAW Chief Counsel" --decision "PROCEED" --approve-final --matter "$SLUG" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "chief final approval blocked before final packet ready"
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked before adversarial government lenses survive"
"$ADVERSARIAL" record --profile auto --lens irs-examiner --decision survive --attack "no fatal finding" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "adversarial survive blocked without evidence"
"$ADVERSARIAL" record --profile auto --lens irs-examiner --decision survive --attack "no fatal finding" --evidence "test fixture" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "adversarial survive blocked without source evidence id"
"$ADVERSARIAL" record --profile auto --lens irs-examiner --decision survive --attack "no fatal finding" --evidence "SRC-9999 test fixture" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "adversarial survive blocked when attack lacks source evidence id"
"$ADVERSARIAL" record --profile auto --lens irs-examiner --decision survive --evidence "SRC-9999 test fixture" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "adversarial survive blocked without attack challenge"
"$ADVERSARIAL" record --profile auto --lens irs-examiner --decision survive --attack "SRC-9999 no fatal finding after source challenge" --evidence "SRC-9999 test fixture" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "adversarial survive blocked by non-current source evidence id"
for lens in irs-examiner state-tax-auditor forensic-accountant cfo-controller outside-critic; do
  "$ADVERSARIAL" record --profile auto --lens "$lens" --decision survive --attack "SRC-0001 no fatal finding after source challenge" --evidence "SRC-0001 test fixture" >/dev/null
done
cp "$TMP/matters/$SLUG/adversarial.jsonl" "$TMP/matters/$SLUG/adversarial.clean.jsonl"
python3 - "$TMP/matters/$SLUG/adversarial.jsonl" <<'PY'
import json, sys
p = sys.argv[1]
rows = [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]
rows[0]["decision"] = "fix"
open(p, "w", encoding="utf-8").write("\n".join(json.dumps(r) for r in rows) + "\n")
PY
"$ADVERSARIAL" status --profile auto >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "adversarial status blocks tampered review ledger row"
cp "$TMP/matters/$SLUG/adversarial.clean.jsonl" "$TMP/matters/$SLUG/adversarial.jsonl"
"$ADVERSARIAL" complete --profile auto >/dev/null
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked before citation gate completes"
"$CITES" record --id C-0001 --proposition 'tax return must tie to books' --authority '26 U.S.C. § 6001' --status verified --source-url 'not-a-url' >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "citation verified row blocked without http source URL"
"$CITES" record --id C-0001 --proposition 'tax return must tie to books' --authority '26 U.S.C. § 6001' --status verified --source-url 'https://uscode.house.gov/' >/dev/null
cp "$TMP/matters/$SLUG/citations.jsonl" "$TMP/matters/$SLUG/citations.clean.jsonl"
python3 - "$TMP/matters/$SLUG/citations.jsonl" <<'PY'
import json, sys
p = sys.argv[1]
rows = [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]
rows[0]["authority"] = "tampered authority"
open(p, "w", encoding="utf-8").write("\n".join(json.dumps(r) for r in rows) + "\n")
PY
"$CITES" status >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "citation status blocks tampered review ledger row"
cp "$TMP/matters/$SLUG/citations.clean.jsonl" "$TMP/matters/$SLUG/citations.jsonl"
"$CITES" complete >/dev/null
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked before council completion is logged"
"$COUNCIL" complete --profile auto >/dev/null
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked before external deliverable exists"
printf '# Draft Report\n\nNumbers tie to source.\n' > "$TMP/matters/$SLUG/draft-report.md"
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by deliverable missing UPL footer"
printf '\nAttorney work-product - not legal advice. Prepared for licensed review.\n' >> "$TMP/matters/$SLUG/draft-report.md"
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by deliverable missing professional report markers"
cat > "$TMP/matters/$SLUG/draft-report.md" <<'MD'
# Draft Report

Owner: GLAW Controller
Report voice: controller/CFO report.
Findings: Numbers tie to source.
Evidence: Test fixture ledger and bank statement.
Red flags: none.
Sign-off conditions: licensed review.

Attorney work-product - not legal advice. Prepared for licensed review.
MD
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by report without source evidence id"
: > "$TMP/matters/$SLUG/evidence/bank.csv"
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by empty source evidence file"
printf 'date,description,amount\n2026-01-01,capital deposit,100.00\n' > "$TMP/matters/$SLUG/evidence/bank.csv"
cat > "$TMP/matters/$SLUG/draft-report.md" <<'MD'
# Draft Report

Owner: GLAW Controller
Report voice: controller/CFO report.
Findings: Numbers tie to source; [VERIFY] placeholder remains.
Evidence: SRC-0001 bank statement.
Red flags: none.
Sign-off conditions: licensed review.

Attorney work-product - not legal advice. Prepared for licensed review.
MD
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by unresolved report placeholder"
cat > "$TMP/matters/$SLUG/draft-report.md" <<'MD'
# Draft Report

Owner: GLAW Controller
Report voice: controller/CFO report.
Findings: Numbers tie to source. REVIEW: EIN not provided.
Evidence: SRC-0001 bank statement.
Red flags: none.
Sign-off conditions: licensed review.

Attorney work-product - not legal advice. Prepared for licensed review.
MD
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by unresolved REVIEW marker"
cat > "$TMP/matters/$SLUG/draft-report.md" <<'MD'
# Draft Report

Owner: GLAW Controller
Report voice: controller/CFO report.
Findings: Numbers tie to source.
Evidence: SRC-0001 bank statement.
Red flags: none.
Sign-off conditions: licensed review.

Attorney work-product - not legal advice. Prepared for licensed review.
MD
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked before high red flag has current-source resolution"
"$FLAGS" resolve RF-0001 --evidence 'SRC-0001 bank reconciliation attached' >/dev/null
"$FLAGS" add --severity medium --owner controller --source "SRC-0001 bank statement" --finding "watch item for final reviewer" --required-fix "carry RF-0002 in Chief risks/conditions until closed" >/dev/null
"$FLAGS" complete >/dev/null
for role in cfo irs-audit-agent legal-counsel forensic-audit outside-critic external-reviewer; do
  "$COUNCIL" record --profile auto --role "$role" --decision approve --evidence "SRC-0001 test fixture review basis" --notes "$role current-source approval conclusion" >/dev/null
done
for lens in irs-examiner state-tax-auditor forensic-accountant cfo-controller outside-critic; do
  "$ADVERSARIAL" record --profile auto --lens "$lens" --decision survive --attack "SRC-0001 no fatal finding after source challenge" --evidence "SRC-0001 test fixture" >/dev/null
done
"$COUNCIL" complete --profile auto >/dev/null
"$ADVERSARIAL" complete --profile auto >/dev/null
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked before accounting control manifest"
mkdir -p "$TMP/matters/$SLUG/workpapers"
cat > "$TMP/matters/$SLUG/workpapers/ledger.json" <<'JSON'
{
  "rows": [
    {
      "booking_date": "2026-01-01",
      "description": "capital deposit",
      "normalized_description": "CAPITAL DEPOSIT",
      "amount": "100.00",
      "currency": "USD",
      "category": "Equity:Owner:Contributions",
      "transaction_hash": "fixture-001",
      "source_method": "deterministic"
    }
  ],
  "audit": [
    {
      "source": "evidence/bank.csv",
      "balance_status": "verified"
    }
  ]
}
JSON
cat > "$TMP/matters/$SLUG/workpapers/bank-rec-input.json" <<'JSON'
{
  "matched": 1,
  "book_only": [],
  "bank_only": [],
  "sum_book": "100.00",
  "sum_bank": "100.00",
  "unreconciled_difference": "0",
  "reconciled": true
}
JSON
"$CONTROL" --matter "$SLUG" --profile accounting --source "SRC-0001 bank statement, ledger, and bank reconciliation source package" --ledger "$TMP/matters/$SLUG/workpapers/ledger.json" --bank-rec "$TMP/matters/$SLUG/workpapers/bank-rec-input.json" >/dev/null
cat > "$TMP/matters/$SLUG/draft-report.md" <<'MD'
# Draft Report

Owner: GLAW Controller
Report voice: controller/CFO report.
Findings: Numbers tie to source.
Evidence: SRC-0001 bank statement plus SRC-9999 stale extract.
Red flags: none.
Sign-off conditions: licensed review.

Attorney work-product - not legal advice. Prepared for licensed review.
MD
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by report with mixed current and stale source ids"
cat > "$TMP/matters/$SLUG/draft-report.md" <<'MD'
# Draft Report

Owner: GLAW Controller
Report voice: controller/CFO report.
Findings: Numbers tie to source.
Evidence: SRC-0001 bank statement.
Red flags: none.
Sign-off conditions: licensed review.

Attorney work-product - not legal advice. Prepared for licensed review.
MD
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && [ -f "$TMP/matters/$SLUG/final_packet.json" ] && echo 1 || echo 0)" "final packet ready after council and red flags clear"
python3 - "$TMP/matters/$SLUG/final_packet.json" <<'PY'
import json, sys
p = sys.argv[1]
packet = json.load(open(p, encoding="utf-8"))
items = packet.get("reviewer_identity_manifest") or []
ok = bool(items) and all(item.get("status") == "pass" and item.get("sha256") for item in items)
sys.exit(0 if ok else 1)
PY
rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "final packet records reviewer identity manifest"

cp "$TMP/matters/$SLUG/draft-report.md" "$TMP/matters/$SLUG/draft-report.clean.md"
printf '# Draft Report\n\nStale after packet.\n' > "$TMP/matters/$SLUG/draft-report.md"
"$CHIEF" --chief "GLAW Chief Counsel" --score 95 --grade A --decision "PROCEED" --risks "none" --conditions "licensed signer final review" --rationale "all gates clear and source manifests tie out" --approve-final --matter "$SLUG" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "chief approval blocked when current packet rebuild fails"
mv "$TMP/matters/$SLUG/draft-report.clean.md" "$TMP/matters/$SLUG/draft-report.md"
"$CHIEF" --chief "GLAW Chief Counsel" --decision "PROCEED" --approve-final --matter "$SLUG" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "chief final approval blocked without complete decision card"
"$CHIEF" --chief "GLAW Chief Counsel" --score 95 --grade A --decision "PROCEED" --risks "none" --conditions "licensed signer final review" --rationale "all gates clear and source manifests tie out" --approve-final --matter "$SLUG" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "chief final approval blocked without source-backed rationale"
"$CHIEF" --chief "GLAW Chief Counsel" --score 95 --grade A --decision "PROCEED" --risks "none" --conditions "licensed signer final review" --rationale "SRC-0001 current source plus SRC-9999 stale source" --approve-final --matter "$SLUG" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "chief final approval blocked by mixed current and stale rationale sources"
"$CHIEF" --chief "GLAW Chief Counsel" --score 95 --grade A --decision "PROCEED" --risks "none" --conditions "licensed signer final review" --rationale "SRC-0001 all gates clear and source manifests tie out" --approve-final --matter "$SLUG" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "chief final approval blocked without nonblocking red flag acknowledgment"
"$CHIEF" --chief "GLAW Chief Counsel" --score 95 --grade A --decision "DENY" --risks "none" --conditions "licensed signer final review" --rationale "SRC-0001 all gates clear and source manifests tie out" --approve-final --matter "$SLUG" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "chief final approval blocked by contradictory denial decision"
"$CHIEF" --chief "GLAW Chief Counsel" --score 95 --grade A --decision "PROCEED" --risks "RF-0002 remains open as a nonblocking watch item" --conditions "licensed signer final review; RF-0002 carried until closed" --rationale "SRC-0001 all gates clear and source manifests tie out" --approve-final --matter "$SLUG" >/dev/null
python3 - "$TMP/matters/$SLUG" <<'PY'
import hashlib, json, pathlib, sys
d = pathlib.Path(sys.argv[1])
packet_hash = hashlib.sha256((d / "final_packet.json").read_bytes()).hexdigest()
rows = [json.loads(line) for line in (d / "decisions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
approved = [row for row in rows if row.get("final_gate") == "approved"]
ok = bool(approved) and approved[-1].get("approved_packet_sha256") == packet_hash
sys.exit(0 if ok else 1)
PY
rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "chief approval records current final packet hash"
printf '\nTampered packet sidecar.\n' >> "$TMP/matters/$SLUG/final_packet.md"
"$GLAW" stage file >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "file stage blocked by tampered final packet markdown"
"$CHIEF" --chief "GLAW Chief Counsel" --score 95 --grade A --decision "PROCEED" --risks "RF-0002 remains open as a nonblocking watch item" --conditions "licensed signer final review; RF-0002 carried until closed" --rationale "SRC-0001 all gates clear and source manifests tie out" --approve-final --matter "$SLUG" >/dev/null
"$GLAW" stage file >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && [ "$(cat "$TMP/matters/$SLUG/.stage")" = file ] && echo 1 || echo 0)" "file stage clears after final packet and chief approval"

"$GLAW" stage matter-retro >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "matter-retro blocked before docket gate"
"$GLAW" docket add 2026-09-15 "tax filing due - verify extension" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "docket add blocked without source-backed owner basis"
"$GLAW" docket add --owner "tax docket clerk" --source "SRC-9999 stale source" 2026-09-15 "tax filing due - verify extension" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "docket add blocked by non-current source evidence id"
"$GLAW" docket add --owner "tax docket clerk" --source "SRC-0001 filing calendar from intake source" 2026-09-15 "tax filing due - verify extension" >/dev/null
"$DOCKET" complete >/dev/null
"$GLAW" stage matter-retro >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && [ "$(cat "$TMP/matters/$SLUG/.stage")" = matter-retro ] && echo 1 || echo 0)" "matter-retro clears after docket gate"

"$GLAW" matter new "No Deadline Source Guard" >/dev/null
ND_SLUG="no-deadline-source-guard"
mkdir -p "$TMP/matters/$ND_SLUG/evidence"
printf 'source support\n' > "$TMP/matters/$ND_SLUG/evidence/source.txt"
"$DOCKET" no-deadlines --source "SRC-9999 stale source" --rationale "no filing deadlines in scoped review" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "no-deadlines blocked by non-current source evidence id"
"$DOCKET" no-deadlines --source "SRC-0001 current source" --rationale "no filing deadlines in scoped review" --reviewer "" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "no-deadlines blocked without accountable reviewer"
"$DOCKET" no-deadlines --source "SRC-0001 current source" --rationale "no filing deadlines in scoped review" >/dev/null
"$DOCKET" complete >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "no-deadlines completes with current source evidence id"

"$GLAW" matter new "Negative Finding Source Guard" >/dev/null
GUARD_SLUG="negative-finding-source-guard"
mkdir -p "$TMP/matters/$GUARD_SLUG/evidence"
printf 'negative finding source\n' > "$TMP/matters/$GUARD_SLUG/evidence/source.txt"
"$COUNCIL" record --profile accounting --role cfo --decision fix --red-flags "unsupported cash variance" --conditions "reconcile cash" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "council fix blocked without source-backed red flag"
"$COUNCIL" record --profile accounting --role cfo --decision fix --red-flags "SRC-0001 unsupported cash variance" --conditions "reconcile cash" >/dev/null
ok "$([ -f "$TMP/matters/$GUARD_SLUG/red_flags.jsonl" ] && grep -q '"source": "SRC-0001"' "$TMP/matters/$GUARD_SLUG/red_flags.jsonl" && grep -q '"origin": "council:accounting:cfo"' "$TMP/matters/$GUARD_SLUG/red_flags.jsonl" && echo 1 || echo 0)" "council fix opens source-backed red flag"
"$ADVERSARIAL" record --profile accounting --lens irs-examiner --decision fix --attack "return tie-out fails" --cure "reconcile tax return" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "adversarial fix blocked without source-backed attack"
"$ADVERSARIAL" record --profile accounting --lens irs-examiner --decision fix --attack "SRC-0001 return tie-out fails" --cure "reconcile tax return" >/dev/null
ok "$([ "$(grep -c 'red_flag_opened' "$TMP/matters/$GUARD_SLUG/timeline.jsonl")" -ge 2 ] && grep -q '"origin": "adversarial:accounting:irs-examiner"' "$TMP/matters/$GUARD_SLUG/red_flags.jsonl" && echo 1 || echo 0)" "adversarial fix opens source-backed red flag"

rm -rf "$TMP"
echo
echo "${fail:-0} failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }
