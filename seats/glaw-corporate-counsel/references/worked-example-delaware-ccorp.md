# Worked Example — Delaware C-Corp, Founder Dual-Class Control, Option Pool, Reg D Seed

A full pass through the 8-step workflow for the most common startup setup. Illustrative — every
document needs licensed-counsel review and current-fee verification (Step 1a). This is the model
for how to structure a `corporate-counsel` response.

## The facts (intake — Step 1)
- **Who:** two co-founders building a software company; one is the CEO who wants to keep voting
  control through future financings; one foreign co-founder (non-US, owns equity, will not work in
  the US yet).
- **Goal:** form the company, issue founder stock, set up an option pool, and raise a **$1.5M
  seed** from US angels + one fund — keeping CEO control.
- **State/entity:** wants the standard VC-ready setup.
- **UPL gate (1d):** legitimate formation; flag that the **securities raise** and **dual-class**
  structure need securities counsel sign-off; the foreign founder's **ownership is fine without a
  visa**, but working in the US is a separate immigration question.

**Recommendation up front:** **Delaware C-corp** (investor standard, QSBS-eligible, supports
dual-class + options) — *not* an LLC or S-corp (an S-corp can't have a foreign shareholder or more
than one class of stock, so it's incompatible with both the foreign founder and dual-class).

## Step 2 — entity & state
Delaware C-corp. Confirm the **tax** posture with `tax-strategy` (C-corp + **QSBS §1202** is the
reason founders pick C-corp); **foreign-qualify** in the state where the company actually operates.

## Step 3 — form the entity
1. **Certificate of Incorporation** — name check; registered agent in DE; authorize **dual-class**
   stock now (`templates/dual-class-charter-provisions.md`): Class A (1 vote, for investors/options)
   + Class B (10 votes, founders); blank-check preferred for the seed round; §102(b)(7) exculpation
   + indemnification.
2. **EIN** (SS-4) — foreign founder doesn't block this; responsible-party rules apply.
3. **Organizational consent** (`templates/organizational-consent.md`) — adopt bylaws, appoint
   directors/officers, authorize founder stock, adopt the equity plan, banking, fiscal year.
4. **No S-election** (foreign owner + multiple classes → ineligible; C-corp is the goal anyway).

## Step 4 — governance documents
- **Bylaws** (`templates/bylaws-skeleton.md`) — classified board optional; advance-notice; written
  consent; indemnification.
- **Founder stock purchase + vesting** — 4-yr/1-yr cliff; founders buy **Class B** at par while
  value is ~$0 → start the **QSBS 5-yr clock** and low basis.
- **§83(b) — file within 30 days** (hard deadline; calendar it for both founders).
- **IP assignment + confidentiality (CIIAA)** from each founder — investors will diligence this.
- **Voting agreement** (`templates/voting-agreement-skeleton.md`) — co-founder agrees to vote with
  the CEO / grants an irrevocable proxy; board-seat designations.

## Step 5 — founder control
- **Dual-class** (above): founders hold **Class B 10-vote**; the seed preferred and the option pool
  are **Class A (1 vote)** → the CEO keeps voting control even as economics are sold/granted.
- **Class B auto-converts to Class A on transfer** (control is personal to the founders, can't be
  acquired); add a **sunset** (e.g., 7–10 yr or on a transfer/IPO) to keep future investors and
  index providers comfortable.
- **Board:** founders designate the majority; one investor seat for the lead fund; CEO as chair.
- Note: the lead fund may push back on dual-class at seed — be ready to negotiate sunset terms or a
  voting-agreement-only approach.

## Step 6 — securities compliance for the $1.5M seed
- Use **Reg D Rule 506(b)** (no general solicitation; accredited + ≤35 sophisticated) — or
  **506(c)** if they'll market it (accredited-only + verification).
- Instruments: **priced preferred** (Series Seed) or **SAFEs/convertible notes**; issue as
  **Class A / preferred**, never Class B.
- **Subscription agreements + accredited-investor questionnaires**; **restrictive legends**.
- **File Form D within 15 days** of first sale; **Blue Sky** notices in each investor's state.
- **409A valuation** before granting options; **Rule 701** covers the option-plan offering.
- Hand the priced-round mechanics (term sheet, SPA, IRA, ROFR/co-sale, voting agreement at the
  investor level) to `pe-vc-counsel` for the definitive financing docs.

## Step 7 — ongoing compliance calendar
- **Delaware**: annual report + **franchise tax** (use the assumed-par-value method — the
  authorized-shares method can produce a shocking bill on a big share count; verify).
- **Registered agent** in DE + foreign-qualified states; **minute book** from day one.
- **CTA/BOI**: under the **March 2025 interim rule, the domestic C-corp is EXEMPT**; the **foreign
  founder doesn't make the company a "foreign reporting company"** (that status is about where the
  *entity* is formed, not its owners) — verify on fincen.gov.
- **S-corp reasonable comp** — N/A (it's a C-corp); but run payroll/W-2 + 1099s; **Form 5472** if
  the company becomes 25%+ foreign-owned.

## Step 8 — what the founders get
**Bottom line:** "We'll form a Delaware C-corp with a **dual-class** charter so you keep voting
control through the seed and beyond, issue your founder Class B with vesting + 83(b), set up the
option pool under a Rule 701 plan, and raise the $1.5M under Reg D 506(b) with Form D + Blue Sky
filings. The foreign co-founder can own equity freely; working in the US is a separate immigration
step."

**Document set to execute (in order):**
| # | Document | Template | Signer |
|---|---|---|---|
| 1 | Certificate of Incorporation (dual-class) | `dual-class-charter-provisions.md` | Incorporator → file DE |
| 2 | Organizational consent + cap table | `organizational-consent.md` | Incorporator/Board |
| 3 | Bylaws | `bylaws-skeleton.md` | Board |
| 4 | Founder stock purchase + vesting + **83(b)** | — | Each founder (83(b) in 30 days) |
| 5 | IP assignment / CIIAA | — | Each founder |
| 6 | Equity incentive plan + 409A | — | Board |
| 7 | Voting agreement | `voting-agreement-skeleton.md` | Founders (+ investors at close) |
| 8 | Seed financing (SAFE/preferred) + **Form D** + Blue Sky | (→ `pe-vc-counsel`) | Company + investors |

**Open items / counsel review:** DE securities counsel to confirm the dual-class charter, the lead
fund's view on dual-class/sunset, the 409A appraisal, and the financing documents; immigration
counsel for the foreign founder's work authorization; CPA (`tax-strategy`) on QSBS qualification.

**Disclaimer:** illustrative and informational — not legal advice; engage licensed counsel in the
relevant state before filing or selling securities; verify all current fees/rules.
