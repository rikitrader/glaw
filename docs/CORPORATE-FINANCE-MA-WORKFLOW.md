# Corporate Finance & M&A execution workflow

`bin/glaw-corporate-finance` is the controlled reference lane for valuation,
planning, transaction, and capital-allocation analysis. It standardizes the
handoff across the finance department:

```text
Intake / sources -> three-statement model -> DCF + trading comps + transaction comps
-> merger / accretion-dilution -> cap table / equity waterfall -> reconciliation
-> sensitivity + adversarial review -> REVIEW (human approval) / BLOCK
-> board, tax, legal, accounting, and registry workpapers
```

The pipeline is deterministic and local. It is an independent reasonableness
check against approved models, not a replacement for banker, accountant, tax,
legal, board, or investment-committee judgment. Material outputs must be
registered through the enterprise artifact registry before final-packet release.

Required controls are source/version/unit preservation, cash and balance-sheet
reconciliation, DCF WACC/growth sensitivity, disclosure of missing inputs, and
qualified human approval. Failed conservation or reconciliation checks block
release.
