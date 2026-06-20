# IRS Exam & Collection Notices — what each is, the clock it starts, the right response

Triage starts here. The **first job** on any matter is to identify the notice, the **clock it
starts**, and whether that deadline is **jurisdictional** (miss it and a forum is lost forever)
or merely **administrative** (miss it and you lose leverage, not the forum). Decode every notice
against IRS.gov "Understand Your IRS Notice or Letter" before responding.

> Source spine: Tax Tip 2018-101 ("What taxpayers can do when a letter arrives") and the 2026
> notice/deadline series (2026-32 missed deadline, 2026-31 help paying, 2026-33 refund status,
> 2026-35 amend a return). Authority below is the primary law.

**The cardinal authentication rule (from the scam Tips):** the IRS's **first contact is by
mail**, not by phone, email, or text. A "notice" that arrives only as a phone call demanding
immediate payment or gift cards is a **scam** — see `scams-and-data-security.md`. Verify any
notice by its CP/Letter number on IRS.gov and the taxpayer's online account.

---

## Examination track

### CP2000 — *Automated Underreporter (AUR) notice*
- **What it is:** Not an audit. The IRS's computers matched the return against third-party data
  (W-2, 1099, K-1) and found a **discrepancy**; it proposes additional tax/penalty/interest.
- **Clock:** Generally **30 days** to respond (date on the notice controls). **Not** a notice of
  deficiency by itself — but ignoring it leads to a **CP3219A**.
- **Correct response:** Agree, partially agree, or disagree **in writing** on the response form,
  attaching documentation. A CP2000 often double-counts basis or ignores offsetting deductions —
  recompute it. Reconcile to the **Wage & Income transcript** (see `transcripts-and-reconstruction.md`).
- **Nature:** Administrative; preserves later rights, but a clean rebuttal here can end it.

### Letter 525 / Letter 692 / Letter 950 — *the 30-day letter*
- **What it is:** The examiner's proposed adjustments (the **Revenue Agent's Report**, Form 4549 +
  Form 886-A) with an invitation to **agree or appeal**. The general "30-day letter."
- **Clock:** **30 days** to file a **written protest** to the **IRS Independent Office of
  Appeals**.
- **Correct response:** If you disagree, **protest to Appeals** (formal written protest when the
  amount exceeds the small-case threshold — defer to `current-figures.md`). This is the cheaper,
  faster forum than Tax Court and where most cases settle on **hazards of litigation**.
- **Nature:** Administrative. Missing it does **not** bar relief — the IRS then issues the 90-day
  notice, which routes you to Tax Court — but you lose the Appeals-first advantage (you can still
  reach Appeals from a docketed Tax Court case).

### Form 4564 — *Information Document Request (IDR)*
- **What it is:** The examiner's request for specific records/documents during a field or office
  audit.
- **Clock:** A **response date** set by the examiner (negotiable; the IRS uses an enforcement
  timeline that can escalate to a **summons** if ignored).
- **Correct response:** Respond **completely and on time** but **only to what is asked** — do not
  volunteer beyond scope (privacy right). Object to overbroad requests in writing. In an eggshell
  audit, **do not respond substantively** until the criminal-exposure gate is cleared.
- **Nature:** Administrative; discipline here drives the whole exam (see `examination-workflow.md`).

### Form 4549 / Form 886-A — *the Revenue Agent's Report (RAR)*
- **What it is:** Form **4549** = the income-tax examination changes (the adjustment numbers and
  the recomputed tax); Form **886-A** = the examiner's written explanation of each adjustment.
- **Clock:** None by itself — it accompanies the 30-day letter. Signing the 4549 (or Form 870)
  is a **consent to assessment / waiver of restrictions** — do **not** sign to "be done" without
  analyzing it.
- **Correct response:** **Recompute every line** against the posted ledger
  (`bin/glaw-audit-package --form4549`); rebut each 886-A explanation with substantiation and
  authority.

