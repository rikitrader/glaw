# Examination Workflow — from first notice to resolution

The audit ladder, the clocks that govern it, and the discipline that wins it. Read
`notices-and-letters.md` for the notice map and `taxpayer-bill-of-rights.md` for the rights you
assert at each rung. Every figure defers to `tax-legal-shared/current-figures.md`.

---

## 1. Identify the exam type

| Type | How it runs | Stakes |
|---|---|---|
| **Correspondence audit** | By mail; one or a few line items (e.g., EITC, a Schedule C deduction, a CP2000 match). | Lowest. Most common. Respond by mail with documentation. |
| **Office audit** | Taxpayer (or rep) brings records to an IRS office. | Medium. Narrower scope; an examiner, not a Revenue Agent. |
| **Field audit** | A **Revenue Agent** visits the home/business/representative's office. | Highest. Broad scope, business returns, ledger-level review. |

A **CP2000** is technically an **Automated Underreporter** match, not an audit, but it is handled
on the same substantiate-and-rebut discipline.

## 2. Fix the statute-of-limitations clocks FIRST

Before substance, know whether the year is even open. Compute the clocks:

```bash
bin/glaw-sol --due-date <YYYY-04-15> --filed-date <YYYY-MM-DD> --as-of <today>
```

| Clock | Limits | Starts | Length | Authority |
|---|---|---|---|---|
| **ASED** (assessment) | The IRS assessing additional tax | Return **filed** | 3 yr; **6 yr** if >25% of gross income omitted; **∞** if fraud or no return | **IRC §6501** |
| **CSED** (collection) | The IRS collecting an assessed debt | **Assessment** date | 10 yr (tolled by OIC, CDP, bankruptcy, time abroad) | **IRC §6502** |
| **RSED** (refund) | The taxpayer claiming a refund | Filing / payment | 3 yr from filing / 2 yr from payment | **IRC §6511** |

**Consequences you act on:**
- An **expired ASED** is a **complete defense** to additional tax — raise it before anything else.
- An **unfiled year** or **fraud** keeps the ASED open **indefinitely** — and is the eggshell
  trigger (route to `/glaw-investigations`; see `persona-and-guardrails.md`).
- A **Form 872** (Consent to Extend the Time to Assess Tax) request means the IRS's clock is
  running out. **Do not consent without analysis** — sometimes letting the ASED run is the win;
  sometimes a limited/restricted consent buys time to substantiate. Decide deliberately.

(Exact lengths/thresholds defer to `current-figures.md`.)

## 3. Reconstruct the IRS's account picture from transcripts

Respond from the record, not from memory. Pull what the IRS actually has:

```bash
bin/glaw-transcript --account <account.json> --wage-income <wi.json>
```

- **Account Transcript** → assessments, payments, penalties, the assessment date (→ CSED), and
  any **SFR** flag.
- **Wage & Income Transcript** → the third-party data (W-2/1099/K-1) the AUR/CP2000 used.
- **Return / Record-of-Account Transcript** → what was filed.

Full detail and the reconciliation gate are in `transcripts-and-reconstruction.md`.

## 4. IDR response discipline (the heart of a field audit)

The **Information Document Request (Form 4564)** drives the exam. Discipline:

1. **Answer only what is asked.** Volunteering beyond scope invites scope-creep and, in an
   eggshell audit, criminal exposure (Right to Privacy — "no more intrusive than necessary").
2. **Respond completely and on time.** Late or partial responses invite a **summons** and adverse
   inferences. Negotiate the date in writing if you need more time.
3. **Index every document to a ledger entry.** Each response item ties to a posted GL entry
   (`bin/glaw-audit-package`) or a named source — so substantiation is traceable, not a story.
4. **Object to overbroad requests in writing** and escalate to the **group manager** (Right to
   Quality Service) when an examiner exceeds scope.
5. **Eggshell gate:** if any badge of fraud is present, do **not** respond substantively until
   the criminal-exposure screen is cleared (`persona-and-guardrails.md`).

## 5. Substantiate every challenged item from the general ledger

For each account under exam, produce the supporting posted entries — each carrying its
tamper-evident hash — and **recompute the agent's proposed adjustments**:

