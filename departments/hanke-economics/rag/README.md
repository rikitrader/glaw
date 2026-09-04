# Source intake and publication-by-publication protocol

The registry intentionally starts empty. That is a safety feature: an unverified title, quotation, page, or dataset is worse than an explicit gap.

For each publication, create exactly one `SourceRecord`, then advance it through:

`KNOWN → FOUND → INGESTED → INDEXED → VERIFIED`

or mark `MISSING`/`RESTRICTED` with a reason. Keep duplicate versions linked, retain lawful-access notes, and never copy a copyrighted full book without lawful access. A source is eligible for a direct Hanke claim only after authorship, source status, quotation/paraphrase, context, date, and citation anchor pass the citation audit.

Required publication intake fields are defined in `schemas/source-record.schema.json`. No placeholder source is treated as evidence.
## Lawful source acquisition

Acquire one indexed public source at a time:

```sh
npm run source:acquire -- DOC-ID
```

The command reads only `rag/document-index.json`, requires HTTPS through the
retrieval boundary, stores successful PDF/HTML bytes under
`documents/acquired/`, and appends an attempt record to
`rag/acquisition-attempts.jsonl`. A successful acquisition remains `FOUND`; the
command never changes the document index or creates `VERIFIED` evidence.

Do not use it for copyrighted full books unless lawful access exists. Restricted,
anti-bot, insecure, and unsupported responses are recorded without storing their
body.

To process the entire current index sequentially, run:

```sh
npm run source:acquire-all
```

The batch command writes `rag/acquisition-batch-summary.json`, exits non-zero if
any indexed source is missing or restricted, and never changes a document to
`VERIFIED`.
