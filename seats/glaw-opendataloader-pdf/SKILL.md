---
name: glaw-opendataloader-pdf
description: "Extract structured data from PDFs with OpenDataLoader PDF (Apache-2.0, #1 benchmark). Converts PDF → Markdown / JSON (with bounding boxes) / HTML / Tagged-PDF, locally, no cloud. Use for: 'convert PDF to markdown', 'PDF to JSON', 'extract tables from PDF', 'parse PDF for RAG', 'OCR a scanned PDF', 'extract formulas/LaTeX from PDF', 'describe charts in a PDF', 'auto-tag / make PDF accessible', 'hybrid mode PDF', 'opendataloader'. Handles the openjdk PATH + the Apple-Silicon --device cpu requirement automatically."
allowed-tools:
  - Bash
  - Read
---

# OpenDataLoader PDF — extraction skill

Local PDF parser already installed on this machine (CLI via `uv tool`, JDK via `openjdk@21`).
Two modes — **fast** (deterministic, local Java, no server) and **hybrid** (routes complex pages to a docling AI backend for far better tables/OCR/formulas).

## Non-negotiable environment rules

1. **`java` must be on PATH.** `openjdk@21` is keg-only, so prefix every command:
   ```
   export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"
   ```
   (The macOS `/usr/bin/java` stub will NOT find it.)
2. **Hybrid server MUST run with `--device cpu` on this Apple-Silicon Mac.** The default
   `--device auto` selects MPS and crashes the docling layout model with
   `Cannot convert a MPS Tensor to float64`. CPU works cleanly and uses all cores.
3. **Batch all files into ONE invocation.** Each `glaw-opendataloader-pdf` call spawns a fresh
   JVM, so pass multiple files/folders at once — don't loop per-file.

## Decision: which mode?

| Document | Mode | Why |
|---|---|---|
| Standard digital PDF, just need text/structure | **Fast** | 0.02s/page, no server needed |
| Complex / borderless / nested tables | **Hybrid** | +90% table accuracy |
| Scanned / image-only PDF | **Hybrid + OCR** | needs `--force-ocr` |
| Math formulas (→ LaTeX) | **Hybrid + formula** | `--enrich-formula` + `--hybrid-mode full` |
| Charts/images needing descriptions | **Hybrid + picture** | `--enrich-picture-description` + `--hybrid-mode full` |
| Make an untagged PDF accessible | **Fast** | `-f tagged-pdf` |

When unsure, start with Fast; escalate to Hybrid only if tables/scans/formulas look wrong.

## Fast mode (no server)

```bash
export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"
opendataloader-pdf file1.pdf file2.pdf folder/ -o output/ -f markdown,json
```
- `-o/--output-dir` — output directory (NOT `--output-folder`)
- `-f/--format` — comma list: `json, text, markdown, html, tagged-pdf`
- Useful flags: `--sanitize` (redact emails/URLs/phones), `--use-struct-tree` (honor native PDF tags)

## Hybrid mode (two steps)

**Step 1 — start the backend** (run in background; first launch downloads docling/OCR models, ~20–30s init):
```bash
export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"
opendataloader-pdf-hybrid --port 5002 --device cpu
```
Wait until the log prints `Application startup complete` before converting. Add as needed:
- `--force-ocr` (scanned PDFs) — and `--ocr-lang "ko,en"` / `ja` / `ch_sim` / `ch_tra` / `de` / `fr` / `ar`
- `--enrich-formula` (LaTeX)  ·  `--enrich-picture-description` (chart/image alt-text)

**Step 2 — convert** (separate shell; batch all inputs):
```bash
export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"
opendataloader-pdf --hybrid docling-fast file1.pdf folder/ -o output/ -f json,markdown
```
- Add `--hybrid-mode full` whenever the server has `--enrich-formula` or `--enrich-picture-description` on.
- When done, stop the server: `pkill -f hybrid_server`.

### How to drive this as the agent
- Start the server with `run_in_background: true`, then poll its log file for
  `Application startup complete` (don't fixed-sleep — init time varies).
- Reuse one running server for the whole batch; only restart to change OCR/enrich flags.
- If a hybrid run returns HTTP 500 `Cannot convert a MPS Tensor to float64`, the server was
  started without `--device cpu` — restart it correctly.

## Output reference

JSON elements carry `type` (heading/paragraph/table/list/image/caption/formula), `id`,
`page number`, `bounding box` `[left, bottom, right, top]` in PDF points, and `content` —
ideal for RAG chunking + click-to-source citations. Markdown preserves heading hierarchy and
table structure for direct LLM context.

## Also available
- Python: `import opendataloader_pdf; opendataloader_pdf.convert(input_path=[...], output_dir="out/", format="markdown,json", hybrid="docling-fast")`
- MCP server `glaw-opendataloader-pdf` (user scope) — same engine via Model Context Protocol.
- LangChain loader: `langchain-opendataloader-pdf`.

## Agent identity & reporting posture

- Identity: `glaw-opendataloader-pdf` is the accountable GLAW seat for this work. It speaks as a named senior professional, not a generic assistant.
- Soul: `glaw-opendataloader-pdf` carries a distinct professional judgment posture for this seat; its reports must preserve its own lens, skepticism, evidence standards, red flags, and sign-off conditions instead of blending into a generic firm voice.
- Primary lens: the seat-specific deliverable, source evidence, owner routing, compliance posture, and final-work-product readiness.
- Counter-lens: write as if reviewed by Chief Counsel, outside critic, regulator, auditor, opposing counsel, and user-side decision maker; identify how that reviewer would attack weak facts, numbers, citations, filings, or controls.
- Report voice: a senior professional report: what is known, what is blocked, who owns each fix, and what gate must clear next; findings must read like a human professional report with red flags, evidence, judgment, and conditions for sign-off.
- Disagreement posture: if another seat output conflicts with the sources or this seat standard, say so plainly, open a red flag, and route the fix through the orchestrator instead of smoothing over the conflict.
- Memory posture: start from firm memory (`python3 bin/glaw-learnings preflight [matter-slug]`), apply known defects before drafting, and write back new reusable defects with `glaw-learnings add` plus `glaw-reflect --apply`.
