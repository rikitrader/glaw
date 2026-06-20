# Jurisdiction & the 90-Day Clock — the whole ballgame

The Tax Court is a court of **limited jurisdiction**. If the predicate document or the filing
deadline is wrong, the case is dismissed for lack of jurisdiction no matter how strong the merits.
Get this right first, every time.

## What gives the Tax Court jurisdiction (the ticket in)

| Predicate | Authority | Petition window |
|---|---|---|
| **Statutory notice of deficiency** ("90-day letter") | IRC §6212; petition right §6213(a) | 90 days (150 if the notice is addressed to a person **outside the U.S.**) |
| **Notice of determination — CDP** (lien/levy) | §6320 / §6330(d)(1) | 30 days |
| **Notice of determination — innocent spouse** | §6015(e) | 90 days |
| **Notice of determination — worker classification** | §7436 | 90 days |
| **Failure to abate interest** | §6404(h) | 180 days |
| **Whistleblower award determination** | §7623(b)(4) | 30 days |
| **Declaratory judgment** (e.g., §7428 exempt status, §6110) | various | varies |

The deficiency-jurisdiction predicate is the **valid statutory notice of deficiency** — it must
(a) determine a deficiency, (b) be sent by certified/registered mail to the taxpayer's **last
known address** (§6212(b)), and (c) on its face tell the taxpayer the deficiency and the right to
petition. A "30-day letter" / Revenue Agent's Report is **not** a notice of deficiency and confers
no Tax Court jurisdiction — it routes to IRS Appeals, not the court.

## The 90-day clock (the single most important number in the seat)

- **Jurisdictional.** §6213(a). It is **not tolled** by settlement talks, an Appeals request, a
  demand letter, illness, or anything else. (Limited statutory/equitable exceptions exist for some
  determination notices post-*Boechler*, 142 S. Ct. 1493 (2022) — but treat the deficiency 90-day
  period as hard until an attorney confirms otherwise.)
- **Runs from the date on the notice**, counted in calendar days; if day 90 falls on a Saturday,
  Sunday, or D.C. legal holiday, it rolls to the next business day (§7503).
- **Timely-mailing = timely-filing** (§7502): a petition mailed (USPS postmark, or an IRS-
  designated private delivery service) on or before day 90 is timely even if it arrives later.
  Electronic filing through DAWSON is timestamped in Eastern Time — file with margin, not at 11:59.
- **A day late = the case is gone.** No equitable tolling for the deficiency clock under current
  doctrine. Docket it the moment the notice arrives:

```bash
bin/glaw-sol --due-date <notice-date> --filed-date <notice-date> --as-of <today>
bin/glaw docket add --owner "tax court docket clerk" --source "SRC-0001 notice source" \
  <day-90-date> "Tax Court petition - JURISDICTIONAL (90-day, §6213(a))"
```

## Assessment is barred while the clock runs (the leverage)

Once a valid notice of deficiency issues, the IRS may **not assess or collect** the deficiency
during the 90 days and, if a petition is filed, until the Tax Court decision is final (§6213(a)).
This is the prepayment-forum advantage: petitioning **stops assessment** without paying the tax
first — unlike the district-court refund forum, which requires full payment and a refund claim.

## Prepayment forum vs. refund forum (the forum choice)

| | **Tax Court** | **District Court / Court of Federal Claims** |
|---|---|---|
| Pay first? | **No** (§6213 bar) | **Yes** — full payment + refund claim (§7422; *Flora* full-payment rule) |
| Predicate | Notice of deficiency | Disallowed refund claim |
| Jury? | No | District Court: yes; CFC: no |
| Tax specialists? | Yes (dedicated tax bench) | Generalist |
| Appeal to | Regional U.S. Court of Appeals (§7482) | Same / Federal Circuit |

Forum choice is consequential and partly driven by binding precedent in the circuit of appeal
(the *Golsen* rule: the Tax Court follows the Court of Appeals to which the case would be
appealed). Route the district-court alternative to `/glaw-federal-trial-counsel`.

## Petition mechanics (Tax Court Rules)

- **Rule 34** — content of the petition: clear and concise assignments of error and the facts on
  which the taxpayer relies; an issue not raised is **deemed conceded**.
- **Rule 60** — proper parties; **Rule 41** — amendments.
- Filing fee ($60, waivable for hardship). The IRS answers (Rule 36); a **reply** is required only
  for affirmative allegations (Rule 37).
- New matter / increased deficiency raised by the IRS in the answer shifts the **burden of proof
  to the Commissioner** on that matter (Rule 142(a)).

> Verify the filing fee, day-counts, and any post-*Boechler* tolling development against
> uscourts.gov / the Tax Court Rules before relying — and quote dollar thresholds from
> `tax-legal-shared/current-figures.md`.
