# The GENIUS Act, Payment Stablecoins & Crypto BSA Obligations

The newest frontier of the BSA-FI universe. **Much of this is PROPOSED rulemaking** — flag
that on every output.

## A. The GENIUS Act (2025)
- **Name:** Guiding and Establishing National Innovation for U.S. Stablecoins Act of 2025.
- **What it does:** creates a federal framework for **permitted payment stablecoin issuers**
  (PPSIs) — entities authorized to issue dollar-pegged payment stablecoins — and directs
  Treasury/FinCEN to apply **anti-illicit-finance (BSA/AML)** requirements to them.

## B. The two 2026 FinCEN/Treasury rulemakings under the GENIUS Act
### 2026-04-08 — Treasury Proposes Rule to Implement GENIUS Act Illicit-Finance Requirements `NPRM`
- Treasury/FinCEN proposes the broader anti-illicit-finance framework for the payment-
  stablecoin regime. **Proposed, not final.**

### 2026-06-18 — GENIUS Act CIP Joint NPRM `NPRM` — **Fed. Reg. 2026-12460**
- **Joint** with the OCC, FRB, FDIC, NCUA.
- **Core proposal:** treat **permitted payment stablecoin issuers** as **financial
  institutions under the BSA**, each required to maintain a **Customer Identification
  Program (CIP)**.
- **Authority:** GENIUS Act; BSA CIP authority **31 U.S.C. 5318(l)**; the CIP rule template at
  31 CFR 1020.220.
- **What a CIP requires (applied to an issuer):** written identity-collection and -verification
  procedures for customers, recordkeeping, customer notice, and comparison against
  government lists (incl. OFAC).
- **Status:** **PROPOSED.** Comment period applies; effective date not set. **Do not build a
  compliance program to the proposed text as if it were final** — scope and obligations may
  change. Verify status on FinCEN.gov / federalregister.gov.

## C. Existing crypto BSA reality (this is current law, not proposed)
Independent of GENIUS, **convertible-virtual-currency (CVC) administrators and exchangers are
already money services businesses** under FinCEN's 2013 and 2019 guidance:
- **MSB status:** a CVC money transmitter must **register** (Form 107, 31 CFR 1022.380),
  maintain an **AML program** (1022.210), file **SARs** (1022.320) and **CTRs**, and apply the
  **Travel Rule** (1010.410) to qualifying transfers.
- **OFAC applies fully** to crypto — sanctioned addresses/persons are blocked the same as fiat.
- **Enforcement is real:** **Paxful $3.5M (2025-12-09)** for facilitating suspicious activity
  with illicit actors; earlier corpus actions include **BitMEX $100M (2021)** and the first
  bitcoin-mixer penalty (2020). See `enforcement-actions.md`.

## D. How GLAW uses this
- `/glaw-fincen-crypto` does **on-chain tracing** (analytical, public-data-only); it is not a
  compliance opinion on whether a client is a regulated MSB/PPSI.
- For "is my stablecoin/crypto business a BSA financial institution, and what must it do?" →
  route doctrine to `/glaw-regulatory-aml`, read this file, and **state clearly which
  obligations are current law (MSB rules) vs. proposed (GENIUS CIP NPRM).**

---

*Not legal advice. Compliance-advisory work-product for review by a licensed professional.
The GENIUS Act rules are proposed and non-final — verify current status on FinCEN.gov and
federalregister.gov before relying.*
