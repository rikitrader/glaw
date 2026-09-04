# GLAW Release Evidence Index

| Artifact | Command | Status |
| --- | --- | --- |
| Restore replay | `node evals/operations/restore-test.mjs` | local executable |
| Load baseline | `node evals/operations/load-report.mjs` | local baseline, not production load |
| Chaos disposition | `node evals/operations/chaos-report.mjs` | local executable |
| SIEM redaction | `node evals/operations/siem-trace-evidence.mjs` | local redaction evidence; collector pending |
| Rollback rehearsal | `node evals/operations/rollback-rehearsal.mjs` | local no-side-effect rehearsal |
| Security review | `docs/reviews/SECURITY_REVIEW_PACKET.md` | independent reviewer pending |
| Legal review | `docs/reviews/LEGAL_REVIEW_PACKET.md` | independent reviewer pending |
