# Founder Control & Dual-Class Structures (the "Meta / Musk" question)

How founders keep control while raising capital or selling economic stake — the real mechanisms,
verified to 2026. **This is corporate/securities law; bring in licensed counsel + (for public
companies) underwriters' counsel.** Verify current rules per Step 1a.

## The core idea: separate VOTES from ECONOMICS
A founder can sell or issue most of the *economic* interest while keeping the *voting* control by
holding a high-vote class.

| Company | Structure | Result |
|---|---|---|
| **Meta** | Class A = 1 vote; **Class B = 10 votes** (founder) | Zuckerberg ~**57% of the vote** on ~**13.6%** of equity |
| **Alphabet** | Triple-class; **Class B = 10 votes**, founder-only, not publicly traded; Class C = non-voting | Page/Brin keep majority vote while public floats Class A/C |
| **SpaceX** | Musk holds **Class B super-voting** → ~**85% of the vote**; Class B **auto-converts to Class A on transfer** | Control is **personal to Musk** — it cannot be sold/auctioned |
| **Snap** | Non-voting Class A to the public | Extreme version — IPO with zero public votes |

## The toolkit (draft from templates/)
1. **Dual/multi-class stock** — set classes in the **charter** (`templates/dual-class-charter-
   provisions.md`): Class A (1 vote, public/investors), Class B (e.g., 10 votes, founders),
   optional Class C (non-voting). Authorized under DGCL §151/§212, TBOC, NRS — differential voting
   is expressly permitted.
2. **Transfer/conversion mechanics** — Class B **auto-converts to Class A on any transfer** outside
   permitted exceptions (estate planning, affiliates). Makes super-voting *personal* (SpaceX model)
   and prevents a buyer from acquiring control via the cheap-to-acquire votes.
3. **Voting agreement + irrevocable proxy** (`templates/voting-agreement-skeleton.md`) — other
   holders agree to vote with the founder, or grant the founder a proxy "coupled with an interest"
   (DGCL §212(e)) so it's irrevocable.
4. **Voting trust** (DGCL §218) — shares are placed in trust; the founder-trustee votes them for a
   term. Older device; voting agreements are more common now.
5. **Board control** — class-based right to elect a majority/all directors; **classified
   (staggered) board**; removal **only for cause**; founder fills vacancies; **protective/veto
   provisions** over key actions.
6. **Charter defenses** — blank-check preferred, shareholder rights plan ("poison pill"), advance-
   notice bylaws, supermajority amendment thresholds, exclusive-forum + (where allowed) fee-shifting.
7. **Sunset clauses** — time-based (e.g., 7–10 yr), ownership-threshold, or death/incapacity
   triggers that collapse the high-vote class. Increasingly expected by index providers (S&P Dow
   Jones, FTSE Russell limit/exclude no-vote shares) and opposed by the Council of Institutional
   Investors — model the investor optics.

## Jurisdiction: Delaware vs Texas vs Nevada (the 2025–26 shift)
- **Delaware** — DGCL + Court of Chancery; the default. But controlling-stockholder conflicts get
  **entire-fairness** scrutiny — *Tornetta v. Musk* (Del. Ch. 2024) voided Musk's $56B Tesla pay
  package. Delaware's 2025 amendments (SB 21) narrowed controller liability in response.
- **Texas** — **TBOC (eff. Sept 2025)**: lets directors weigh the company's mission, gives
  controllers more latitude, raises shareholder-proposal/derivative-suit thresholds; Texas Business
  Courts. **Tesla and SpaceX redomiciled to Texas.**
- **Nevada** — statutory business-judgment protection, founder-friendly.
- Pick based on investor expectations vs control priorities; flag the tradeoffs honestly.

## "Retain control after a sale" — be precise
- **Selling economics, keeping votes** (IPO/secondary of low-vote stock): works — founder cashes
  out value while Class B keeps control.
- **Selling a *stake* (minority)**: works — keep >50% of votes (or the high-vote class) + board
  rights.
- **Selling the *whole* company (change of control / 100% acquisition)**: by definition the buyer
  controls — "keeping control" then means negotiated **rollover equity + board seats + consent
  rights + founder/CEO employment agreement**, not retained voting control. For inbound acquisitions
  (incl. **non-US acquirers** — CFIUS, HSR, exchange rules), coordinate M&A/securities counsel.

## Mandatory caveats
- **Exchange listing rules:** NYSE/Nasdaq permit dual-class **at IPO** but **prohibit
  mid-stream disparate reduction** of existing shareholders' voting rights (the voting-rights
  policy). You can't *add* super-voting to insiders after a public float.
- **Controlling-stockholder fiduciary duties** apply (entire fairness when conflicted — *Tornetta*).
- **S-corps cannot do this** (one class of stock). Dual-class needs a **C-corp**.
- Document everything; coordinate equity issuances with `equity-and-securities-compliance.md`.
