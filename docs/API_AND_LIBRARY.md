# GLAW Library and API Model

GLAW has one supported runtime model: local repository code plus standard-library execution.

## In-Repo Libraries

| Path | Role |
|---|---|
| `lib/bookkeeping/glaw_engine` | source-first bookkeeping and forensic engine |
| `lib/bookkeeping/glaw_engine/_compat` | local replacements for formerly external model/table/XML helpers |
| `docx/` | minimal local `python-docx`-style shim used by bundled workflows |
| `lib/federal-litigation` | federal causes and complaint support |
| `lib/render` | local rendering checks |
| `lib/writing` | legal-writing quality checks |
| `federal-trial-counsel/scripts/ftc_engine` | federal litigation CLI engine |

## External Package Policy

Do not add runtime dependencies. Specifically, do not add package manifests or install paths such as:

- `requirements.txt`
- `pyproject.toml`
- `package-lock.json`
- `npm install`
- `pip install`
- virtualenv bootstrap scripts

Former external package surfaces are handled locally:

| Former surface | Current behavior |
|---|---|
| pandas/pydantic/lxml | `lib/bookkeeping/glaw_engine/_compat` |
| python-docx | local `docx/` shim |
| docxtpl | stdlib DOCX template replacement |
| eyecite | stdlib citation extractor |
| juriscraper | local court list/handoff |
| jsonschema | small local schema validator |
| Google APIs | Google Sheets CSV export via stdlib URL reads; local CSV/JSON/HTML exports |
| reportlab/pypdf/PyPDF2 | local PDF/OCR binary orchestration, no Python PDF packages |

## API and Credential Behavior

GLAW does not require API keys for core operation.

Optional credentials may be used by operator-specific extensions, but the bundled app must work without them:

| API | Bundled default |
|---|---|
| Google Sheets | input supported through CSV export URL, no Google SDK |
| Google Docs/Drive | local export only |
| CourtListener | optional token for higher rate limits; local handoff still works |
| ProPublica nonprofit lookup | optional key if the user enables that workflow |
| OCR/PDF binaries | Python orchestrates rendering, OCR passes, parsing, and audit; local binaries perform text recognition |

## Adding a Library

1. Put code under `lib/` or the owning seat.
2. Use only Python standard-library imports or other in-repo modules.
3. Add a CLI smoke test if the library has user-facing behavior.
4. Add the module to `lib/firm-roster.md` if it owns a workflow.
5. Run `bin/glaw-test` and `bin/glaw-doctor`.

## Compatibility Contract

Local shims intentionally cover the subset used by GLAW, not full third-party APIs. When a workflow needs unsupported behavior, return a precise message naming the unsupported operation and the local output that was still produced.
