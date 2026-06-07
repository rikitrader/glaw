# Audit-Trail Specification

Every deliverable carries an audit trail so any conclusion can be walked back to a source.
This is what separates a litigation/SEC-grade product from a guess. **No audit trail → not
shippable.**

## The citation atom

Every load-bearing factual sentence ends with a bracketed cite. Formats:

| Source type | Cite format | Example |
|---|---|---|
| SEC/issuer filing | `[FORM : section/page]` | `[10-K FY24 : Item 7 MD&A p.42]` |
| Trade record | `[blotter : row/timestamp]` | `[blotter : row 1187, 2024-03-11 15:58:02 ET]` |
| Email / chat | `[comms : date : sender→recipient]` | `[email : 2024-02-09 : CFO→Controller]` |
| Bank / account | `[acct ####(last4) : line/date]` | `[acct 4471 : 2024-01-22 wire $250,000]` |
| Board / minutes | `[minutes : date : item]` | `[board minutes : 2023-11-30 : item 4]` |
| Deposition / testimony | `[depo : name : p:line]` | `[depo : Smith : 88:14]` |
| Statute / rule | `[cite]` (verify vs. primary law) | `[Exchange Act §10(b); Rule 10b-5]` |
| Not present | `NOT IN RECORD` | — |

Rules:
- **Quote, don't paraphrase, the load-bearing facts** (admissions, false statements verbatim).
- **One cite per fact**, more if corroborated by multiple sources.
- **Label** each statement FACT / INFERENCE / THEORY. Inferences name the facts they rest on.

## The audit-trail table (closes every deliverable)

A single table mapping the chain end-to-end:

| # | Source (file/locator) | Location | Extracted fact (verbatim or precise) | Used in conclusion | Confidence |
|---|---|---|---|---|---|
| 1 | 10-K FY24.pdf | Item 7, p.42 | "Revenue rose 38% on new enterprise contracts" | Channel-stuffing theory (Finding 3) | Med |
| 2 | blotter.csv | row 1187 | CEO sold 200k sh 2 days pre-restatement | Insider-trading Finding 5 | High |

## Integrity controls

- **Hash originals** where possible (`shasum -a 256 file`) and record the digest so the
  evidence set is tamper-evident. Work on copies.
- **Flag gaps**: referenced-but-missing documents (`<attached: X>` with no file), missing
  statement pages, date-sequence breaks — list them in *Gaps & Next Steps*.
- **Estimates**: if a number must be derived, label it `[ESTIMATED]` and state the method.
  Never present an estimate as a sourced fact.
- **Conflicts**: when two sources disagree, show both and the resolution rationale — do not
  silently pick one.

## Privilege & ethics flags
- Mark anything potentially **privileged** (attorney–client / work product) before it goes
  in an index that might be produced.
- Surface **adverse facts** about the user's own position — burying them defeats the purpose.
- This is analytical support, **not legal advice**; licensed counsel reviews before filing.
