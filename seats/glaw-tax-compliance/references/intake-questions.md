# Structured Intake (AskUserQuestion spec)

When `AskUserQuestion` is available, fire **one** call batching the four **categorical** intake
items below. This is faster and less error-prone than a prose interview. Keep the two free-form
items — *which tax years* and *why the returns were late* — conversational (they don't fit fixed
options). Skip any question the user already answered or a document already resolves.

`AskUserQuestion` allows 1–4 questions per call, each with 2–4 options; the user can always pick
"Other" and type a custom answer, so options need not be exhaustive — cover the common cases.

## The four questions

### Q1 — Tax authority  (header: `Authority`)
Drives the entire ruleset; federal vs. state vs. foreign are parallel but different.
- **IRS (federal)** — U.S. federal back taxes.
- **A U.S. state** — state Department of Revenue (ask which; some states have no income tax — see `references/state-and-international.md`).
- **Both federal + state** — file federal first so AGI flows to the state return.
- **Another country** — non-U.S. authority; framework applies but specifics differ; recommend local pro.

### Q2 — Filer type  (header: `Filer type`)
Determines forms, entity-return sequencing, and SE-tax/payroll exposure.
- **Individual (W-2 / 1040)** — wages only, simplest path.
- **Self-employed / Schedule C** — 1099/cash income; needs expense reconstruction + SE tax.
- **LLC** — single-member (Schedule C) vs. multi-member (1065); clarify in follow-up.
- **S-corp / C-corp / partnership** — entity return (1120-S/1120/1065) + K-1s before the owner's 1040.

### Q3 — IRS contact / collection status  (header: `IRS contact`)
Sets urgency and which deadline (if any) is controlling.
- **No notices yet** — proactive cleanup; most options open.
- **Got a notice (CP-series)** — balance/levy-intent notices; identify which (CP14/501/503/504 vs. the final CP90/LT11/Letter 1058 that grants CDP rights).
- **SFR / Substitute for Return filed** — IRS assessed an inflated balance; plan to replace it.
- **Active lien / levy / wage garnishment** — urgent; CDP or TAS may be time-critical.

### Q4 — Ability to pay  (header: `Ability to pay`)
Selects the balance-resolution path in Step 5.
- **Can pay in full** — clears the balance and preserves a clean record for FTA.
- **Can pay monthly over time** — Installment Agreement (Form 9465 / online).
- **Can't pay full; have some assets/income** — evaluate Offer in Compromise (RCP math).
- **Paying anything is a hardship** — Currently Not Collectible (Form 433-F).

## After the answers

- Map answers onto Step 2 (years) and Step 5 (resolution path).
- For anything still blank, apply the **1c defaults**, state the assumption, and proceed.
- Then ask the two free-form items conversationally: *"Which tax years are unfiled or late?"* and
  *"What was going on when they went unfiled?"* (the latter feeds reasonable-cause viability,
  Step 6).
- Re-confirm the categorical answers before any irreversible step (filing, sending a letter).
