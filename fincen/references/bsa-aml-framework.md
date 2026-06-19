# The BSA / AML Framework — Standing Reference

The durable legal architecture the GLAW FinCEN cell works inside. The dated regulatory
changes that move on top of this sit in `regulatory-updates-2025-2026.md`.

## 1. The statute — Bank Secrecy Act (BSA)
- **Codification:** 31 U.S.C. **5311–5336** (the "Currency and Foreign Transactions
  Reporting Act," a.k.a. the BSA), plus 12 U.S.C. 1829b / 1951–1960.
- **Purpose (5311):** require records and reports that have a "high degree of usefulness" in
  criminal, tax, regulatory, and counter-terrorism investigations.
- **Administrator:** the **Financial Crimes Enforcement Network (FinCEN)**, a Treasury
  bureau, with delegated authority from the Secretary (31 U.S.C. 5318(a)).
- **Regulations:** **31 CFR Chapter X** (parts 1010 general + industry-specific parts 1020
  banks, 1021 casinos, 1022 MSBs, 1023 broker-dealers, 1024 mutual funds, 1025 insurance,
  1026 futures, 1027 dealers in precious metals/stones, 1028 operators of credit-card
  systems, 1029 loan/finance, 1030 housing GSEs).

## 2. Who is a "financial institution"
Defined at 31 U.S.C. 5312(a)(2) and 31 CFR 1010.100(t): banks, MSBs, broker-dealers, mutual
funds, casinos, insurance companies, futures commission merchants, dealers in precious
metals/stones, and more. **Expanding frontier:** the 2026 GENIUS Act CIP NPRM would add
**permitted payment stablecoin issuers** to the BSA-FI universe (see
`genius-act-stablecoins.md`) — proposed, not final.

## 3. The core reporting / recordkeeping obligations
| Obligation | Trigger | Rule |
|---|---|---|
| **CTR** (Currency Transaction Report) | cash transaction(s) > **$10,000**/day per person | 31 CFR 1010.311 |
| **SAR** (Suspicious Activity Report) | known/suspected suspicious activity ≥ threshold | 31 CFR 1020.320 et al. |
| **CDD / Beneficial Ownership** | account opening; legal-entity customers | 31 CFR 1010.230 |
| **CIP** (Customer Identification Program) | new accounts | 31 CFR 1020.220 et al. |
| **314(a)** mandatory info request | law-enforcement query | 31 CFR 1010.520 |
| **314(b)** voluntary info sharing | FI-to-FI, registered | 31 CFR 1010.540 |
| **MSB registration** (Form 107) | being an MSB | 31 CFR 1022.380 |
| **FBAR** (FinCEN Form 114) | > $10,000 in foreign accounts | 31 CFR 1010.350 |
| **Form 8300** | > $10,000 cash in a trade/business | 31 CFR 1010.330 |
| **Travel / recordkeeping rules** | funds transfers ≥ $3,000 | 31 CFR 1010.410 |

## 4. The five AML-program "pillars"
A covered FI must maintain a written AML program (31 U.S.C. 5318(h); 31 CFR 1020.210 et al.):
1. **Internal policies, procedures, and controls.**
2. **A designated BSA/AML compliance officer.**
3. **Ongoing employee training.**
4. **Independent testing** (audit).
5. **(Since the 2018 CDD Rule) risk-based customer due diligence**, including
   beneficial-ownership identification — the "fifth pillar."

## 5. The AMLA-2020 shift — "effective and reasonably designed"
The **Anti-Money Laundering Act of 2020** (part of the FY21 NDAA) re-oriented the BSA:
- Programs must be **"effective and reasonably designed"** and **risk-based**, not merely
  present-and-papered.
- Treasury must publish national **AML/CFT Priorities** that institutions incorporate into
  their risk assessments.
- It created the **AML Whistleblower Program** (§ 6314 → 31 U.S.C. 5323) and the
  **Corporate Transparency Act** BOI regime (§ 6403 → 31 U.S.C. 5336).
- **The 2026-04-07 program-reform NPRM** (Fed. Reg. doc. **2026-07033**, pub. 2026-04-10;
  comment closed 2026-06-09) is FinCEN's attempt to write this shift into the program rules —
  and it **expressly supersedes and withdraws the July 3, 2024 proposal**
  (`regulatory-updates-2025-2026.md` § A). Still proposed.

## 6. The BSA Advisory Group (BSAAG)
The standing public-private body (Annunzio-Wylie Act § 1564) through which industry, law
enforcement, and regulators shape BSA policy. FinCEN periodically invites nominations
(most recently 2026-02-24). Membership/advice channel — not an obligation.

## 7. Examination & enforcement
- **Examiners:** the federal functional regulators (OCC, FRB, FDIC, NCUA for banks; SEC/FINRA
  for broker-dealers; IRS-SBSE for MSBs and others) examine for BSA compliance under FinCEN's
  delegated authority; the **FFIEC BSA/AML Examination Manual** is the working standard.
- **Penalties:** civil money penalties (31 U.S.C. 5321) and criminal penalties (5322) for
  willful violations; FinCEN can also pursue individuals (e.g., compliance officers). Recent
  examples: Canaccord $80M (2026), Paxful $3.5M (2025) — see `enforcement-actions.md`.

---

*Not legal advice. Compliance-advisory work-product for review by a licensed professional.
Verify all rates, thresholds, and rule status on FinCEN.gov before relying.*
