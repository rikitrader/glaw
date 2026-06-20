# Sources & Corpus Provenance Index

Maps each ingested **FinCEN Updates** email (date + headline) to the KB file(s) that consumed
it, and the primary-authority map. Source feed: `fincenupdates@public.govdelivery.com`
(the user's subscription), cross-checked against FinCEN.gov / the Federal Register.

## Corpus → KB file (2025–2026 window)

| Date | Headline (FinCEN Update) | Type | Consumed by |
|---|---|---|---|
| 2026-06-18 | GENIUS Act CIP joint NPRM (Fed. Reg. doc. 2026-12460; pub. 2026-06-22) | NPRM | genius-act-stablecoins.md; regulatory-updates §E; crypto seat |
| 2026-06-12 | Guidance: eliminate fraud via information sharing (314(b)) | Advisory | sar-ctr-reporting.md; regulatory-updates §I |
| 2026-06-11 | Spanish translation — 2026 FIFA World Cup HT notice | Notice | regulatory-updates §H; tbml seat |
| 2026-06-05 | Joint advisory: non-work-authorized populations & employers | Advisory | regulatory-updates §H |
| 2026-05-11 | Notice: HT threat during 2026 FIFA World Cup | Notice | regulatory-updates §H; tbml seat |
| 2026-05-11 | Alert: stop ML by Iran's IRGC | Alert | regulatory-updates §H; fatf-international.md; ofac seat |
| 2026-05-06 | CDD FAQs consolidated to align w/ Exceptive Relief Order | FAQ | cdd-beneficial-ownership.md; regulatory-updates §B |
| 2026-04-30 | RMSB registration OMB renewal (Form 107) — comment req | OMB/PRA | bsa-aml-framework.md; regulatory-updates §A |
| 2026-04-16 | FY2025 Year in Review | Report | regulatory-updates §A |
| 2026-04-09 | Updated FAQs — Minnesota (Hennepin/Ramsey) GTO | FAQ | gto-tracker.md; regulatory-updates §D |
| 2026-04-08 | Treasury (FinCEN+OFAC) proposes GENIUS Act PPSI AML/CFT + sanctions rule (Fed. Reg. doc. 2026-06963; pub. 2026-04-10) | NPRM | genius-act-stablecoins.md; regulatory-updates §E |
| 2026-04-07 | NPRM: fundamentally reform FI AML/CFT programs (Fed. Reg. doc. 2026-07033; pub. 2026-04-10; withdraws Jul-3-2024 NPRM) | NPRM | bsa-aml-framework.md; regulatory-updates §A; aml seat |
| 2026-03-19 | FAQs — Southwest Border GTO | FAQ | gto-tracker.md; regulatory-updates §D |
| 2026-03-10 | Expanded Southwest Border GTO | GTO | gto-tracker.md; regulatory-updates §D; tbml seat |
| 2026-03-06 | $80M penalty — Canaccord Genuity LLC | Enforcement | enforcement-actions.md; regulatory-updates §F |
| 2026-02-27 | Limited Exemptive Relief — Minnesota GTO | Exceptive Relief | gto-tracker.md; regulatory-updates §D |
| 2026-02-24 | BSAAG nominations | Admin | bsa-aml-framework.md; regulatory-updates §A |
| 2026-02-13 | Exceptive Relief to streamline CDD | Exceptive Relief | cdd-beneficial-ownership.md; regulatory-updates §B |
| 2026-02-13 | Whistleblower tips webpage | Notice | whistleblower-program.md; regulatory-updates §I |
| 2026-01-13 | FAQs — Minnesota Fraud GTO | FAQ | gto-tracker.md; regulatory-updates §D |
| 2026-01-09 | Sec. Bessent — combat fraud in Minnesota | Notice | gto-tracker.md; regulatory-updates §D |
| 2025-12-22 | Data-driven border ML operation | Notice | gto-tracker.md; regulatory-updates §D |
| 2025-12-09 | $3.5M penalty — Paxful | Enforcement | enforcement-actions.md; genius-act-stablecoins.md; regulatory-updates §F; crypto seat |
| 2025-11-21 | FATF identifies AML/CFT/CPF-deficient jurisdictions | Advisory | fatf-international.md; regulatory-updates §G; ofac seat |
| 2025-11-13 | Sinaloa Cartel — 10 MX gambling estabs = primary ML concern | Notice | fatf-international.md; regulatory-updates §H; tbml seat |
| 2025-10-09 | SAR FAQs (four), joint w/ FRB/FDIC/NCUA/OCC | FAQ | sar-ctr-reporting.md; regulatory-updates §C; sar seat |
| 2025-09-08 | Modified Southwest Border GTO | GTO | gto-tracker.md; regulatory-updates §D |
| 2025-09-08 | Notice on financially motivated sextortion | Notice | regulatory-updates §H |
| 2025-09-05 | Guidance — cross-border information sharing | Advisory | fatf-international.md; sar-ctr-reporting.md; regulatory-updates §G |
| 2025-09-03 | FinCEN.gov UI refresh | Admin | (noted; no compliance substance) |

## Pre-window corpus items used for context (not 2025–2026)
- 2025-06-27 — banks' alternative TIN-collection method → cdd-beneficial-ownership.md (context)
- 2025-06/08 — fentanyl-counter orders (extended Aug 2025) → gto-tracker.md (context)
- 2025-02-06 — Brink's $37M penalty → enforcement-actions.md
- 2024-01-31 — Asre $100k penalty → enforcement-actions.md
- 2024-01-01 — BOI registry began accepting reports → cdd-beneficial-ownership.md
- 2024-03-15 — CIP/CDD ruling for IRA designated beneficiaries → cdd-beneficial-ownership.md
- 2024-07-19 — July-2024 AML/CFT program NPRM (now withdrawn by 2026-04-07) → bsa-aml-framework.md
- 2021-08-10 — BitMEX $100M; 2020-10-19 — first bitcoin-mixer penalty → enforcement-actions.md

## Primary-authority map (quick index)
- **BSA statute:** 31 U.S.C. 5311–5336 · regs **31 CFR Chapter X**
- **Delegated authority / exceptive relief:** 31 U.S.C. 5318(a)
- **AML program:** 31 U.S.C. 5318(h); 31 CFR 1020.210 et al.
- **CIP:** 31 U.S.C. 5318(l); 31 CFR 1020.220 et al.
- **CDD Rule:** 31 CFR 1010.230
- **SAR:** 31 U.S.C. 5318(g); 31 CFR 1020.320 et al. · **CTR:** 31 CFR 1010.311
- **314(a)/(b):** 31 CFR 1010.520 / 1010.540
- **GTO:** 31 U.S.C. 5326; 31 CFR 1010.370
- **Special measures:** 31 U.S.C. 5318A
- **MSB registration:** 31 CFR 1022.380 (Form 107)
- **CTA / BOI:** 31 U.S.C. 5336; 31 CFR 1010.380
- **Whistleblower:** AMLA § 6314 → 31 U.S.C. 5323
- **Penalties:** 31 U.S.C. 5321 (civil) / 5322 (criminal)
- **AML/CFT Program reform NPRM (2026-04-07):** Fed. Reg. doc. **2026-07033**, pub. 2026-04-10
- **GENIUS PPSI AML/CFT + sanctions NPRM (2026-04-08):** Fed. Reg. doc. **2026-06963**, pub. 2026-04-10
- **GENIUS PPSI CIP NPRM (2026-06-18):** Fed. Reg. doc. **2026-12460**, pub. 2026-06-22

## Citation-verification status (verified 2026-06-18 against federalregister.gov / fincen.gov / fatf-gafi.org)

### CONFIRMED to a precise primary citation
- **2026-04-07 program-reform NPRM** → Fed. Reg. doc. **2026-07033** (pub. 2026-04-10),
  "Anti-Money Laundering and Countering the Financing of Terrorism Programs"; comment period
  closed 2026-06-09; proposed 12-month post-final implementation. **Expressly supersedes and
  withdraws the July 3, 2024 program NPRM** (FinCEN states it will not finalize the 2024
  proposal). Still PROPOSED.
- **2026-04-08 GENIUS illicit-finance NPRM** → Fed. Reg. doc. **2026-06963** (pub. 2026-04-10),
  "Permitted Payment Stablecoin Issuer AML/CFT Program and Sanctions Compliance Program
  Requirements"; **joint FinCEN + OFAC**; comment closed 2026-06-09. Still PROPOSED.
- **2026-06-18 GENIUS CIP NPRM** → Fed. Reg. doc. **2026-12460** CONFIRMED CORRECT
  (public inspection; scheduled pub. 2026-06-22; Docket FINCEN-2026-0100). Still PROPOSED.
- **Enforcement amounts/dates** — Canaccord **$80M** (2026-03-06, Consent Order 2026-01),
  Paxful **$3.5M** (2026-12-09 release / order 2025-08-12), Brink's **$37M** (2025-02-06,
  $42M total w/ DOJ NPA) — all CONFIRMED.
- **Southwest Border GTO terms** — CONFIRMED: expanded order lowers CTR threshold to **$1,000**
  (original 2025 order $200), AZ/CA/NM/TX border ZIPs, effective **2026-03-07 to 2026-09-02**.
- **FATF call-for-action list** — Oct 22–24, 2025 plenary (lists dated 24 Oct 2025):
  **DPRK, Iran, Myanmar** CONFIRMED (countermeasures for DPRK/Iran; EDD only for Myanmar).
  Oct-2025 grey-list removals: Burkina Faso, Mozambique, Nigeria, South Africa.

### STILL PENDING / deliberately not pinned to a number
- **Minnesota (Hennepin/Ramsey) GTO** exact threshold, covered institutions detail, and
  expiration — not independently confirmed; read the current order on FinCEN.gov.
- Current **CTA/BOI reporting scope**: in flux; not stated as a fixed obligation.

---

*Not legal advice. Compliance-advisory work-product for review by a licensed professional.*
