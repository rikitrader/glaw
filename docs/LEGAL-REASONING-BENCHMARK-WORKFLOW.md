# Legal Reasoning Benchmark Department

## Canonical workflow

```text
Domain + jurisdiction intake
        ↓
Original question and fact-pattern design
        ↓
Medium / Hard / Expert difficulty rating
        ↓
1 correct answer + 9 plausible distractors
        ↓
Concise stepwise rationale + 1–5 authority/academic references
        ↓
Adversarial ambiguity, authority, distractor, and solvability review
        ↓
Senior-lawyer criterion rubric + human attorney review
        ↓
PASS / REVIEW / BLOCK
```

The covered domains are IP/privacy/technology, regulatory/government affairs, securities/capital
markets, financial regulation/compliance, private equity/M&A/transaction structuring, antitrust and
merger control, healthcare/life sciences/pharmaceuticals, and environmental/energy/ESG/climate.

Each artifact must preserve the jurisdiction, governing law, effective date, source ledger, fact
assumptions, difficulty, answer key, distractor rationale, references, red-team findings, and human
review status. Questions must be unambiguous and self-contained. Verification tasks must state the
defect and justify every edit.

## Senior-lawyer rubric

| Criterion | 0–1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Doctrine and authority | wrong/unsupported | rule stated | rule applied | controlling and contrary authority weighed |
| Facts and precision | material omissions | mostly defined | complete | operationally exact and date-aware |
| Reasoning | recall only | partial application | coherent application | exceptions, counterarguments, and judgment |
| Answer set | obvious/overlap | weak distractors | plausible | nine alternatives fail for distinct expert reasons |
| Practical judgment | no consequence | generic caveat | identifies impact | prioritizes risk, remedy, escalation, and implementation |
| References | absent | weak | relevant | authoritative, traceable, and proposition-matched |

Any material ambiguity, fabricated authority, jurisdiction mismatch, or unsupported unique answer is
`BLOCK`. A defensible but unsettled issue is `REVIEW`, not silently forced into a false certainty.
