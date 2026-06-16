# GLAW Toolbelt — CLI Reference

The firm's reasoning lives in markdown skills; its deterministic work lives in source-only
CLIs under [`../bin/`](../bin/). The toolbelt is source-first and zero third-party package:
no `pip install`, no `npm install`, no virtualenv bootstrap, and no remote package fetch.
Tools use bash, Python 3, repository libraries, and the Python standard library.

Run any tool with no arguments for its usage. `bin/glaw-doctor` smoke-tests them all.

## State & ops
| Tool | Usage |
|---|---|
| `glaw` | `matter new "<name>"` · `matter list` · `matter use <slug>` · `stage <stage>` · `docket add --owner <owner> --source "SRC-0001 <basis>" <YYYY-MM-DD> "<desc>"` (source must be current matter evidence) · `docket upcoming [days]` · `timeline-log <event>` · `config get/set <k> [v]`; `stage strategy` revalidates complete intake plus current-source conflicts and engagement artifacts |
| `glaw-headless` | `--goal "<objective>" [--matter SLUG] [--json]`; read-only spawned/orchestrator report with matter, stage, track, loop decision, open gates, next owner/command, final-packet summary, compliance manifest, normalized `compliance_action_plan` rows (`id`, `owner`, `next_command`, `required_fix`, `missing`), government-adversary manifest, accounting-control manifest/failures for bank reconciliation and tax tie-out routing, decisions, artifacts, and human-seal boundary. `glaw --headless --goal ...` delegates here |
| `glaw-daemon` | `status [--json]` · `goal add --name NAME --objective TEXT [--kind docket-watch\|matter-loop] [--horizon-days N]` · `goal list [--json]` · `goal disable --name NAME` · `once [--json] [--horizon-days N]`; source-only standing-goal/docket watcher. It scans all matters, surfaces missed/upcoming deadlines, records `$GLAW_HOME/daemon/runs.jsonl`, routes via `glaw-loop`, and stops while the oversight kill-switch is active |
| `glaw-sandbox` | `list [--json]` · `run [--scenario all\|NAME] [--json]`; source-only isolated simulation runner. It creates temporary `$GLAW_HOME` fixtures and proves fail-closed behavior for conscience human-only acts, Oversight Board kill-switch, daemon deadline routing, jurisdiction pack failures, reviewer profile-map consistency, government/regulatory/litigation adversary coverage, final-packet government-adversary failures routing back to `/glaw-adversarial`, Fortune 500 accounting-control priority for bank reconciliation/tax tie-out blockers, SEC/PCAOB tabletop routing for failed audit-reviewer attacks, citation-grounding failures routing to `/glaw-legal-research`, red-flag accountability failures routing to `/glaw-red-flags`, and professional report-quality failures routing through compliance/final-packet repair |
| `glaw-docket-gate` | `status` · `complete` after owned/source-backed deadlines are docketed; docket and no-deadline sources must cite a current source artifact ID; `no-deadlines --source "SRC-0001 <basis>" --rationale <why>` for explicit no-deadline close-out |
| `glaw-intake` | `init [slug] --track <track>` · `set <field> <value>` · `status` · `complete --by "<named reviewer>"` · `show`; strategy and file gates revalidate the current structured `intake.json`, including universal fields, track-specific fields, and a named accountable intake reviewer |
| `glaw-ethics` | `record-conflicts --status cleared\|waived\|conflict --source "SRC-0001 <basis>"` · `draft-engagement --responsible-professional "<named licensed reviewer>" --source "SRC-0001 <basis>"` · `status` · `complete`; conflicts, waiver evidence, and engagement sources must cite current matter source artifacts, the responsible professional must be a named accountable reviewer rather than a generic placeholder, and `conflicts_cleared` logs only after source-backed conflicts and engagement are ready |
| `glaw-council` | `record --profile auto --role <lens> --decision approve\|fix\|deny` · `status` · `complete`; `approve` requires source-backed `--evidence` plus role-specific `--notes`, the cited `SRC-####` must resolve to a current matter source artifact, `fix/deny` red flags must cite `SRC-####`, `fix` requires `--conditions`, generated red flags store the current source ID in `source` and the reviewer path in `origin`, and every required role must approve before final packet |
| `glaw-adversarial` | `record --profile auto --lens <government/regulatory lens> --decision survive\|fix\|strike` · `status` · `complete`; `survive` requires source-backed `--evidence` plus a source-cited `--attack` challenge summary, the cited `SRC-####` values must resolve to current matter source artifacts, `fix/strike` attacks must cite `SRC-####`, `fix` requires `--cure`, generated red flags store the current source ID in `source` and the RED-team reviewer path in `origin`, and `adversarial_done` logs only when every required RED-team lens survives |
| `glaw-red-flags` | `add --severity critical\|high\|medium\|low --source "SRC-0001 <basis>" ...` · `resolve <id> --evidence "SRC-0001 <fix support>"` · `status` · `complete` · `list`; add and resolution evidence must cite a current source artifact ID from `evidence/`, `sources/`, or `source_documents/`, and `complete` refuses stale critical/high closures. Open medium/low flags are nonblocking only when the final packet carries them with owner, required fix, finding, and a current `SRC-####` source. |
| `glaw-upl-check` | `<matter-slug-or-dir>` → fail-closed check that text deliverables carry attorney-work-product / not-legal-advice footer language |
| `glaw-citation-corpus` | `capture --id <id> --source-url <allowlisted-url> (--text <text>\|--file <path> --authenticated-copy\|--fetch) [--segment <text>]` · `status`; rejects off-allowlist legal source URLs, records pasted `--text` as untrusted, treats `--fetch` from approved sources as authoritative, treats `--file --authenticated-copy` from approved URLs as an offline official copy, and stores source/segment SHA-256 hashes in the matter corpus ledger. Verified citations cannot rely on untrusted pasted text |
| `glaw-citation-gate` | `record --id <id> --proposition ... --authority ... --status verified --support-summary ... --corpus-id <id> --source-url https://... --reviewer legal-research` · failed rows require `--defect-type incorrect\|misgrounded\|ungrounded\|incomplete` · `status` · `complete`; logs `citations_verified` only when every latest citation row is verified with proposition, authority, support summary, corpus source/segment hashes, the legal-research reviewer, and a valid HTTP(S) source URL |
| `glaw-groundedness` | `audit [--matter <slug>] [--json]` → fail-closed deterministic lexical floor for verified citation propositions against trusted corpus segments; writes `groundedness.json`, reports entity-grounding plus relation-preservation metrics, blocks untrusted pasted corpus rows, and does not claim semantic Shepardizing or HalluGraph proof |
| `glaw-final-packet` | `build --profile auto` → `final_packet.json` + `final_packet.md`; logs `final_packet_ready` only when gates are clear, at least one external text deliverable exists, every external report includes `Owner:`, `Report voice:`, `Findings:`, `Evidence:`, `Red flags:`, and `Sign-off conditions:`, has no unresolved bracket placeholders such as `[VERIFY]` and no unresolved `REVIEW:` markers, the report plus required council/adversarial reviews and resolved critical/high red flags cite hashed nonempty source files such as `SRC-0001` from `evidence/`, `sources/`, or `source_documents/`, every packet carries a current `government_adversary_manifest` proving at least one government/regulatory/litigation attack lens with source-cited evidence and challenge text, every packet also carries a self-routing `compliance_manifest` tying ethics/UPL, citations, adversaries, red flags, source evidence, report quality, reviewer identity, and accounting controls into one file-readiness compliance record with `owner`, `next_command`, and `required_fix` per row, open medium/low red flags are owner-assigned, fix-described, source-backed, and hashed into the packet manifest, the citation verifier plus every required reviewer/lens resolves to a hashed GLAW skill identity file, accounting/accounting-tax/tax/SEC-reporting profiles include a passing `accounting_control.json` proving books-doctor, bank reconciliation, and tax tie-out controls where applicable, and the markdown packet digest matches `final_packet.json` |
| `glaw-accounting-control` | `--source "SRC-0001 <basis>" --ledger ledger.json --bank-rec bank_rec.json [--profile accounting\|accounting-tax\|tax\|sec-reporting] [--tax-tieout tax_tieout.json]` → runs strict books-doctor, copies workpapers, validates clean bank reconciliation and tax tie-out for accounting-tax/tax profiles, and writes `accounting_control.json` |
| `glaw-host` | `manifest [--json]` · `status [--json]` · `execute --tool glaw --args '["version"]' [--matter SLUG] [--role READER\|WRITER\|ADMIN\|AUDITOR] [--actor NAME] [--json]`; source-only host adapter for zeroclaw/MCP-style runtimes. It exposes a tool manifest, accepts argv arrays only, blocks path traversal and shell strings, enforces RBAC at the host boundary, wraps executions in `glaw-conscience` pre/post guards, and preserves RBAC ADMIN for human-seal acts |
| `glaw-mcp` | `tools [--json]` · `call glaw_manifest\|glaw_status\|glaw_execute --arguments '<json>' [--json]` · `serve`; source-only MCP-style JSON-RPC bridge over `glaw-host`, exposing only manifest/status/guarded execute and no raw shell. `glaw_execute` arguments include `role` and `actor` so MCP calls inherit host RBAC enforcement |
| `glaw-extism` | `tool_metadata [--json]` · `execute --payload '{"tool":"glaw","args":["version"],"role":"READER","actor":"Extism Reader"}' [--json]`; source-only zeroclaw/Extism plugin contract shim exporting `tool_metadata` and `execute`, delegating to `glaw-host`, denying hardware authority, and preserving host RBAC plus conscience gates |
| `glaw-constitution-score` | `scaffold` · `<input.json> [--json]`; deterministic constitutional-risk matrix for public-law matters. It classifies scrutiny tier, source support, tailoring/nexus gaps, adversarial lenses, and human-authority blockers. It does not issue rulings or replace citation verification |
| `glaw-jurisdiction-pack` | `scaffold` · `list` · `validate <pack.json> [--json]`; deterministic state/federal/international jurisdiction matrix gate. It requires source-backed governing-law, forum, tax, licensing, filing, deadline, and government/adversarial-lens coverage before a cross-jurisdiction answer is treated as portable. Bundled packs include `us-core.json` and `us-fortune500-tax-sec.json` |
| `glaw-oversight` | `status [--json]` · `halt --by NAME --reason TEXT` · `resume --by NAME --role ADMIN --reason TEXT` · `escalate --matter SLUG --reason TEXT [--source SRC-0001]` · `decision --matter SLUG --decision approve\|fix\|deny\|halt --by NAME --role ADMIN --reason TEXT [--source SRC-0001]` · `policy [--json]` · `validate-policy [--path PATH] [--json]`; global kill-switch plus Oversight Board ledger and source-controlled policy pack. `glaw-loop` stops routing while halted and records non-convergence escalations here |
| `glaw-rbac` | `check --operation read\|write\|audit\|admin\|human_authority --role READER\|WRITER\|ADMIN\|AUDITOR --actor NAME [--json]` · `roles` · `audit`; enforces execution rings with SOC2 control IDs and writes hash-chained audit rows to `$GLAW_HOME/audit/rbac.jsonl` |
| `glaw-authority` | `check <file\|serve\|sign\|transmit\|charge\|pay\|submit-live> [--human-authority "<name/role>"] [--role ADMIN]` → fail-closed human-authority gate for acts GLAW may prepare but not autonomously commit; human-seal acts require RBAC ADMIN and write SOC2-mapped audit rows |
| `glaw-conscience` | `check-call --command "<command>" [--matter <slug>] [--json]` · `check-response [--text "<text>"] [--matter <slug>] [--json]` → autonomous pre/post guardrail; blocks destructive shell calls, hand-logged reserved gate events, live filings or human-only actions without authority, unresolved placeholders, unsupported human-act claims, and high-stakes legal/tax/accounting/final output without `SRC-####` |
| `glaw-loop` | `status [--matter <slug>] [--json] [--max-iterations N]` · `once [--matter <slug>] [--json] [--max-iterations N] [--acceptance TEXT] [--request-action <human-only-action>]` → Chief routing loop that inspects current gate state, names the owning department and next command, lists required Council/adversarial profiles, exposes blocked final-packet compliance rows in `compliance_failures` plus normalized `compliance_action_plan` rows (`id`, `owner`, `next_command`, `required_fix`, `missing`), routes accounting-control rows to `glaw-accounting-control`, government-adversary rows to `/glaw-adversarial`, citation rows to `/glaw-legal-research`, red-flag rows to `/glaw-red-flags`, and general manifest defects to `/glaw-compliance`, checks owner/command/reason/authority-boundary/conscience acceptance criteria, writes `loop_decisions.jsonl` on `once`, stops while the oversight kill-switch is active, records non-convergence in `glaw-oversight`, and refuses filing/signature/service/payment/charge/live-transmission authority |
| `glaw-learnings` | `add '<json>'` · `preflight [matter] [--query TEXT] [--track TRACK]` · `query "<query>" [--json] [--limit N] [--matter M] [--type T] [--track TRACK]` · `stats`; source-linked long-term memory store under `$GLAW_HOME/learnings/learnings.jsonl` with ranked selective retrieval and workflow-track weighting |
| `glaw-reflect` | `[--apply]` → synthesizes source-linked knowledge rules from repeated `glaw-learnings` defects and writes them back to the same isolated memory store |
| `glaw-setup` | deploy every sub-skill as a `/glaw-*` command (symlink model) |
| `glaw-policy` | `check [--root PATH] [--json]` → fail-closed policy contract: CI must run doctor/bookkeeping/policy gates, doctor must include required tests/tool smokes, hooks must run the commit gate, and file/final-packet gates must carry required artifacts |
| `glaw-doctor` | health harness: skills resolve · tools run · no dangling refs · profile reviewer-map consistency · Codex/Claude parity · no weak review-gate examples → `HEALTHY`/`PROBLEMS` |
| `glaw-preamble.sh` | shared preamble emitted by each stage skill |

