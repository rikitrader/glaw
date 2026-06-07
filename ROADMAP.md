<div align="center">

# GLAW Roadmap — from Law Firm to Autonomous Agency

**North star:** evolve GLAW from a virtual *law firm* into a self-driving **AI agency** — an
organism that senses a legal/governance situation, reasons across departments, drafts and
acts, checks itself against its own conscience, and learns — *ready for the fight and ready
for the advice.*

</div>

> **Read this first — the honest frame.** GLAW automates the *analytical and operational*
> work of a firm/agency: research, drafting, investigation, modeling, monitoring, and
> decision-support. It does **not** claim, and must never claim, the legitimate authority of
> a court, a regulator, or a sovereign. Anything **binding, coercive, or irreversible**
> (filing, charging, sanctioning, paying, signing on behalf of a person) stays behind a
> human with lawful authority. "100% autonomous agency" means a closed analytical loop with
> humans holding the seal — not autonomous government power. The guardrails in
> [§7](#7-the-constitution-of-the-agency-non-negotiable) are load-bearing, not decoration.

---

## 1. Where we are (v1.0 — shipped)

A working virtual firm: **59 skills · 10 departments · 8-stage matter pipeline · 4 hard
gates · 20 tools**, with the contract-review chain (review → score → real Word tracked
changes → publish) proven end-to-end. The Investigations Bureau + Intelligence
Super-Structure (FinCEN/Intel/SEC cells) already seed the "agency" muscles. `glaw-doctor`
keeps it healthy.

**What's missing to become an *organism*:** it still waits to be told. It has departments
but no *autonomic loop* — no continuous perception, no self-set goals, no persistent
working memory across matters, no adopted conscience in a host runtime. The rest of this
document closes that gap.

---

## 2. The Autonomous Organism (the thinking loop)

GLAW's autonomy is a continuous loop, mapped onto pieces that already exist plus pieces
this roadmap adds. It deliberately mirrors `zeroclaw-x0`'s own crates (`conscience`,
`memory`, `runtime`):

```
        ┌──────────── SENSE ────────────┐
        │ dockets, filings, news, data, │
        │ inbound docs, deadlines, RSS  │
        └───────────────┬───────────────┘
                        ▼
   ORIENT  → classify the matter, route to departments (firm-roster)
                        ▼
   DECIDE  → strategy + structure; the Chief sets the goal & plan
                        ▼
   ACT     → draft / redline / file-prep / investigate / model
                        ▼
   VERIFY  → the 4 gates + adversarial RED→BLUE + glaw-doctor   ← the CONSCIENCE
                        ▼
   LEARN   → write matter memory, update playbooks, retro       ← persistent MEMORY
                        └────────────► back to SENSE
```

- **Conscience = the gates.** Conflicts, citation-verification, adversarial-survival, and
  the UPL/lawful-analysis disclaimer are the organism's refusal reflexes. In a host runtime
  they become a *veto* on any action that fails them.
- **Memory = matters + playbooks.** Every matter already leaves `matter.md` / `docket.jsonl`
  / `timeline.jsonl`. The roadmap promotes this to a queryable long-term memory the
  organism reasons over.
- **Drive = goals.** Today a human supplies the goal. The Autonomy Core (Phase 2) lets the
  Chief hold standing goals ("keep every entity compliant," "watch this docket") and act on
  them on a schedule.

---

## 3. Phased roadmap

| Phase | Version | Theme | Headline capabilities | Exit criteria |
|---|---|---|---|---|
| **1** | `1.0` ✅ | **The Firm** | 59 skills, pipeline, gates, contract chain, doctor | shipped & open-sourced |
| **2** | `1.x` | **Autonomy Core** | self-driving matter loop, docket/deadline daemon, standing goals, persistent memory, `glaw-loop` | a matter can advance itself between gates without a prompt |
| **3** | `2.0` | **Harness Integration** | adapters for zeroclaw-x0 (Extism plugin + conscience), OpenClaw, ZeroClaw; MCP server; CLI bridge | GLAW runs as a capability *inside* an autonomous host |
| **4** | `3.0` | **The Branches** | Constitutional Law branch; Legislative-drafting, Administrative-law, and Judicial/adjudication departments | GLAW can analyze a statute/policy end-to-end and draft + adjudicate a model rule |
| **5** | `4.0` | **The Agency** | Treasury/fiscal, Regulatory rule-making, Justice/enforcement-prep, Diplomacy/treaties, Public-records/FOIA, Elections-integrity analysis | full agency org chart, each function gated |
| **6** | `5.0` | **Closed Loop + Oversight** | continuous multi-domain operation under a human Oversight Board, simulation/red-team sandbox, formal audit ledger | 100% analytical autonomy with the seal held by humans |

