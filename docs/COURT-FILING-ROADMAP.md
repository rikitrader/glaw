# Court Case Creation and Filing Roadmap

Status date: 2026-08-13

GLAW can now route supported matters, assemble integrity-checked packets, and
produce supervised filing and service handoffs. It does not sign, file, serve,
transmit, pay a fee, or claim that a court accepted anything. Those acts remain
with a licensed attorney or other authorized human filer.

## Implemented now

| Capability | Coverage | Control |
|---|---|---|
| Federal subject-matter routing | Federal question and diversity | Federal claims require statute plus `SRC-####`; diversity recursively resolves individuals, corporations, LLC members, and partners and requires a supported amount over $75,000 |
| Federal national baseline | Civil Rules effective December 1, 2025 | Current official U.S. Courts/PACER authority pack |
| Federal local rules | Middle District of Florida | Verified November 1, 2025 Rule 3.01 limits and response periods; every other district returns `review` |
| Florida trial-court routing | All 67 counties and 20 circuits | Ordinary monetary civil only: small claims through $8,000, county civil through $50,000, circuit civil over $50,000 |
| Filing packet | Federal and Florida routed cases | Required gate artifacts and every filing PDF are SHA-256 checked; post-packet edits block handoff |
| Filing-day authority metadata gate | Federal core, M.D. Florida, and Florida trial-court packs | `bin/glaw-court-case authority-check` validates pack status, ISO review date, maximum age, and complete source metadata; packet preparation fails closed when the selected pack is stale or malformed |
| Filing handoff | CM/ECF or Florida Courts E-Filing Portal | Preparation-only operator checklist; live submit fails closed because no certified connector exists |
| Filing receipt | Human-filed matters | Records court, case number, filing time, actor, receipt artifact, and hashes |
| Service handoff and proof | Supported packets | Preparation-only handoff; actual proof starts a review-required candidate response date |
| Federal drafting metadata | FTC CLI | Unknown jurisdiction and nature-of-suit values remain blank with warnings; LLC citizenship follows members; answer timing is anchored to actual service when known |
| Word export | Local zero-dependency DOCX | Valid expanded package, 12-point Times New Roman defaults, double spacing, and one-inch baseline margins |

Run the implemented workflow:

```bash
bin/glaw-court-case route --input case.json --json
bin/glaw-court-case prepare --input case.json --output-dir filing --json
bin/glaw-court-case handoff --packet filing/court-filing-manifest.json --output filing/operator-handoff.json --json
bin/glaw-court-case record-receipt --packet filing/court-filing-manifest.json --receipt filing/receipt.json --actor "docket clerk" --json
bin/glaw-court-case service-handoff --packet filing/court-filing-manifest.json --output filing/service-handoff.json --json
bin/glaw-court-case record-service --packet filing/court-filing-manifest.json --proof filing/service.json --actor "docket clerk" --json
```

## Remaining coverage gaps

| Priority | Gap | Completion condition |
|---|---|---|
| P0 | Live filing-day authority refresh | The local metadata gate is implemented; remaining work is a controlled online refresh for rules, local rules, fees, forms, administrative procedures, judge orders, and portal notices, with unreachable sources blocking |
| P0 | Certified live connectors | Court-approved CM/ECF and Florida portal adapters, test-environment certification, least-privilege credentials, human preview/consent, idempotency, receipt capture, rollback/recovery, and independent security review |
| P0 | Exact official forms | Current fillable JS-44, AO 440, district/state summons, civil cover sheets, disclosure forms, accessibility, PDF/A where required, and byte-level validation against court rules |
| P0 | Deadline engine | Rule-specific triggering events, service methods, holidays, extensions, judge orders, tolling, relation back, removal/remand, and docket reconciliation; no deadline becomes final without docket-counsel review |
| P1 | Federal local packs | Current source-backed pack for the other 93 district courts plus bankruptcy and magistrate-specific workflows where authorized |
| P1 | State coverage | County/circuit/local packs for the other 49 states, D.C., and territories; clerk procedures, case types, fees, summons, exhibits, and service rules |
| P1 | Claim-element integration | Map all supported causes to current elements and defenses, require source-backed element-to-fact coverage, and eliminate all generic pleading text before final-packet approval |
| P1 | Service providers | Jurisdiction-specific authorized service methods, waiver workflows, process-server handoff, proof validation, failed-service escalation, and privacy controls |
| P2 | Specialized proceedings | Separate reviewed workflows for family, probate, juvenile, eviction, foreclosure, administrative appeals, extraordinary writs, class actions, sealed matters, multidistrict litigation, appellate, bankruptcy, and criminal matters |
| P2 | Operations | Role-based access, matter isolation, audit retention, incident response, disaster recovery, observability, SLA monitoring, and periodic legal/security recertification |

## Delivery sequence

1. Complete P0 authority-refresh and official-form validation before enabling any
   new court pack for production reliance.
2. Pilot one additional federal district and one Florida county with local
   counsel, using sandbox filings and documented acceptance cases.
3. Certify connector controls independently; keep production transmission off
   until court terms, credentials, consent, security, and receipt reconciliation
   all pass.
4. Expand district/state packs in measured cohorts, with regression fixtures for
   every court and a named owner plus review date on every authority source.
5. Add specialized proceedings only as separate schemas and gates; do not infer
   them from the ordinary-civil router.

The roadmap is complete when every supported forum has current primary-source
authority, tested forms and rules, supervised human approval, immutable receipts,
service and docket reconciliation, security certification, and a documented
fail-closed response for every missing or stale input.
