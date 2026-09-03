# GLAW Security and Reliability Evaluation Plan

## Automated suites

- Cross-tenant matrix: every read, retrieval, export, cache, vector, object, queue, and model-context path.
- Privilege and ethical-wall suite: unknown privilege defaults restrictive; direct and inherited relationships are tested.
- Prompt-injection suite: uploaded PDFs, OCR, email, web pages, and tool output containing fake system instructions.
- Malicious-document suite: malformed MIME, decompression bombs, macros, oversized files, duplicate hashes, and parser failures.
- External-effect suite: duplicate webhooks, timeout after submit, stale receipt, mismatched lookup, and replayed commands.
- Provider suite: timeout, 5xx, schema failure, model substitution, budget exceedance, and region denial.

## Release gates

1. Zero cross-tenant or privilege-leak failures.
2. Zero unauthorized consequential actions.
3. All high-risk benchmark packs meet their configured threshold.
4. Chaos runs leave no workflow in an unknown state without a reconciliation or incident record.
5. Signed audit export verifies from genesis through manifest.

Production requires an independent legal/security review and evidence of restored backups.