### Phase 2 — Autonomy Core (the next sprint)
- `bin/glaw-loop` — a goal-driven driver (think `/goal` for matters): takes a standing
  objective, runs SENSE→…→LEARN, stops at any gate that needs a human, resumes when cleared.
- **Docket daemon** — `glaw docket` already calendars deadlines; add a watcher that wakes,
  surfaces what's due, and drafts the response packet *before* the deadline.
- **Perception adapters** — pluggable SENSE sources: `glaw-court-scrape` (dockets),
  RSS/news, an inbound-docs folder, regulator feeds (SEC EDGAR, Federal Register).
- **Persistent working memory** — promote matter state to a queryable store (vector +
  structured); the Chief recalls precedent across matters.
- **`glaw-chief-decision` → autonomous mode** — the Chief records PROCEED / WITH-FIXES /
  WITH-CONDITIONS *and*, under explicit policy, executes the non-binding ones.

### Phase 3 — Harness Integration (see [§6](#6-harness-integration))
### Phase 4 — The Branches (see [§5](#5-constitutional-law--the-next-move))

---

## 4. The Constitution of the firm → the Agency

The seed is already here: the Investigations **Bureau**, the **Intelligence
Super-Structure** (FinCEN / Intel / SEC cells), and the **regulatory** seats. The agency is
those muscles plus the missing organs of governance — built as new departments, each behind
the same gates.

```
              GLAW AGENCY (target org)
   ┌──────────────┬──────────────┬──────────────┐
   │  ANALYZE     │   DRAFT      │   ADJUDICATE  │
   │ (existing)   │ (Phase 4)    │  (Phase 4-5)  │
   ├──────────────┼──────────────┼──────────────┤
   │ Investigations  Legislative    Judicial/      │
   │ Intelligence    Constitutional Administrative │
   │ Securities      Regulatory     Hearings/ALJ   │
   │ Tax/Treasury    Rule-making    Appeals model  │
   └──────────────┴──────────────┴──────────────┘
        all under the CONSCIENCE (gates) + OVERSIGHT BOARD (humans)
```

---

## 5. Constitutional Law — the next move

The first new branch. A **`/glaw-constitutional`** department plus supporting seats:

- **`/glaw-constitutional`** — constitutional analysis: standing, justiciability, levels of
  scrutiny (rational-basis / intermediate / strict), enumerated vs. reserved powers,
  separation-of-powers, federalism, due process, equal protection, First/Fourth/Fifth/
  Fourteenth-Amendment frameworks. Produces a **constitutional memo** + a scored risk matrix.
- **`/glaw-legislative`** — statutory & rule **drafting**: bills, model statutes, agency
  rules, with a legislative-history and impact section. Pairs with `glaw-cites` and a
  (new) statute corpus.
- **`/glaw-admin-law`** — administrative law: APA notice-and-comment, *Chevron/Loper Bright*
  deference analysis, rule-making records, arbitrary-and-capricious review.
- **`/glaw-judicial`** — model adjudication: an opinion-drafting + bench-memo seat that takes
  a record and the adversarial briefs and produces a reasoned, citation-checked **draft
  opinion** — explicitly a *model* for study/preparation, never a binding judgment.

**New tooling for the branch**
- `glaw-constitution-score` — deterministic scoring of a measure against constitutional risk
  factors (scrutiny tier, nexus, less-restrictive-means), mirroring `glaw-contract-score`.
- A **statute/precedent corpus** adapter (Caselaw Access Project / Court Listener / public
  U.S. Code & CFR) feeding `glaw-legal-research` so citations are *verifiable*, not invented.

**Exit criteria:** take a real (public) statute or policy, run constitutional + admin-law
analysis, draft a model rule *and* a model opinion on a challenge to it, with every citation
verified and an adversarial pass survived.

---

## 6. Harness integration

GLAW should run as a capability *inside* any autonomous host. Three first-class targets,
one generic path.

### 6a. `zeroclaw-x0` (your main autonomous agent — Rust/Extism)
zeroclaw-x0 already has the right shape: `zeroclaw-plugins` runs **Extism plugins** with
permission-gated host functions (`zc_http_request`, `zc_env_read`) and plugin exports
(`tool_metadata`, `execute`); it has a `zeroclaw-conscience` crate and `zeroclaw-memory`.

