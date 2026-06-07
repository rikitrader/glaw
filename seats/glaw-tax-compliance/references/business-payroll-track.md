# Business & Payroll Non-Filer Track

Use this when the filer is an **entity** (S-corp, partnership, C-corp, multi-member LLC) or has
**employees**. These returns carry penalties the individual track doesn't, and one of them —
the **Trust Fund Recovery Penalty** — pierces the entity to hit owners *personally*. Verify
current dollar amounts per SKILL.md Step 1a (most are inflation-indexed).

## Sequence rule

**Entity return + K-1s must be filed BEFORE the owner's 1040** (Step 4). The owner's personal
income flows from the K-1, so an unfiled 1120-S/1065 blocks an accurate 1040. Order: entity
income returns → payroll returns (oldest forward) → owners' 1040s → then resolve + relief.

## 1. Unfiled entity income-tax returns

| Entity | Return | Late-filing penalty | Watch |
|---|---|---|---|
| **S-corp** | 1120-S | **§6699**: ~**$255 per shareholder, per month** (or part), up to **12 months** — *even if no tax is due* | Pass-through, so penalty surprises owners who assumed "no tax = no penalty" |
| **Partnership / multi-member LLC** | 1065 | **§6698**: same ~**$255 per partner, per month**, up to 12 months — *even with no tax due* | Per-partner × per-month compounds fast for multi-owner LLCs |
| **C-corp** | 1120 | **§6651** FTF (~5%/mo, max 25%) + FTP (~0.5%/mo) on tax due | Standard FTF/FTP mechanics like a 1040 |

> §6698/§6699 penalties are **eligible for FTA and reasonable cause** (they're FTF penalties).
> Check FTA first, exactly as with individuals (`references/penalty-relief.md`).

## 2. Unfiled payroll (employment-tax) returns

- **Form 941** — quarterly federal income-tax withholding + Social Security/Medicare.
- **Form 940** — annual FUTA.
- **W-2 / W-3** (to SSA) and **1099-NEC** (to contractors + IRS).
- Penalties: FTF/FTP under **§6651**, **failure-to-deposit** under **§6656** (tiered by how late
  the deposit is), all **FTA/reasonable-cause eligible**.

## 3. Trust Fund Recovery Penalty (TFRP) — §6672  ⚠ personal, severe

This is the one to flag loudly:
- A **responsible person** who **willfully** fails to collect/pay over withheld trust-fund taxes
  (the *employees'* income-tax withholding + employees' FICA share) is personally liable for
  **100%** of those taxes. (Not the employer's FICA share — just the trust-fund portion.)
- "Responsible" = anyone with authority over which bills get paid (officer, partner, bookkeeper,
  check-signer). "Willful" = paid other creditors instead of the IRS. Multiple people can be
  jointly liable.
- The IRS proposes it via **Letter 1153 / Form 2751**; contest by attacking *responsibility* or
  *willfulness* and/or **appeal** within the stated window.
- **It is NOT dischargeable in bankruptcy** and survives the entity's dissolution. It is a
  separate assessment, **not** an FTF/FTP penalty — so FTA and ordinary reasonable-cause don't
  abate it; the fight is over responsibility/willfulness.

## 4. Information-return penalties — §6721 / §6722

- **§6721** — failure to file a correct information return (1099/W-2) **with the IRS**.
- **§6722** — failure to furnish the correct payee statement **to the recipient**.
- Penalties are **per form**, tiered by how late you correct, **indexed annually**, with a much
  higher amount (and no cap) for **intentional disregard**. Unfiled 1099s for contractors are a
  common, expensive surprise for back-filing businesses — verify current per-form amounts.

## 5. Criminal & escalation flags

- **Payroll non-compliance is the fastest route to enforced collection and criminal referral.**
  Willful failure to collect/pay over employment tax can be charged under **§7202** (felony).
- If the business pyramided payroll taxes over multiple quarters, or owners diverted withheld
  funds, run the **Step 1d criminal-exposure gate** and route to a tax attorney before filing.
- Open the entity's books with `financial-forensics` if records are missing; sequence entity
  returns with `roofer-accounting` / `institutional-finance` where those skills fit the industry.