```bash
bin/glaw-audit-package --book <book> --accounts Expenses:Meals,Expenses:Travel \
  --form4549 <4549.json>
```

Where records are genuinely lost, a **Cohan-rule** estimate may support a deduction — but it must
be **labeled an estimate** with a documented basis, never presented as a substantiated figure
(see `transcripts-and-reconstruction.md`). Route forensic edge cases to
`/glaw-financial-forensics`; tie the numbers out with `/glaw-accounting` + `/glaw-tax-provision`.

## 6. The resolution ladder

```
   Audit (exam)
        │  disagree
        ▼
   30-day letter (Letter 525/692/950 + Form 4549/886-A)
        │  written protest within 30 days
        ▼
   IRS Independent Office of Appeals   ──settle on hazards of litigation──▶ done
        │  no agreement → IRS issues...
        ▼
   90-day Statutory Notice of Deficiency (§6212)
        │  petition within 90 days  ── JURISDICTIONAL ──
        ▼
   U.S. Tax Court  (litigate WITHOUT prepaying; route to /glaw-federal-trial-counsel)
        │  (or, alternatively, after assessment:)
        ▼
   pay → file refund claim → Refund litigation (district court / Court of Federal Claims)
```

**Audit reconsideration** is the off-ramp when an assessment already exists (an agreed RAR, an
unprotested 30-day letter, an unpetitioned 90-day notice, or an **SFR**) but the taxpayer has
**documents not previously considered**. It is the practical way to replace an overstated **SFR**
with the real return, or to reopen a default assessment — grounded in the **Right to Challenge
the IRS's Position and Be Heard**.

## 7. Penalty abatement (run in parallel)

Test First-Time Abatement, then reasonable cause, and quantify the abatable penalty (Form 843):

```bash
bin/glaw-abatement --penalty <amt> [--factors death_or_serious_illness,reliance_on_tax_professional]
```

Mechanics and the decision tree are in `penalty-relief.md`.

## 8. ⛔ Adversarial gate — IRS-examiner RED → BLUE (before anything is sent)

**No response leaves the firm** until `/glaw-adversarial` runs the **IRS Revenue Agent / Appeals
Officer / Chief Counsel** red-team against it:

- **RED** attacks the substantiation (is every figure tied to the ledger?), the reconstruction
  method, the **SOL position** (is the year really closed, or is there a tolling event / §872 the
  defense missed?), and the **penalty defense** (does reasonable cause actually hold, or is it
  invented?).
- **BLUE** reworks any position the firm's own examiner-adversary destroys. A surviving kill-shot
  becomes a **condition + an attorney-sign-off flag + an honest downside** — the deliverable still
  ships, with the weakness disclosed (per the suite Chief Protocol).

Record the sign-off with `/glaw-chief-decision`.

## 9. Build the response package & docket the deadlines

Route the assembled facts to `/glaw-draft` for the stage reached: **IDR response** · **30-day
protest** (with hazards-of-litigation) · **90-day Tax Court petition** (with
`/glaw-federal-trial-counsel`) · **Form 2848** POA · **Form 843** abatement request. Then docket
every clock:

```bash
bin/glaw docket add --owner "IRS audit docket clerk" --source "SRC-0001 exam notice" <YYYY-MM-DD> "IDR response due"
bin/glaw docket add --owner "IRS audit docket clerk" --source "SRC-0001 exam notice" <YYYY-MM-DD> "30-day protest deadline"
bin/glaw docket add --owner "IRS audit docket clerk" --source "SRC-0001 notice" <YYYY-MM-DD> "90-day Tax Court petition (JURISDICTIONAL)"
```

## Gate summary (don't skip a rung)

1. Notice triaged + SOL clock computed (year open?) — **before** substance.
2. Eggshell screen cleared (no badges of fraud) **or** attorney referral made.
3. Account reconstructed from transcripts; income reconciles to the W&I transcript.
4. Every challenged item tied to the ledger or conceded (no fabricated substantiation).
5. RED→BLUE adversarial pass survived (or weaknesses disclosed as conditions).
6. Every jurisdictional deadline docketed.
