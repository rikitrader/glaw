---
name: glaw-draft
version: 1.0.0
description: "GLAW pipeline stage 4 — the documents. Corp-build: certificate/articles of incorporation, bylaws or operating agreement, organizational board/member consents, founder agreements + IP assignment, equity docs (SAFE / stock purchase / option plan), and for offerings the PPM + subscription agreement + Form D draft. Litigation: the complaint or answer, motions, discovery requests, and demand letters. Every drafted document carries the UPL footer; all citations defer to /glaw-legal-research. Use after the structure memo, or when asked to 'draft the documents', 'draft the complaint', 'draft the operating agreement', 'draft the PPM', 'write the bylaws', 'draft a demand letter', 'prepare the formation docs'."
allowed-tools:
  - Skill
  - Agent
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
triggers:
  - draft the documents
  - draft the complaint
  - draft the operating agreement
  - draft the PPM
  - formation docs
  - demand letter
---

## When to invoke this skill

Fourth stage of the GLAW pipeline. Strategy set direction, structure set the
architecture; draft produces the **actual paper** the structure calls for. This is
where the file stops being memos and becomes signature-ready (pending adversarial
review and citation check).

Draft does not bless citations. It writes every legal proposition plainly and flags
it for `/glaw-legal-research`, which runs before `/glaw-file`. And nothing leaves
without the UPL footer.

## Preamble (run first)

```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

Read `~/.claude/skills/glaw/lib/firm-roster.md` before routing. Read
`structure-memo.md` and `strategy-memo.md` — draft executes them exactly; it does
not re-decide architecture.

## UPL footer (stamp on EVERY drafted document)

Pull the disclaimer from `/glaw-ethics-conflicts` and place it at the foot of every
document this stage produces:

> **Attorney work-product — not legal advice.** Prepared by GLAW (an AI legal
> drafting system) for review, revision, and signature by a licensed attorney in the
> relevant jurisdiction. Use of this material does not create an attorney-client
> relationship. Verify all citations and deadlines independently before filing.

## Workflow

Branch on `MATTER_TYPE` from `matter.md`. For long, multi-document drafting sets,
parallelize independent documents with the **Agent** tool, each routed to its seat.

### Corp/fund build — Formation, Governance, Offering

Drive the document set off the structure memo's org chart and cap table.

1. **Charter documents.** Certificate of incorporation (Delaware) or articles of
   organization, matching the entity type, jurisdiction, and authorized shares from
   structure. Route to **`glaw-corporate-counsel`**.
2. **Governance.** Bylaws (corp) or operating agreement (LLC) / LP agreement (fund),
   reflecting the cap table, control terms, and tax elections. Route to
   **`glaw-corporate-counsel`**; fund LPAs to **`glaw-pe-vc-counsel`**.
3. **Organizational consents.** Initial board/member written consents: adopt
   charter+bylaws, appoint officers/managers, authorize stock issuance, ratify the
   tax elections (S-election, 83(b) reminders, QSBS posture). Route to
   **`glaw-corporate-counsel`**.
4. **Founder package.** Founder agreements, restricted-stock purchase agreements with
   vesting, and **IP assignment** (assign all pre-formation IP into the entity).
   Route to **`glaw-corporate-counsel`**; specialized IP assignment to **`/glaw-ip-counsel`**.
5. **Equity docs.** SAFE / convertible note, stock purchase agreement, and the
   equity-incentive (option) plan + form grant, consistent with the cap table. Route
   to **`glaw-pe-vc-counsel`** / **`glaw-corporate-counsel`**.
6. **Offering package (if raising).** PPM, subscription agreement, and the **Form D**
   draft for the Reg D exemption chosen in strategy. Route to
   **`glaw-fund-regulatory-council`** (Form D / Blue Sky / PPM supplements) and
   **`glaw-pe-vc-counsel`** (PPM/sub-agreement). For tokenized offerings, route to
   **`glaw-tokenization-compliance`**. Tax disclosure sections route to **`glaw-tax-compliance`**.
7. **Render.** Produce final formatted documents via **`glaw-document-generate`**,
   **`glaw-docx`**, or **`glaw-make-pdf`** — each carrying the UPL footer.

### Litigation case — Pleadings, Motions, Discovery, Demands

Drive the document set off the parties-to-claims matrix.

> **Florida civil matter? Use the Title VI document factory first.** Select the cause(s) of action
> with `glaw-fl-statute causes` (or `chapter <N>` / `search <term>`), then draft from the ready-to-file
> **`/glaw-fl-quantum-meruit`** library: quantum-meruit/unjust-enrichment (`fl-quantum-meruit/templates/0*`)
> and the full Title VI set (`fl-quantum-meruit/templates/title6/complaint-*.md`, `enforcement-*.md`,
> `petition-*.md`, `motion-*.md`) + the discovery/intake/subpoena packs. **Run the dispositive-gate
> checks for the chosen cause** (e.g. §489.128 licensing, *Commerce* express-contract bar, pay-if-paid
> *DEC Electric*, §713.22 lien clock, §68.065 demand, §70.001 150-day presuit) before the count is drafted.

1. **Complaint or answer.** Complaint: caption, jurisdiction+venue allegations,
   parties, factual background, then one count per claim from the matrix — each
   pleading its elements against the pleaded facts — and a prayer for relief tracking
   the damages theory. Answer: responses + every affirmative defense + counterclaims.
   Route to **`/glaw-fl-quantum-meruit`** (FL civil), **`glaw-federal-trial-counsel`** (federal),
   and **`glaw-elite-corporate-counsel`**.
2. **Motions.** Whatever the posture calls for — motion to dismiss, for summary
   judgment, to vacate (Rule 1.540 / fraud-on-court), preliminary injunction/TRO.
   Route to **`glaw-elite-corporate-counsel`** / **`glaw-federal-trial-counsel`**.
3. **Discovery requests.** Interrogatories, requests for production, requests for
   admission, and deposition notices — built to close the fact gaps flagged in
   strategy/structure. Route to **`glaw-federal-trial-counsel`**.
4. **Demand letters.** Pre-suit demand or statutory demand (e.g. civil-theft
   pre-suit demand) where strategy chose the demand-first path. Route to
   **`glaw-elite-corporate-counsel`**.
5. **Render.** Format via **`glaw-document-generate`** / **`glaw-docx`** / **`glaw-make-pdf`**, UPL
   footer on each.

## Output

A complete document set written to `~/.glaw/matters/<slug>/drafts/`, every document
carrying the UPL footer, every legal proposition flagged for `/glaw-legal-research`,
and a manifest listing each draft + its responsible seat + its open citation items.

Then advance:

```bash
~/.claude/skills/glaw/bin/glaw stage adversarial
~/.claude/skills/glaw/bin/glaw timeline-log draft_done
```

Hand off to `/glaw-adversarial` — nothing drafted here reaches `/glaw-file` until
the RED→BLUE pass survives and `/glaw-legal-research` verifies every citation.
