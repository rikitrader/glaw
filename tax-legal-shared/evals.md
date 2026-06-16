# Shared Tax/Legal Evals

Use these checks when reviewing tax/legal workflow output:

- Does every numeric figure cite a `FIG-YYYY-####` entry from
  `current-figures.md`?
- Does every `FIG-YYYY-####` entry include `as_of`, `source_url`, and
  `verified_by`?
- Does the workpaper identify source bank statements, ledger rows,
  reconciliation status, and unresolved differences?
- For tax filing workflows, does `tax_tieout.status` equal `pass`, with
  `provision_ties=true` and `internal_consistency=true`?
- For external deliverables, is the UPL/work-product footer present?
- For filing, signature, service, payment, charge, or live transmission, did the
  human-authority gate record the authorizing actor?
