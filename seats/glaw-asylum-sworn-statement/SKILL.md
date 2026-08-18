---
name: glaw-asylum-sworn-statement
version: 1.0.0
description: "GLAW evidence-controlled asylum declaration and witness reconstruction seat. Builds source-cited evidence registers, actor maps, chronologies, factual nexus and credible-fear maps, and attorney-ready sworn statements without inventing facts."
allowed-tools:
  - Skill
  - Agent
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - WebFetch
  - WebSearch
triggers:
  - asylum sworn statement
  - asylum declaration
  - credible fear
  - nexus analysis
  - asylum witness declarations
  - reconstruct asylum case
  - evidence-controlled affidavit
  - GLAW asylum
---

# GLAW Asylum Sworn Statement

This seat reconstructs asylum declarations and witness packets from a complete local evidence set. It is evidence development and attorney work product, not a guarantee of asylum eligibility and not a substitute for licensed immigration counsel.

## Governing discipline

Every material assertion must have a source label: `[PERSONAL MEMORY]`, `[DOCUMENT: filename/page]`, `[WITNESS: personal observation]`, `[ALLEGATION RECORDED]`, `[INFERENCE]`, or `[UNRESOLVED]`. Never invent facts or silently fix contradictions. Preserve adverse commercial, neighborhood, domestic, criminal, regulatory, and other alternative explanations. A complaint proves that a complaint was made; it does not automatically prove the underlying allegation.

## Mandatory outputs

1. Evidence register with paths, hashes when feasible, metadata, extraction status, duplicates, and missing attachments.
2. Cast/actor map with legal names, aliases, roles, affiliations, source of knowledge, and unresolved identity conflicts.
3. Source-cited master timeline with event date distinguished from document date.
4. Applicant sworn statement in the source language, with readable evidence references.
5. Exhibit index and contradiction log.
6. Factual nexus map: possible protected ground, supporting facts, alternative motives, missing evidence, and exact testimony.
7. Credible-fear fact map: subjective fear, past harm, objective basis, actor capability/inclination, nexus, government protection, internal relocation, and CAT facts.
8. Independent witness packet with personal observation separated from hearsay.
9. Red-team credibility report and attorney handoff checklist.

## Nexus and credible fear

Verify current law from official sources before drafting legal analysis:

- EOIR credible-fear guidance: https://www.justice.gov/eoir/policy-manual-eoir/part-II/icpm/chapter-6-4
- EOIR asylum/withholding/CAT overview: https://www.justice.gov/eoir/asylum-withholding-removal-convention-against-torture
- EOIR nexus precedent chart: https://www.justice.gov/eoir/bia-precedent-chart-ai-ca

Credible fear is a significant possibility of establishing asylum eligibility, not a grant. Nexus generally requires that a protected ground was or would be at least one central reason. The applicant should state facts and fear in first person; counsel should make the legal argument.

## Workflow

Search all nested case folders. Extract PDFs, DOCX, XLSX, images/OCR, forms, immigration records, official reports, witness files, drafts, and referenced-but-missing exhibits. Resolve actors only after comparing names and identifiers. Record competing dates and ages instead of selecting the convenient one.

Draft chronologically: identity; family/residence/work; political/community participation; conflict and alternative explanations; threats; principal incident; actors; government response; property and emotional effects; relocation; departure; current fear; contradictions; signature. Do not describe an arrest, kidnapping, political motive, threat author, nationwide reach, or current search unless personally known or documented.

Re-interview each witness independently before showing other statements. Require dates, location, reason for presence, what was seen/heard/done, what was told by the applicant, limits of knowledge, contact details, identity documents, signature, date, source-language version, and certified translation.

Run adversarial review against: inconsistent dates/ages, identity variants, alternative motives, partial documents, copied witnesses, government referrals or partial remedies, unsupported current fear, internal relocation, CAT, and filing/timeliness issues. A material unresolved conflict blocks signature.

## File-readiness gate

Return `FACT-INCOMPLETE`, `NEEDS-REINTERVIEW`, or `ATTORNEY-REVIEW REQUIRED` when a central identity, date, actor, motive, threat, current-risk, exhibit, translation, or witness-independence issue remains unresolved. Never label a declaration “bulletproof” merely because it is long or persuasive.

Final applicant confirmation under penalty of perjury, qualified translation/interpreter review, and licensed immigration-attorney signoff are mandatory before filing.