- **GLAW-as-plugin:** ship a thin Extism plugin (`glaw-plugin`) that exports `tool_metadata`
  for each GLAW CLI and `execute` to run it under zeroclaw's permission gates. The 20 tools
  become 20 zeroclaw tools.
- **Conscience adoption:** map GLAW's 4 gates into `zeroclaw-conscience` so the host's own
  refusal layer enforces conflicts/citations/adversarial/UPL on *any* legal action.
- **Memory bridge:** persist GLAW matter state through `zeroclaw-memory` so the agent
  remembers matters across runs.
- **Hardware-aware caveat:** zeroclaw-x0 also has `robot-kit`/`zeroclaw-hardware`; GLAW
  actions must stay informational — no GLAW path may drive a physical actuator.

### 6b. OpenClaw / ZeroClaw (orchestrators)
Spawned-session contract: GLAW skills already detect spawned sessions and auto-pick
recommended options instead of prompting. Add a `glaw --headless --goal "<objective>"` entry
that emits a structured completion report (what shipped, decisions, open gates) for an
orchestrator to consume.

### 6c. Generic — MCP + CLI
- **`glaw-mcp`** — expose the toolbelt + matter state as an MCP server so *any* MCP client
  (Claude Code, Cursor, Gemini, Codex) gets GLAW tools.
- **CLI bridge** — every capability is already a `bin/` CLI with JSON I/O; that's the
  lowest-common-denominator integration for any harness.

> Integration spec lives in [`docs/integration.md`](docs/integration.md) (Phase 3).

---

## 7. The Constitution of the Agency (non-negotiable)

The more autonomous GLAW gets, the more these bind. They are the organism's conscience.

1. **Humans hold the seal.** No autonomous path may *file, serve, charge, sanction, pay,
   sign for a person, or otherwise bind/coerce anyone.* Those require an authorized human act.
   GLAW prepares; a person commits.
2. **The gates cannot be disabled.** Conflicts → citations → adversarial → UPL run on every
   matter, autonomous or not. A position the firm's own adversary destroys is not acted on.
3. **Lawful analysis only.** Investigations/intel seats are analytical work-product. No
   covert ops, surveillance, intrusion, or illegal collection — ever.
4. **Verifiable authority, no hallucinated law.** Every legal citation is checked against a
   real corpus before it leaves the building. Unverifiable = struck.
5. **Full audit ledger.** Every autonomous decision is logged (timeline + decision card +
   reproducible inputs) and reviewable. Nothing happens off the record.
6. **Kill-switch + Oversight Board.** A human can halt the loop instantly; standing goals are
   set and revoked by people; high-impact actions escalate to a human Oversight Board.
7. **Democratic-legitimacy caveat.** An AI does not possess sovereign or judicial authority.
   The "Agency" is decision-support and operational drafting for legitimate human
   institutions — never a replacement for them.

---

## 8. Gap analysis — what stands between here and the Agency

| Gap | Today | Needed | Phase |
|---|---|---|---|
| **No autonomic loop** | waits for a prompt | `glaw-loop` + docket daemon + standing goals | 2 |
| **No persistent cross-matter memory** | per-matter files | queryable long-term memory | 2 |
| **No host embedding** | standalone skill | Extism plugin + MCP + conscience adoption | 3 |
| **Citations not corpus-backed** | model + `glaw-cites` | wired statute/case corpus (CAP/CourtListener/U.S.C./CFR) | 4 |
| **No constitutional/legislative/judicial seats** | firm-only | the Branches (`/glaw-constitutional` …) | 4 |
| **Thin automated tests** | `glaw-doctor` smoke only | golden-output tests per seat + sandbox sim | 2–6 |
| **Real filing connectivity is partial** | scaffolds (IRS/EFW2) | transmitter creds + EDGAR/court e-file (human-sealed) | 4–5 |
| **No formal oversight tooling** | gates in prose | Oversight Board workflow + kill-switch + audit ledger | 6 |
| **Single-jurisdiction bias** | US-centric | jurisdiction packs (state, federal, international) | 4–5 |

---

## 9. Contributing to the roadmap

Pick a Phase-2 item (the Autonomy Core is the unlock), or propose a Branch seat under
[CONTRIBUTING.md](CONTRIBUTING.md). Rules that never bend: a new seat goes in
`lib/firm-roster.md`, passes `bin/glaw-doctor`, keeps the gates load-bearing, and honors
[§7](#7-the-constitution-of-the-agency-non-negotiable). Build the organism — keep the seal
in human hands.

<div align="center"><sub>GLAW · ready for the fight · ready for the advice · the seal stays human</sub></div>
