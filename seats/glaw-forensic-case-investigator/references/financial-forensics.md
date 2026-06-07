# Financial Forensics — Tracing, Shells, Badges of Fraud

## FOLLOW-THE-MONEY METHOD
1. **Account inventory:** every account — holder (legal name), bank, acct #, routing, signatories,
   who actually controls login/signature card, open & close dates, state of formation.
2. **Source → Account → Use:** for every dollar, where it came from, which account it landed in,
   where it left to. Build a directed flow.
3. **Reconcile expectations vs. reality:** customer/insurer paid $X for purpose Y → did $X reach Y?
   Gaps = diversion.
4. **Tie controllers to entities:** who opened it, who signed, who moved it. Control = liability.

## SHELL / MONEY-HIDING RED FLAGS (the "where is it hidden" checklist)
- **Same address for multiple "independent" entities** (e.g., several SPVs + a vendor at one suite).
- **SPV / holding LLC with no operations** receiving operating cash.
- **Out-of-state entity** holding an in-state operating account (jurisdiction arbitrage).
- **Newly formed entity** right before/after money moves or a dispute arises.
- **Re-skinning:** old company "can't be attached," form a new LLC, migrate brand/domain/Maps pin.
- **Nominee signatories / "accountant" or assistant** with signing authority who moves funds.
- **Personal control of a partnership/escrow account** (sole login handed to one insider).
- **Round-tripping:** money out to a related entity and partly back as "fees"/"loans."
- **Commingling:** customer deposits, insurer checks, investor funds in one account.
- **Cash-out / structuring:** withdrawals/zelle/wires kept just under reporting/limit thresholds;
  requests to *raise* transfer limits to move larger sums.
- **Insider payments while insolvent** ("not solvent that whole last year" + paying contractors).

## BADGES OF FRAUD (intent proxies — FUFTA §726.105(2) + common law)
Insider transferee · debtor kept control/use · concealment · transfer after suit threatened ·
transfer of substantially all assets · absconding · removal/concealment of assets · less-than-
equivalent value · insolvency at/around transfer · timing near a large new debt · essential-asset
transfer to a lienor→insider chain. **Two or more badges = strong actual-intent inference.**

## ENTITY CONTROL MAP — what to capture per entity
| Field | Why it matters |
|---|---|
| Legal name + type (LLC/Inc/SPV/Trust) | identity |
| State of formation + status | jurisdiction, good standing |
| EIN | links bank accounts & tax |
| Address / suite | shell-clustering detection |
| Registered agent / organizer | who set it up |
| Members/officers/signatories | **control = liability** |
| Bank(s) + acct #(s) + routing | follow-the-money anchor |
| Role in the flow | source / conduit / sink |
| First seen in evidence (date) | timing vs. disputes |

## INSOLVENCY & FRAUDULENT-TRANSFER ANALYSIS
- Establish insolvency window (debts > assets, or unable to pay debts as due).
- List every transfer to insiders/related entities in that window.
- For each: value given vs. received (reasonably equivalent?), badges present, transferee.
- Map the **clawback targets** (transferees who can be sued to disgorge).

## RECONSTRUCTION WITHOUT FULL STATEMENTS
When only chats/screenshots/check images exist: build a ledger of every dollar *mentioned*
(amount, date, payer, payee, account, source-cite), flag the ones with corroborating images/PDFs,
and mark the rest "asserted — subpoena bank to confirm." Never present asserted as proven.

## HAND-OFF TO OTHER SKILLS
For full statement reconstruction (P&L / balance sheet / GL from raw bank data), invoke the
`financial-forensics` skill. For securities/SPV/fund-structure questions, `institutional-finance`
or `pe-vc-counsel`. For MCA/usury/veil-piercing legal drafting, `elite-corporate-counsel`.
