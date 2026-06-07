# sec-enforcement-swarm

An 11-seat virtual SEC enforcement & securities-investigation division. Routes a matter to the
right specialist seat(s), runs them as a coordinated swarm, subjects every conclusion to an
adversarial RED→BLUE pass, and ships a court/SEC-ready deliverable with a full audit trail and
zero fabricated data.

## Invoke
`/sec-enforcement-swarm` — then describe the matter (a tip, a filing, a trade blotter, a Wells
Notice, a fact pattern). The skill picks the posture (investigative / defense / diligence),
routes to seats, and produces the deliverable.

## The 11 seats (`agents/`)
1. SEC Enforcement Attorney · 2. SEC Investigator · 3. Forensic Accountant ·
4. Market Manipulation Analyst · 5. Insider Trading Analyst · 6. FCPA Investigator ·
7. Whistleblower Analyst · 8. Litigation Support Specialist · 9. Expert Witness Report
Generator · 10. Wells Notice Response Generator · 11. 10-K/10-Q Risk Analyzer.

## References (`references/`)
- `orchestration.md` — swarm recipes per matter type + spawn/reconcile mechanics.
- `securities-law-map.md` — provisions and elements each seat proves (verify vs. primary law).
- `adversarial-protocol.md` — the RED→BLUE attack/rebuild protocol.
- `audit-trail-spec.md` — mandatory citation and audit-trail format.

## Guardrails
Analytical / litigation-support tool — **not legal advice**, no attorney–client relationship.
Zero hallucination: every fact cites a source or is marked `NOT IN RECORD`; every statute/case
cite must be verified against primary law. Licensed counsel must review before any filing.

## Related skills
`glaw-sec-enforcement`, `financial-forensics`, `forensic-case-investigator`, `institutional-finance`.