## Contract-review chain
| Tool | Usage |
|---|---|
| `glaw-contract-score` | `scaffold` · `<findings.json>` → scorecard (risk 0–100, tier, grade A–F, red-flag card). Severity 🔴critical/🟡important/🟢acceptable. |
| `glaw-redline` | `annotate <contract> <findings.json>` → highlighted HTML + comments · `decide <file> <id> accept\|deny` · `status <file>` |
| `glaw-redline-docx` | `<contract.docx> <findings.json> [-o base]` → local normalized redline JSON plus replacement DOCX |
| `glaw-review-chain` | `<contract.docx> <findings.json> --matter <slug>` → one-shot local scorecard, redline artifact, and publish bundle |

`findings.json` (the shared shape): `[{ "id","quote","severity","issue","suggestion" }]`.

## Documents & research
| Tool | Usage |
|---|---|
| `glaw-doc-extract` | `<file\|dir> [-o out]` → text + metadata for local text/DOCX inputs; PDFs use local binaries when installed |
| `glaw-cites` | `<file>` or `-` (stdin) `[--json]` → extracted/normalized citations (stdlib citation extractor) |
| `glaw-court-scrape` | `--list [filter]` · `<court_id>` → dockets/opinions (zero-dependency court handoff, 300+ courts + PACER) |
| `glaw-assemble` | `vars <template.docx>` · `<template.docx> <data.json> -o out.docx` using stdlib DOCX merge |
| `glaw-publish` | `<matter-slug\|dir> [--folder NAME] [--local-only]` → local HTML/manifest publish bundle in the house style |

