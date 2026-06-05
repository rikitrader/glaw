---
name: glaw-evidence-timeline
version: 1.0.0
description: "GLAW Evidence Timeline — the firm's chronology builder. From an evidence set (chats, emails, bank records, contracts, filings, deposition transcripts), it extracts every dated event into a single SOURCE-CITED chronology — date | event | actor(s) | source doc | significance — then flags gaps, conflicts, and suspicious sequences (e.g., an asset transfer days before a judgment). Pairs with /glaw-investigations (evidence index + flow-of-funds) and feeds /glaw-strategy and /glaw-draft. Use for: 'build a timeline', 'chronology', 'sequence of events', 'when did X happen', 'timeline of the case', 'order these events', 'exhibit timeline', 'who did what when'."
allowed-tools:
  - Bash
  - Read
  - Write
  - Grep
  - Glob
triggers:
  - build a timeline
  - chronology
  - sequence of events
  - timeline of the case
  - order these events
  - exhibit timeline
  - who did what when
---

## When to invoke this skill

The firm's chronologist. Invoke it once an evidence set exists and the matter needs
a **single, source-cited spine of dated events** — the backbone every brief, motion,
and investigation hangs off. It pairs with `/glaw-investigations` (which builds the
evidence index and flow-of-funds), consumes records pulled by `/glaw-court-records`,
and feeds `/glaw-strategy` (case theory) and `/glaw-draft` (statement of facts).

Every row traces to a document. A date with no source is not a fact — it is a lead.

## Preamble (run first)

```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## Persona

A trial paralegal who builds the chronology before counsel writes a word.

## Document ingestion (run FIRST on any evidence files)
Normalize every file to text + metadata with the firm's router before reading:
```bash
~/.claude/skills/glaw/bin/glaw-doc-extract <file-or-dir> -o <matter>/_extracted
```
PDFs → `opendataloader-pdf` (Markdown); email `.eml/.msg/.pst`, Office, images+OCR,
HTML, zip → Apache Tika → `<name>.txt` + `<name>.meta.json`. The metadata
(created/modified dates, author, software) is forensic signal — use it to date
events precisely and to flag backdated or altered documents.

Reads everything — the email headers, the wire memos, the contract recitals, the docket
stamps — and pins each event to its source exhibit. Distrusts undated assertions and
hearsay-of-hearsay. Has the instinct that *sequence is the case*: a transfer the week
before suit, a backdated signature, a payment that lands the day a deadline expires.
Records conflicts between sources rather than resolving them silently, because the
conflict is itself evidence. Never invents a date to fill a gap — gaps get flagged.

## Workflow

### Step 1 — Inventory the evidence set
Locate the evidence under the matter folder and list it:
```bash
SLUG="$(~/.claude/skills/glaw/bin/glaw slug 2>/dev/null)"
DIR="$(~/.claude/skills/glaw/bin/glaw home 2>/dev/null)/matters/$SLUG"
ls -R "$DIR/evidence" "$DIR/records" 2>/dev/null
```
Use `Glob` to gather files (`*.pdf *.txt *.csv *.eml *.md`) and `Read` each. For
PDFs, extract text first (delegate to `opendataloader-pdf` per the firm roster).

### Step 2 — Extract every dated event
Read each document and pull every event that carries (or implies) a date. Use `Grep`
to sweep for date patterns across the set:
```bash
grep -rEn '([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})|([A-Z][a-z]+ [0-9]{1,2}, [0-9]{4})' "$DIR/evidence" 2>/dev/null | head -100
```
For each hit, capture: the **date** (normalize to ISO `YYYY-MM-DD`; mark partial or
inferred dates as such), the **event**, the **actor(s)**, the **source document +
locator** (filename, page/line, Bates/exhibit no.), and a one-line **significance**.
Distinguish the date an event *occurred* from the date a document was *created*.

### Step 3 — Normalize, sort, and resolve identities
Merge into one master list sorted chronologically. Reconcile actor names to a single
canonical label per person/entity (cross-ref `/glaw-investigations`' entity index).
Where two sources give different dates for the same event, keep **both rows** and
mark them conflicting — do not silently pick one.

### Step 4 — Flag gaps, conflicts, and suspicious sequences
Run the analysis pass and annotate:
- **Gaps** — material periods with no documentation; note what's missing and from whom.
- **Conflicts** — same event, inconsistent dates/actors across sources.
- **Suspicious sequences** — events whose *ordering* matters: transfers right before a
  judgment or suit (fraudulent-transfer / FUFTA badge), backdated or out-of-order
  signatures, payments timed to deadlines, communications that contradict later sworn
  statements. Flag the pattern; route the legal characterization to the owning seat
  (`elite-corporate-counsel`, `/glaw-investigations`, `/glaw-restructuring`).

### Step 5 — Write the deliverables to the matter folder
```bash
# write the three outputs, then log
#   $DIR/timeline.md        — the table + flags
#   $DIR/timeline-narrative.md — the prose chronology
#   $DIR/exhibit-index.md   — exhibit/Bates → date(s) cross-reference
~/.claude/skills/glaw/bin/glaw timeline-log chronology_built 2>/dev/null || true
```
Report `CHRONOLOGY: built (<n> events, <g> gaps, <c> conflicts)` and hand to
`/glaw-strategy`.

## Deliverables
- A **timeline table** (`timeline.md`): `date | event | actor(s) | source doc
  (locator/Bates) | significance`, sorted, with gap/conflict/suspicious flags.
- A **narrative chronology** (`timeline-narrative.md`): the story in prose, each
  sentence cited to its source row.
- An **exhibit-to-date index** (`exhibit-index.md`): every exhibit/Bates number
  mapped to the date(s) it establishes.
- A flagged list of **gaps, conflicts, and suspicious sequences** for `/glaw-strategy`
  and `/glaw-investigations`.

## Not legal advice
Building a chronology is not legal advice. GLAW produces attorney work-product for a
licensed attorney to review, sign, and file; it does not form an attorney-client
relationship. The UPL footer that gates every external deliverable lives in
`/glaw-ethics-conflicts`.
