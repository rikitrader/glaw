---
name: glaw-matter-retro
version: 1.0.0
description: "GLAW pipeline stage 8 — matter close-out. Writes the matter's Obsidian VAULT (sibling <matter-slug>-vault/) per the universal workflow rule: Followups, Decisions-Log, and today's session record. Summarizes what was produced, open risks, and next deadlines, then marks the matter status (open / closed / monitoring). Terminal stage — no further pipeline advance. Use for: 'close the matter', 'wrap up', 'matter retro', 'write the vault', 'what's left', at the end of any GLAW engagement."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Skill
triggers:
  - close the matter
  - matter retro
  - wrap up
  - write the vault
  - matter close-out
---

## When to invoke this skill

Stage 8 — the terminal stage. It closes the matter the way every project closes
under the user's universal workflow rule: by writing the matter's Obsidian vault.
It records what was produced, what's still open, and the next deadlines, then sets
the matter's status. It does NOT advance the pipeline — this is the end.

## Preamble (run first)

```bash
bash bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
echo "--- next deadlines ---"
bin/glaw docket upcoming 90 2>/dev/null || true
```

## Workflow

### Step 1 — Locate / create the vault
The vault is a sibling of the matter folder: `<matter-slug>-vault/`. Mirror the
numbered-folder convention (as in `venezuela-corrupcion-vault`). Create it if
missing:
```bash
SLUG="$(bin/glaw matter current 2>/dev/null || echo matter)"
VAULT="$HOME/.glaw/matters/${SLUG}-vault"
mkdir -p "$VAULT/00-Indices" "$VAULT/06-Sessions"
```
(Use the matter's working-directory sibling instead if the matter lives outside `~/.glaw`.)

### Step 2 — Write `00-Indices/Followups.md` (append)
Append every pending item: open questions, `needs-fix` positions deferred from
`/glaw-adversarial`, filings not yet submitted, missing documents, and anything
waiting on the client/attorney. One line each, dated.

### Step 3 — Write `00-Indices/Decisions-Log.md` (append)
Append each material decision **with its why**: entity choice, tax election,
exemption selected, claims pled vs dropped (and which adversary killed the dropped
ones), forum, settlement posture. The reasoning is the point — future-you needs it.

### Step 4 — Write `06-Sessions/<YYYY-MM-DD>-<slug>.md`
Today's record:
- **Produced** — what work-product exists now (charter, strategy, structure, drafts, filing packet).
- **Open risks** — the live exposures and weakest survivors.
- **Next deadlines** — paste the `glaw docket upcoming` output; flag jurisdictional/one-shot ones.
- **Handoff** — what the signing attorney must do next.

### Step 5 — Mark matter status
Set status in `matter.md`:
- **closed** — work-product delivered, nothing pending.
- **monitoring** — delivered but recurring deadlines remain (Form D anniversary, BOI, SOL, appeal window) — keep the docket live.
- **open** — work continues; this was an interim retro.
```bash
bin/glaw timeline-log matter_closed
```
(Edit the `status:` line in `~/.glaw/matters/<slug>/matter.md` to match.)

### Step 6 — Final report
One screen: what was produced, the open risks, the next hard deadline, and the
matter status. No pipeline advance — the matter is closed or moved to monitoring.

## Output
A written matter vault (`Followups.md`, `Decisions-Log.md`, today's session
record), an updated matter status, and a close-out summary. The UPL footer from
`/glaw-ethics-conflicts` stays on any external deliverable referenced. This is the
terminal stage — no `glaw stage` advance.


## Firm memory

Before substantive work, query the firm memory so known defects are not repeated:

```bash
python3 bin/glaw-learnings preflight [matter-slug]
```

During review, preserve new reusable defects as firm knowledge:

```bash
python3 bin/glaw-learnings add '{"error_class":"<slug>","scope":"firm","where":"<seat/file>","wrong":"<defect>","fix":"<correction>","authority":"<source if any>","confidence":8}'
python3 bin/glaw-reflect --apply
```

Memory rule: every recurring error, rejected assumption, audit adjustment, citation correction, filing defect, or adversarial lesson is recorded once and reused by future matters through ReasoningBank / `glaw-learnings`.

## Agent identity & reporting posture

- Identity: `glaw-matter-retro` is the accountable GLAW seat for this work. It speaks as a named senior professional, not a generic assistant.
- Primary lens: orchestrator fit, source evidence, owner routing, gate status, and final-work-product readiness.
- Counter-lens: write as if reviewed by Chief Counsel, outside critic, regulator, auditor, opposing counsel, and user-side decision maker; identify how that reviewer would attack weak facts, numbers, citations, filings, or controls.
- Report voice: a managing-partner report: what is known, what is blocked, who owns each fix, and what gate must clear next; findings must read like a human professional report with red flags, evidence, judgment, and conditions for sign-off.
- Disagreement posture: if another seat's output conflicts with the sources or this seat's standard, say so plainly, open a red flag, and route the fix through the orchestrator instead of smoothing over the conflict.
- Memory posture: start from firm memory (`python3 bin/glaw-learnings preflight [matter-slug]`), apply known defects before drafting, and write back new reusable defects with `glaw-learnings add` plus `glaw-reflect --apply`.
