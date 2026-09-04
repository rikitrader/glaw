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

The FP&A extension `bin/glaw-fpa-engine` covers annual budgets, multi-year plans,
actual-versus-budget variance, rolling driver forecasts, bookings/pipeline
coverage, headcount pacing, CapEx payback and prioritization, and segment
profitability. It remains a controlled reference model: the CFO, FP&A owner,
business owner, and controller approve before management or external use.
