---
name: glaw-reconstruct
version: 1.0.0
description: "GLAW Reconstruction Workflow — rebuild a FULL set of audited books from many bank/card statements across MULTIPLE accounts and formats, driven by the CFO chief orchestrator and gated by the Audit agent's adversarial consensus loop. Ingests every source into its own cash account, runs the statement-continuity (completeness) gate, reclassifies inter-account transfers (kills the double-count), ties each account to its statement closing, clears the books-doctor control gate, then puts the reconstructed statements through a CPA/IRS adversarial loop until the numbers are AGREED — producing a fully audited package. Use for: 'reconstruct the books', 'rebuild from bank statements', 'multiple accounts', 'forensic reconstruction', 'audit-ready financials from statements', 'reconstruct all statements', 'multi-account close'."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Skill
  - Agent
  - AskUserQuestion
triggers:
  - reconstruct the books
  - rebuild from bank statements
  - multiple accounts
  - forensic reconstruction
  - reconstruct all statements
  - multi-account close
---

## When to invoke this skill

The **end-to-end reconstruction workflow** — the only correct way to turn a pile of
statements (many accounts, many formats, many periods) into a **fully audited** set of
books. It is **not** a loose command: the **CFO chief orchestrator** (`/glaw-cfo`) drives it,
the **Controller** (`/glaw-controller`) posts the fixes, and the **Audit agent**
(`/glaw-audit`) runs the **adversarial consensus loop** on every reconstructed number before
sign-off. The deterministic engine is `bin/glaw-reconstruct`; this seat orchestrates it.

## Persona

A forensic controller rebuilding a company's books from source for an audit or IRS exam:
every account reconciled to its statements, every transfer between the company's own
accounts netted out, every period present, every figure defended against a skeptic.

## Preamble (run first)
```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## ⛔ The chief-orchestrated pipeline (every step owned, every number challenged)

```
            ┌──────────────────────  /glaw-cfo  (chief orchestrator, owns the loop)  ─────────────────────┐
            ▼                                                                                              │
0. MANIFEST   list every source → its own cash account (Checking, Savings, Amex = Liabilities:CreditCard) │
1. INGEST     glaw-reconstruct ingests each source (CSV/OFX/QFX/MT940/CAMT/PAIN/PDF) → its account         │
2. ⛔ CONTINUITY  completeness gate — each account's statements chain (opening==prior close, no gaps)      │
3. TRANSFERS  inter-account transfers detected + reclassified → the double-count is removed                │
4. ⛔ TIE-OUT     each account's GL balance == its latest statement closing balance                        │
5. ⛔ CONTROL     glaw-books-doctor over the rebuilt ledger (TB/BS/classified/cash/dedup/integrity)        │
6. ADVERSARIAL    /glaw-audit runs the consensus loop ───────────────────────────────────────────────────┘
                    RED (skeptical CPA + IRS revenue agent + fraud lawyer) attack the reconstructed
                    statements → COLLECT comments → REDIRECT /glaw-controller to fix (post entries) →
                    RE-RUN glaw-reconstruct → LOOP until no surviving challenge AND both agree
7. SIGN-OFF   /glaw-chief-decision records PROCEED/WITH-CONDITIONS; /glaw-ledger lock seals the periods
```

### Run the deterministic reconstruction
```bash
~/.claude/skills/glaw/bin/glaw-reconstruct manifest.json --out ~/recon --format text
```
Manifest (each source = one account; **give the statement's `opening`/`closing` so the books
tie** — an ongoing company never starts at zero):
```json
{"book":"acme","entity":"Acme LLC","window":5,
 "sources":[{"path":"checking/","account":"Assets:Bank:Checking","chart":"roofing",
             "opening":"50000","closing":"61200"},
            {"path":"amex.csv","account":"Liabilities:CreditCard:Amex","chart":"roofing",
             "type":"liability","opening":"0","closing":"-3400"}]}
```
- **`opening`/`closing`** — the statement's balances. The first statement's `opening` posts as an
  **Opening Balance Equity** entry so the GL reflects the true starting position; `closing` drives
  the per-account tie-out and the Golden Rule.
- **`type`** — `asset` (default) or `liability` (credit cards, lines of credit) for correct
  opening-balance sign.
- **`invert`** — set `true` only for a statement that shows charges as **positive** (the default,
  charges-negative, posts correctly).

⛔ **Exit 0 only when** continuity is complete, **every source's Golden Rule verified**, every cash
account has a closing balance **and ties**, the book is single-currency, and the control gate is
bulletproof. A vacuous pass is impossible: an account with statements but **no closing to tie to is
a FAILURE**, not a silent OK. A multi-currency book fails — revalue to one reporting currency
(`/glaw-fx`) first. Anything short → **not audit-ready**; the chief routes the fix.

### The adversarial consensus loop (step 6 — never skipped)
Hand the reconstructed statements to `/glaw-audit`, which runs the same loop-until-agreed
debate as `/glaw-cfo`: a CPA + IRS agent + financial-fraud lawyer attack every estimate,
cut-off, classification, and transfer; the Controller corrects the books via `/glaw-journal`;
re-reconstruct; repeat until the panel lands no surviving comment and agrees on every number.
Escalate the hardest convergence to `/glaw-chief-counsel`'s loop engine. Drive divergence
with `/glaw-adversarial`, convergence with `/glaw-consensus`.

## Deliverables
A fully reconstructed, **multi-account**, audited set of books: per-source ingest report,
the continuity (completeness) result, the transfer reclassifications, the per-account
tie-out, the books-doctor control report, the **adversarial findings record** (every comment
→ how resolved), and the audited statements + entry-to-source trace. Locked when signed.

## Not legal or accounting advice
Forensic-accounting work-product, not legal, tax, or accounting advice, and not an audit
opinion under any standard. Prepared for review and sign-off by a licensed CPA / attorney.
Carries the UPL footer from `/glaw-ethics-conflicts` on any external deliverable.
