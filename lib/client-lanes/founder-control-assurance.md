# Founder Control Assurance Lane

This lane is the event-driven assurance layer for the Founder Control Stack. It
is additive to the corporation, VC/PE, fund, tax, accounting, SEC, and UHNW
lanes. It produces attorney/CPA work-product scaffolding and never signs,
files, transmits, pays, or binds without a human seal.

## Required assurance sequence

1. Capture the proposed transaction and source evidence.
2. Reconcile the legal cap table, fully diluted denominator, transfer ledger,
   equity compensation, preferred/convertible instruments, and total voting
   universe.
3. Run `bin/glaw-founder-control` and preserve the input/output digest.
4. Check the 5.01% economic threshold and greater-than-50.1% voting floor.
5. Review dilution, transfer, conversion, fiduciary, related-party, accounting,
   tax, disclosure, and investor-document consequences.
6. Record exceptions, cure steps, responsible owner, and deadline.
7. Obtain Delaware counsel, accounting, tax, and Chief/Council review where
   applicable.
8. Refresh the CourtListener/Delaware authority index, confirm the controlling
   appellate disposition, map the correct court and remedy, and preserve adverse
   authority for each control provision.
9. Issue the Control Assurance Certificate and docket recurring monitoring.

## Event triggers

Financing, equity issuance, option-pool change, SAFE or note conversion,
preferred conversion, Class B transfer, founder trust or estate change, board
change, board-size change, merger, acquisition, reorganization, subsidiary
transaction, public offering, investor protective-provision amendment, and any
threshold or voting-universe change.

## Control certificate outputs

- Fully diluted economic ownership calculation.
- Total voting-universe reconciliation.
- Founder voting-power calculation and sensitivity.
- Document-precedence and amendment-conflict result.
- Current authority and jurisdiction/forum index review, including adverse cases,
  facial versus as-applied posture, and current appellate treatment.
- Fiduciary and independent-process determination.
- Accounting, tax, valuation, and disclosure handoff.
- Exceptions, evidence hashes, reviewers, human seal, and docket entries.

## Three-lawyer-review firewall

Every founder-control event must answer three separate questions before it is
file-ready:

1. **Mandatory law:** Is the provision permitted by the current DGCL, the
   certificate, securities law, exchange rules, tax/insolvency law, and any
   required class or stockholder vote?
2. **Fiduciary process:** Who acted in which capacity, was there a controller or
   conflict, what independent process was used, and is the record defensible under
   the applicable standard of review?
3. **Judicial review:** Which court can hear the claim, what remedy is available,
   is the issue facial or as-applied, and has a later appellate decision changed
   the rule?

The machine-readable authority index is
`founder-control-stack/case-law-jurisdiction-index.json`. Its 2026 refresh must
be treated as a current-law snapshot, not a substitute for Delaware counsel.
