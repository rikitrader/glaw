<!-- INGESTED REFERENCE — distilled from the DOJ "Civil RICO" manual (18 U.S.C. §§ 1961-1968),
     justice.gov/sites/default/files/usam/legacy/2014/10/17/civrico.pdf (legacy USAM, doc created
     2007-10-11; 597 pp). DOJ manuals are U.S. Government works (public domain). Ingested into GLAW
     2026-06-09 via glaw-doc-extract → opendataloader-pdf. This is a distilled, cited summary for the
     federal RICO library — verify each cite ([VERIFY] anything you rely on) and consult the OCRS
     *Criminal RICO Manual* for the criminal-side elements the civil manual cross-references. -->

# Civil RICO — DOJ doctrine (18 U.S.C. §§ 1961-1968)

## The two civil tracks (a load-bearing distinction)
- **§ 1964(a) — equitable relief: the United States ONLY.** The Attorney General has the **exclusive**
  authority to sue for equitable relief (injunctions, divestiture, dissolution, monitors). **A private
  plaintiff CANNOT obtain an injunction under RICO** — Congress deliberately omitted a private
  injunctive action; the private remedy is treble damages only. *Sedima v. Imrex*, 473 U.S. 479,
  486-87 (1985); *Agency Holding Corp. v. Malley-Duff*, 483 U.S. 143, 152 (1987).
  - **US § 1964(a) elements:** (1) the defendant **committed or intended to commit a RICO violation**
    (the same elements as criminal RICO, **except criminal intent is not required**); and (2) a
    **reasonable likelihood of a future violation**. Proof by a **preponderance**.
- **§ 1964(c) — treble damages: PRIVATE litigants only (not the US).** A plaintiff must show a **RICO
  violation that was the PROXIMATE CAUSE of injury to the plaintiff's business or property.**
  *Holmes v. SIPC*, 503 U.S. 258, 268 (1992); *Anza v. Ideal Steel Supply*, 547 U.S. 451 (2006);
  *Beck v. Prupis*, 529 U.S. 494 (2000). (Proximate cause is the recurring private-RICO killer —
  *Anza*: an indirect/derivative injury to a competitor is too remote.)

## The substantive offenses — § 1962
- **(a)** use/invest income derived from a pattern of racketeering (or collection of unlawful debt)
  to acquire an interest in / operate an enterprise.
- **(b)** acquire or maintain, through a pattern, an interest in or control of an enterprise.
- **(c)** **conduct or participate** in the conduct of an enterprise's affairs **through a pattern of
  racketeering** — the most-pleaded. **Reves "operation or management" test:** the defendant is not
  liable under § 1962(c) unless it **participated in the operation or management of the enterprise
  itself**. *Reves v. Ernst & Young*, 507 U.S. 170, 185 (1993). (Outside advisers/professionals who
  merely provide services usually fail Reves.)
- **(d)** **conspiracy** to violate (a), (b), or (c).

## Enterprise — § 1961(4)
"Any individual, partnership, corporation, association, or other legal entity, and any union or group
of individuals **associated in fact** although not a legal entity." For § 1962(c) the **enterprise
must be DISTINCT from the defendant "person."** An **association-in-fact** must be pleaded as members
who **functioned as a continuing unit over time to achieve a shared objective** (allege the structure
+ a factual basis). *Boyle v. United States*, 556 U.S. 938 (2009) (a/i/f needs a purpose, relationships,
and longevity — but not a formal hierarchy).

## Pattern of racketeering — §§ 1961(5), 1962(c)
At least **two acts of racketeering, the last within ten years** of a prior act — **plus** the
**H.J. Inc. continuity + relationship** test: the predicates are *related* (same purpose/result/
participants/victims/methods) **and** amount to or threaten **continuing** racketeering (closed-ended:
a substantial period; or open-ended: a threat of continuation). *H.J. Inc. v. Northwestern Bell*,
492 U.S. 229, 237-43 (1989). (Two acts are necessary but **not sufficient** — sporadic/short-lived
schemes fail continuity.)

## Predicate "racketeering activity" — § 1961(1)
A closed list of state felonies (murder, kidnapping, gambling, arson, robbery, bribery, extortion,
drugs, obscenity) **and** federal offenses — incl. **mail fraud (§ 1341), wire fraud (§ 1343)**, bank
fraud, Hobbs Act extortion, money laundering (§§ 1956-1957), bribery, embezzlement from pension/union
funds, securities fraud, immigration offenses, and others. (Fraud predicates must be pleaded with
**Rule 9(b)** particularity.)

## Statute of limitations — 4 years (civil)
Civil RICO borrows the **4-year** antitrust limitations period (RICO's § 1964 was patterned on the
antitrust laws). *Agency Holding Corp. v. Malley-Duff*, 483 U.S. 143, 156 (1987). Accrual follows the
**injury-discovery** rule, and **separate accrual** can apply to new injuries. *Rotella v. Wood*,
528 U.S. 549 (2000); *Klehr v. A.O. Smith*, 521 U.S. 179 (1997).

## Other DOJ-noted points
- **The United States is NOT a "person"** under RICO and cannot be a RICO defendant. *United States v.
  Bonanno Organized Crime Family*, 879 F.2d 20 (2d Cir. 1989).
- **Respondeat superior:** a collective entity (corporation/union) is liable for its agents' acts
  within scope and **motivated at least in part to benefit the principal**.
- **Aiding-and-abetting:** most courts bar a *private* plaintiff's a/a-of-the-whole-violation theory
  after *Central Bank* — but a defendant who aids/abets the **predicate acts** is punishable as a
  principal (18 U.S.C. § 2) and can satisfy the "two acts" element.

## How GLAW uses this
- Charging/standing screen: `glaw-fed-cause show "RICO"` (the §1962(a-d) entries carry these elements);
  the **defenses/killers** the other side raises (enterprise-distinctness, Reves operation-or-management,
  no pattern/continuity, Anza proximate cause, 4-yr SOL, no private injunction) are in
  `glaw-fed-defense show "RICO"` / `for "RICO"`.
- **Drafting flag:** a *private* civil-RICO complaint pleads § 1964(c) treble damages + proximate cause
  — **not** an injunction (that is the US's § 1964(a) lane). Plead the enterprise in a distinct section
  (Boyle continuing-unit allegations) and the predicates with Rule 9(b) particularity.
