# Florida Quantum Meruit Litigation Agent — COMPLETE DOCUMENT LIBRARY

This agent reuses the **federal-trial-counsel template library** (symlinked here as
`federal-library/` and `federal-references/`) as its motion/discovery/pleading engine,
and overlays **Florida state-court adaptations** + the **quantum-meruit-specific
documents** the federal set lacks.

## How to adapt a federal-library template to Florida state court
When you pull any `federal-library/...` template, convert it:
- **Caption** → "IN THE CIRCUIT COURT OF THE [Nth] JUDICIAL CIRCUIT IN AND FOR [COUNTY] COUNTY, FLORIDA".
- **Rules** → Fla. R. Civ. P. (not FRCP): pleading **1.110**; MTD **1.140**; discovery
  **1.280**; interrogatories **1.340** (≤30); production **1.350**; admissions **1.370**;
  depositions **1.310**; summary judgment **1.510** (FL adopted the federal *Celotex*
  standard eff. 2021); amendment **1.190**; default **1.500**; sanctions **1.380**;
  voluntary dismissal **1.420**; lis pendens **§ 48.23**; proposal for settlement
  **§ 768.79 / Rule 1.442**; offer of judgment.
- **Standard cites** → Florida (e.g., MSJ: *In re Amends. to Fla. R. Civ. P. 1.510*,
  309 So. 3d 192 (Fla. 2020)). Verify all via `/glaw-legal-research`.
- **Signature/service** → Florida e-filing (Florida Courts E-Filing Portal), e-service
  per Rule 2.516; Certificate of Service required.

---

## 1. SUITS / PLEADINGS
| Document | Source |
|---|---|
| **Complaint — Quantum Meruit + Unjust Enrichment** (FL) | `01-complaint-qm-ue.md` *(this folder)* |
| Per-property **Homeowner + GC** complaint (bucket-split) | `/glaw-recover-payment` → `recover-payment/templates/complaint-ho-and-gc-florida.md` |
| Generic / multi-count money complaint (breach, account stated, lien) | `recover-payment/templates/complaint-florida.md` |
| Complaint (structure reference) · Amended · Counterclaim/Crossclaim · Third-party · Answer | `federal-library/pleadings/` (adapt to FL) |
| Federal **RICO** complaint (60+ jobs / fraud pattern) | `glaw-federal-trial-counsel` + `federal-library/pleadings/complaint_federal.md` + pleading engine |

## 2. SUMMONS & SERVICE
| Document | Source |
|---|---|
| Summons + service instructions + return of service | `02-summons-service.md` *(this folder)* |

## 3. DISCOVERY (full package)
| Document | Source |
|---|---|
| **Request for Production (Rule 1.350)** — QM-tailored | `03a-request-for-production.md` *(this folder)* |
| **Interrogatories (≤30, Rule 1.340)** — QM-tailored | `03b-interrogatories.md` *(this folder)* |
| **Requests for Admission (Rule 1.370)** — QM-tailored | `03c-requests-for-admission.md` *(this folder)* |
| ↳ broader/oppositional discovery (depo, subpoena, expert, responses) | `federal-library/discovery/*.md` (adapt) + `recover-payment` GC/HO sets |
| Notice of Deposition (Rule 1.310) | `federal-library/discovery/deposition_notice.md` (adapt) |
| Subpoena duces tecum to non-party (carrier/lender/bank) | `federal-library/discovery/subpoena_third_party.md` (adapt) |
| Notice of Deposition (Rule 1.310) | `federal-library/discovery/deposition_notice.md` (adapt) |
| Subpoena duces tecum to non-party (carrier/lender/bank) | `federal-library/discovery/subpoena_third_party.md` (adapt) |
| Expert disclosure (Rule 1.280(b)) | `federal-library/discovery/expert_disclosure.md` (adapt) |
| Responses/objections to opposing discovery | `federal-library/discovery/discovery_response_template.md` |
| Rule 1.280 initial disclosures (FL 2025 disclosure regime — verify) | `federal-library/discovery/initial_disclosures.md` (adapt) |

## 4. MOTIONS (complete library — adapt FRCP→Fla. R. Civ. P.)
| Motion | Source |
|---|---|
| **Final Summary Judgment** (Rule 1.510) | `04-motion-summary-judgment.md` *(this folder, FL)* + `federal-library/motions/summary_judgment.md` |
| MSJ supporting **Affidavit/Declaration** | `05-msj-affidavit.md` *(this folder)* |
| Opposition to Motion to Dismiss | `federal-library/motions/opposition_to_mtd.md` |
| Motion to Dismiss (if defending a counterclaim) | `federal-library/motions/motion_to_dismiss.md` |
| Motion for **Default** + Default Final Judgment | `federal-library/motions/motion_for_default_judgment.md` |
| Motion to **Compel** discovery + sanctions (Rule 1.380) | `federal-library/motions/motion_to_compel.md` |
| Motion for **Sanctions** | `federal-library/motions/motion_for_sanctions.md` |
| Motion in **Limine** | `federal-library/motions/motions_in_limine.md` |
| Motion to **Amend** (Rule 1.190) | `federal-library/motions/motion_to_amend.md` |
| Motion for **Protective Order** | `federal-library/motions/motion_for_protective_order.md` |
| Reply brief | `federal-library/motions/reply_brief.md` |
| Post-trial motions (new trial / rehearing) | `federal-library/motions/post_trial_motions.md` |
| TRO / Preliminary Injunction (asset freeze) | `federal-library/motions/tro_motion.md`, `preliminary_injunction.md` |
| Opposition to opposing SJ | `federal-library/motions/opposition_to_sj.md` |

