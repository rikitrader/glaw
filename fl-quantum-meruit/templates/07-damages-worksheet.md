<!-- MODULE 7 — Damages Calculation Worksheet (Florida). Pairs with `bin/glaw-qm damages`.
     NOT legal advice; verify the §55.03 quarterly rate. -->

# DAMAGES CALCULATION WORKSHEET — [PLAINTIFF] v. [DEFENDANT], Case No. ____

| Line | Item | Amount |
|---|---|---|
| 1 | Reasonable value of work/services performed | $[VALUE] |
| 2 | Less: payments received | −$[PAID] |
| 3 | **Outstanding balance** (Line 1 − Line 2) | **$[OUTSTANDING]** |
| 4 | Contractual late fees (if any) | $[LATE] |
| 5 | Prejudgment interest — § 55.03 (from [DUE DATE] to [DATE]) | $[INTEREST] |
| 6 | **Total judgment sought** (3 + 4 + 5) | **$[TOTAL]** |
| 7 | Taxable costs (filing, service, transcripts) — § 57.041 | $[COSTS] |
| 8 | Attorney's fees (only if contract/statute applies) | $[FEES] |

**Prejudgment interest basis:** outstanding $[OUTSTANDING] × annual rate [RATE]% ×
([DAYS] ÷ 365). Florida's § 55.03 rate is set **quarterly** by the CFO — apply the correct
rate for each quarter the debt was outstanding (myfloridacfo.com). Post-judgment interest
accrues at the § 55.03 rate on the date of judgment.

**Auto-compute:**
```
~/.claude/skills/glaw/bin/glaw-qm damages --value [VALUE] --paid [PAID] --due [YYYY-MM-DD]
```
<!-- UPL/work-product footer per /glaw-ethics-conflicts -->