### CP3219A — *Statutory Notice of Deficiency arising from AUR (the "90-day letter," AUR branch)*
- **What it is:** The formal **notice of deficiency** issued when a CP2000 is unresolved.
- **Clock / Nature:** **90 days** to petition the **U.S. Tax Court** — **jurisdictional** (see below).

### Letter 3219 / Letter 531 — *Statutory Notice of Deficiency ("90-day letter")*
- **What it is:** The IRS's formal determination of a deficiency, issued under **IRC §6212**. It is
  the taxpayer's **ticket to Tax Court** — the only way to litigate **without first paying**.
- **Clock:** **90 days** (150 days if addressed to a person outside the U.S.) to file a petition
  in the **U.S. Tax Court** (**IRC §6213(a)**).
- **Correct response:** **File the Tax Court petition before the 90th day**, full stop. If
  warranted, route litigation strategy to `/glaw-federal-trial-counsel`. Filing the petition
  **bars assessment** until the case is decided (§6213(a)).
- **Nature: JURISDICTIONAL.** The 90 days is **not** extendable and **not** subject to ordinary
  equitable tolling for Tax Court deficiency jurisdiction — **miss it and the Tax Court door
  closes**; the only remaining path is pay-then-sue (refund litigation) or audit reconsideration.
  Compute the petition deadline from the notice date the **day it arrives** and docket it.

---

## Collection track (post-assessment — hand off to `/glaw-tax-relief`)

These follow an assessment (after an agreed RAR, an unprotested 30-day letter, an unpetitioned
90-day notice, or an SFR). The audit seat flags them; collection resolution belongs to the
tax-relief seat.

| Notice | What it is | Clock | Nature |
|---|---|---|---|
| **CP14** | First notice of balance due | Pay-by date | Administrative |
| **CP501 / CP503** | Reminder notices (escalating) | Pay-by date | Administrative |
| **CP504** | Notice of **Intent to Levy** (state refunds / limited assets) — **not** yet full CDP | 30 days stated | Administrative (no CDP yet) |
| **Letter 1058 / CP90 / CP1058** | **Final Notice of Intent to Levy and Notice of Your Right to a Hearing** | **30 days** to file **Form 12153** (CDP) | **Time-critical** — triggers **CDP** rights under §6330 |
| **CP523** | Installment-agreement default / intent to terminate | 30 days stated | Administrative |
| **CP508C** | Certification of **seriously delinquent** tax debt to the State Department (passport) | — | §7345; lifted by IA/OIC |

**Lien vs. levy:** a **lien** (Notice of Federal Tax Lien, **§6320**) is a public *claim* securing
the debt; a **levy** (**§6330**) is the actual *seizure* (bank, wages, receivables). Both the NFTL
filing and the Final Notice of Intent to Levy independently trigger **CDP** rights and a **30-day**
Form 12153 window — past 30 days (within ~1 year) only an **Equivalent Hearing** remains, without
the levy-suspension and Tax Court guarantees.

---

## Triage cheat-sheet — clock and forum at a glance

| Notice | Clock | If you miss it |
|---|---|---|
| CP2000 | ~30 days | → CP3219A (90-day) issues |
| 30-day letter (525/692/950) | 30 days to protest | Lose Appeals-first; 90-day notice follows |
| IDR (Form 4564) | examiner's date | Summons risk; adverse inferences |
| **90-day notice (531/3219/CP3219A)** | **90 days to Tax Court** | **JURISDICTIONAL — Tax Court door closes** |
| CP504 | 30 days | Escalates toward Final Notice |
| **Letter 1058 / CP90** | **30 days (Form 12153)** | Lose CDP + Tax Court review of collection |
| CP508C (passport) | — | Passport action; resolve via IA/OIC |

Dollar thresholds (formal-protest ceiling, lien-filing threshold, passport threshold) defer to
`tax-legal-shared/current-figures.md` — verify current on IRS.gov.