## 5. PROPOSED ORDERS
All in `federal-library/orders/` — MTD, SJ, compel, sanctions, scheduling, consent,
TRO, PI. Pair one with every motion (FL judges expect a proposed order).

## 6. PRETRIAL / TRIAL / JUDGMENT
| Document | Source |
|---|---|
| **Trial Brief** (bench or jury) | `06-trial-brief.md` *(this folder)* |
| **Damages Calculation Worksheet** | `07-damages-worksheet.md` *(this folder)* — or `bin/glaw-qm damages` |
| **Proposed Final Judgment** | `08-final-judgment.md` *(this folder)* |
| Witness & exhibit lists, trial prep workflow | `federal-library/workflows/trial_preparation_workflow.md` |

## 7. SETTLEMENT / LEVERAGE
| Document | Source |
|---|---|
| **Settlement Demand Letter** | `09-settlement-demand.md` *(this folder)* |
| **Proposal for Settlement** (§ 768.79 / Rule 1.442 — fee-shifting) | `10-proposal-for-settlement.md` *(this folder)* |
| Leverage score (0–100) + strategy | `bin/glaw-qm leverage` |

## 8. CONSTRUCTION-LIEN ADD-ONS (if requested)
| Document | Source |
|---|---|
| **Notice of Lis Pendens** (§ 48.23) | `11-lis-pendens.md` *(this folder)* |
| Claim of Lien / NTO / lien foreclosure count | `/glaw-recover-payment` (Ch. 713 workflow) |

## 9. CLAIM ENGINE (for "any other sue")
`~/.claude/skills/federal-trial-counsel/scripts/federal_pleading_engine` — 40+ causes of action with
elements, fact-to-element mapping, Rule 9(b) detection, and MTD risk scoring (incl.
RICO, conversion, fraud). Use it to draft/score companion federal counts; route to
`glaw-federal-trial-counsel`.

## REFERENCES (the "system")
`federal-references/` — `frcp_summary.md`, `fre_summary.md`, `mdfl_local_rules.md`,
`eleventh_circuit_standards.md`, `federal_litigation_engines.md`, `case_strategy_system.md`.
For Florida-state specifics, layer the rule conversions at the top of this file.

> Every external deliverable carries the UPL/work-product footer (`/glaw-ethics-conflicts`).
> Attorney work-product — verify all cites; not legal advice.


## 9. TITLE VI LIBRARY (full Florida Civil Practice & Procedure)
Index DB of all 36 Title VI chapters + a pleadable skeleton for every cause of action. Query:
`glaw-fl-statute list | causes | chapter <N> | search <term>`.
| Document | Source |
|---|---|
| Index DB (all chapters, kinds, key sections) | `../lib/fl-title6-index.json` |
| Cause-of-action catalog (replevin, ejectment, quiet title, partition, declaratory, injunction, lost instrument, dishonored check, statutory lien, attachment, garnishment, proceedings supplementary, eviction, unlawful detainer) | `title6/causes-of-action-catalog.md` |
| Master intake + claim routing | `title6/intake-questions.md` |
| Cross-action discovery set (RFP/Rogs/RFA) | `title6/discovery-set.md` |
| Subpoena pack (trial/deposition/duces tecum party + non-party, Rule 1.410/1.351) | `title6/subpoenas.md` |
| ↳ dedicated ready-to-file complaints | `title6/complaint-statutory-lien-foreclosure.md`, `complaint-replevin.md`, `complaint-quiet-title.md`, `complaint-declaratory-judgment.md`, `complaint-ejectment.md`, `complaint-reestablish-lost-instrument.md` |
| ↳ judgment-enforcement pack | `title6/enforcement-proceedings-supplementary.md` (§56.29 — verified), `enforcement-garnishment.md` (Ch.77) |


## 10. FLORIDA CAUSES LIBRARY (110 causes + legal standards)
Query: `glaw-fl-cause list | category <c> | show <name> | search <t> | standards | sol <yr>`.
| Document | Source |
|---|---|
| Index DB (110 causes — elements/SOL/defenses/authority + standards) | `../lib/fl-causes-index.json` |
| Common-causes catalog (pleadable skeletons) | `causes/common-causes-catalog.md` |
| Legal-standards motion pack (MTD/MSJ 1.510/DV/JNOV/Daubert/punitive) | `causes/motions-legal-standards.md` |
| Dedicated complaints (≈30, covering all 110 causes) | `causes/complaint-*.md` — contract/common-counts/note/warranty; equity (unjust enrichment, rescission, specific performance, trusts/accounting/indemnity); business (fiduciary duty, tortious interference, conspiracy); intentional torts (assault/battery, defamation, malicious prosecution/abuse of process, IIED, trespass/nuisance, invasion of privacy); negligence (general, hiring/retention/security, malpractice, products liability, wrongful death, NIED); statutory (FDUTPA, FCCPA, civil theft, usury); + misc (consortium, joint venture, way of necessity, building code, wrongful birth) |
| § 772.11 civil-theft pre-suit demand | `causes/demand-civil-theft.md` |
