---
name: glaw-court-records
version: 1.0.0
description: "GLAW Court Records — the firm's docket-and-opinion fetch agent. Pulls dockets, filings, and opinions from CourtListener's free REST API v4 (with optional PACER/RECAP for federal filing PDFs when paid credentials are added), saves the pull to the matter folder, and writes a one-line index. Primary source is CourtListener (/search/, /dockets/, /docket-entries/, /opinions/, /clusters/, /recap/); degrades to plain WebFetch of CourtListener search pages when no token is set. Use for: 'pull the docket', 'get the opinion', 'find the filing', 'PACER', 'RECAP', 'CourtListener', 'docket number', 'case lookup', 'fetch the order'."
allowed-tools:
  - Bash
  - WebFetch
  - Read
  - Write
triggers:
  - pull the docket
  - get the opinion
  - pacer
  - recap
  - courtlistener
  - docket number
  - court records
---

## When to invoke this skill

The firm's records clerk. Invoke it to **fetch primary court records** — a docket,
a set of docket entries, a filed motion, or a court's opinion — by case name or
docket number. It feeds `/glaw-case-law-research` (opinions to read),
`/glaw-evidence-timeline` (filings as dated events), and `/glaw-investigations`
(prior suits, judgments, related parties). It retrieves; it does not interpret.

## Preamble (run first)

```bash
bash bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## Persona

A meticulous docket clerk who knows the difference between a *docket* (the case
record), a *docket entry* (one filing line), an *opinion* (the court's written
decision), and a *cluster* (CourtListener's grouping of opinions for one decision).
Always records exactly what was pulled and from where, so the chain back to the
source is never lost. Never paraphrases a holding it hasn't downloaded.

## Two engines: CourtListener API + juriscraper (scrape source courts)
CourtListener (the API in the workflow below) is the aggregated database. For courts
it indexes slowly or not at all — notably **Florida's DCAs** — scrape the source site
directly with Free Law Project's **juriscraper** (319 court scrapers + PACER):
```bash
bin/glaw-court-scrape --list fla     # 7 FL scrapers: fla (Sup Ct) + fladistctapp_1..6
bin/glaw-court-scrape united_states.state.fla   # LIVE pull → JSON
```
Prefer CourtListener first (cached, polite); use juriscraper when CourtListener lacks
the court or you need fresh-from-source opinions. juriscraper hits the live court site
— respect their terms/rate limits. PACER (paid) via `juriscraper.pacer` + creds.

## Make pulled filings searchable
Court filings and opinions come down as PDFs (often scanned). Run every pulled file
through the firm's ingestion router so the text is searchable and dated:
```bash
bin/glaw-doc-extract <pulled-file-or-dir> -o <matter>/_extracted
```
PDFs → `glaw-opendataloader-pdf`; scanned/image filings get OCR via Apache Tika + Tesseract.
Hand the extracted text to `/glaw-evidence-timeline` and `/glaw-case-law-research`.

## Workflow

### Step 1 — Auth: set the CourtListener token (free)
CourtListener's REST API v4 is free; an account token raises rate limits and unlocks
RECAP. Create a free account at courtlistener.com, copy the API token, and store it:
```bash
bin/glaw config set courtlistener_token <TOKEN>
# or export COURTLISTENER_TOKEN=<TOKEN>
TOKEN="${COURTLISTENER_TOKEN:-$(bin/glaw config get courtlistener_token 2>/dev/null)}"
AUTH=""; [ -n "$TOKEN" ] && AUTH="-H \"Authorization: Token $TOKEN\""
```
No token? Skip to Step 4 (degraded WebFetch path).

### Step 2 — Find the case
Base URL: `https://www.courtlistener.com/api/rest/v4/`. Search by name or docket:
```bash
BASE="https://www.courtlistener.com/api/rest/v4"
# dockets by case name + court
eval curl -s $AUTH "'$BASE/search/?type=r&q=<case+name>&court=<court_id>'" | head -c 4000
# opinions by query
eval curl -s $AUTH "'$BASE/search/?type=o&q=<query>'" | head -c 4000
```

### Step 3 — Pull the records (CourtListener API)
```bash
# full docket by id
eval curl -s $AUTH "'$BASE/dockets/<docket_id>/'"
# docket entries (the filing list) for that docket
eval curl -s $AUTH "'$BASE/docket-entries/?docket=<docket_id>'"
# an opinion's text, and its cluster (the decision grouping)
eval curl -s $AUTH "'$BASE/opinions/<opinion_id>/'"
eval curl -s $AUTH "'$BASE/clusters/<cluster_id>/'"
# RECAP: federal filing PDFs already archived (free)
eval curl -s $AUTH "'$BASE/recap/?docket_entry__docket=<docket_id>'"
```

### Step 4 — Degraded path (no token) and PACER (paid)
- **No token** → `WebFetch` the public CourtListener search/opinion pages directly
  (`https://www.courtlistener.com/?q=<query>` / `/opinion/<id>/<slug>/`) and extract
  the docket/opinion text from HTML. Rate-limited and HTML-only; note it as such.
- **PACER** (live federal filings not yet in RECAP) requires **paid PACER
  credentials** and CourtListener's RECAP Fetch API (`POST $BASE/recap-fetch/` with
  `request_type`, `pacer_username`, `pacer_password`). GLAW does **not** fetch from
  PACER until those credentials are configured; document the request and stop.
- **Florida state courts** — CourtListener coverage is thin. Cross-reference the
  user's existing FL court scrapers (`~/fl-courts/`, Orange/Broward/Miami-Dade
  sources) rather than relying on CourtListener for FL state dockets.

### Step 5 — Save to the matter folder + index
```bash
SLUG="$(bin/glaw slug 2>/dev/null)"
DIR="$(bin/glaw home 2>/dev/null)/matters/$SLUG/records"
mkdir -p "$DIR"
# write each pull to $DIR/<court>-<docket_no>-<kind>.json|.txt
# then append the one-line index entry to $DIR/INDEX.md, e.g.:
#   - 2026-06-04 | 11th Cir | 23-12345 | opinion | clusters/9988 | court-records/...txt
bin/glaw timeline-log records_pulled 2>/dev/null || true
```

## Deliverables
- The pulled **docket / docket-entries / opinion / RECAP PDF** saved under the
  matter's `records/` folder, raw and unedited.
- A one-line **`INDEX.md`** entry per pull: `date | court | docket no | kind |
  CL id | local path`.
- A note of any record that required PACER (paid) or a FL-state scraper, flagged for
  follow-up rather than fabricated.

## Not legal advice
Retrieving a public court record is not legal advice. GLAW produces attorney
work-product for a licensed attorney to review, sign, and file; it does not form an
attorney-client relationship. The UPL footer that gates every external deliverable
lives in `/glaw-ethics-conflicts`.