## Tax & regulatory
| Tool | Usage |
|---|---|
| `glaw-tax-report` | `types` · `validate <f.json>` · `scaffold <form>` using the in-repo stdlib schema validator |
| `glaw-fill-form` | `--form FORM --data return.json --out out/form` → `.fill.json` + `.fill.txt` manual-entry package |
| `glaw-irs-file` | `scaffold <form>` · `submit <payload.json> [--live] [--human-authority "<name/role>"] [--role ADMIN]` · `status <id>` · `efw2 <payload.json>` (W-2→SSA) · `list <year>`; `--live` validates and stages the payload, then refuses transmission unless the human-authority plus RBAC ADMIN gate is satisfied |
| `glaw-compliance-audit` | `<docs-dir> [--type s-corp\|c-corp\|llc\|fund] [-o out.md]` → ✅have / 🟡action / ❌gap per item |
| `glaw-exempt-org` | `search "<name>"` · `<EIN>` → nonprofit lookup + financial-risk read (ProPublica API, no key) |

## Scoring & sign-off
| Tool | Usage |
|---|---|
| `glaw-bureau-score` | `competency <json>` · `fraud <json>` → deterministic fraud score (0–100) + FBI competency scorecard |
| `glaw-chief-decision` | record the Chief's PROCEED / WITH-FIXES / WITH-CONDITIONS sign-off → matter timeline + decision card; final approve/deny requires `--score`, `--grade`, `--risks`, `--conditions`, and `--rationale`; `--approve-final` rebuilds `final_packet.json`, requires it to be ready, requires score ≥90 and an A-range grade, requires a proceed/approve decision, requires the Chief rationale to cite a current `SRC-####`, requires every open nonblocking red flag ID to appear in `--risks` or `--conditions`, and binds approval to that packet's `generated_at` plus SHA-256 digest; `--signoff` is a human-authority act and requires `--human-authority "<name/role>"` plus `--role ADMIN`, or `GLAW_HUMAN_AUTHORITY_ACTOR` plus `GLAW_RBAC_ROLE=ADMIN` |

## Zero-Dependency Policy

GLAW ships no third-party package manifest. The supported install path is:

```bash
./setup
bin/glaw-doctor
```

Library code that historically depended on packages such as pandas, pydantic, lxml,
python-docx, docxtpl, eyecite, juriscraper, jsonschema, or Google SDKs now uses in-repo
compatibility modules or local stdlib fallbacks. Google Sheets input uses CSV export URLs.
PDF/OCR bank ingestion uses repo code plus local binaries, not Python packages.
