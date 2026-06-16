# GLAW Depth-Hardening Punch-List

**Created:** 2026-06-16 · **Source:** 4-agent depth audit (corpus/citation, autonomy/safety, branches/harness, test/eval) · **Owner of this file:** Claude (docs lane).

The breadth is done and the safety spine is **verified real** (authority gate, loop maker-checker, kill-switch, daemon, RBAC, MCP/host adapter — all enforce in code). The remaining gaps cluster in **substantive content behind real gates** and **defense-in-depth residuals**. This list is ordered by leverage.

**Status legend:** `OPEN` · `IN-PROGRESS` (Codex active in working tree) · `DONE`.
**SSOT note:** items touching `lib/glaw_profiles.py` or `lib/firm-roster.md` are flagged `[SSOT]` — single-owner lock, set `GLAW_SSOT_OWNER` before committing.

---

## P0 — Verifiable-law pillar (the production blocker)

### H-1 · Citation corpus does not resolve to an authoritative source — `DONE`
- **Files:** `bin/glaw-citation-corpus`, `bin/glaw-citation-gate`, inline dup at `bin/glaw-gate`.
- **Current state:** stores user-pasted text; `--fetch` is a bare `urlopen` on **any** URL with **no domain allowlist**. Verification is hash/consistency vs the user's *own* captured source. A fabricated case passes if the user pastes matching text. This means §7.4 ("no hallucinated law") is **not** enforced today.
- **Required fix:**
  1. Add a source-URL **domain allowlist** for `--source-url`/`--fetch`: `courtlistener.com`, `www.courtlistener.com`, `govinfo.gov`, `uscode.house.gov`, `ecfr.gov`, `www.law.cornell.edu` (extendable via config). Reject off-allowlist URLs at capture time.
  2. Real **fetch-and-match**: on `--fetch`, retrieve the allowlisted URL and assert the cited `--segment` is actually present in the *fetched* body (not just the user-pasted text), before recording the corpus row.
  3. Keep the existing hash/tamper trail.
- **Acceptance:** a citation whose `--source-url` is off-allowlist is **rejected**; a `verified` citation whose segment is absent from the *fetched* allowlisted source is **rejected**. Add both as negative fixtures.
- **Closed:** `glaw-citation-corpus` now rejects off-allowlist URLs, treats pasted text as untrusted, permits `--fetch` only from approved authority domains, supports offline `--file --authenticated-copy` official copies, and `glaw-citation-gate` / `glaw-gate` reject verified rows backed by untrusted pasted corpus text.
- **Coordination:** Codex has these files open. Do not edit; this is the target bar for Codex's in-flight work.

### H-2 · Groundedness is lexical, not semantic, and has no negative test — `DONE`
- **Files:** `lib/glaw_groundedness.py`, `bin/glaw-groundedness`, `test/groundedness_test.sh`.
- **Current state:** bag-of-words overlap (≥0.30 entity / ≥0.20 relation) vs the user's *own* segment; 30% shared words passes. "HalluGraph entity-grounding / relation-preservation" is named but not implemented. Only a happy-path test exists.
- **Required fix:** (a) add a **negative fixture** — an unsupported proposition must FAIL the gate (highest priority, cheap); (b) raise the floor or move toward real entity/relation extraction (triples) rather than token overlap; (c) document the honest limitation in the gate output.
- **Acceptance:** `groundedness_test.sh` includes a "must FAIL on unsupported claim" case that is asserted to be rejected.
- **Closed:** `groundedness_test.sh` includes unsupported-claim and fabricated-pasted-corpus negative fixtures; `glaw_groundedness.py` blocks untrusted corpus rows directly and labels its output as a deterministic lexical floor, not semantic proof.
- **Coordination:** Codex active here — do not edit.

---

## P1 — Substantive content behind real gates

### H-3 · Jurisdiction-pack ships zero real legal data — `DONE`
- **Files:** `bin/glaw-jurisdiction-pack` (+ wherever the pack data would live).
- **Current state:** schema validator with one placeholder Delaware scaffold ("example filing deadline", "SRC-0001 …"). Enforces discipline on a matrix someone else must populate; easy to mistake for "done."
- **Required fix:** seed at least the high-frequency jurisdictions actually used by live matters (DE, FL, TX, NY + federal) with **source-backed** entity/tax/licensing/filing-authority rows, each carrying a real `SRC-####`. Keep the validator; give it real data to validate.
- **Acceptance:** `glaw-jurisdiction-pack validate` passes on a **populated** (non-scaffold) DE+FL+TX+federal pack with zero `review`/placeholder warnings.
- **Closed:** `jurisdiction/packs/us-core.json` now seeds DE, FL, TX, NY, and federal corporate filing authority with official source URLs and source catalog entries; `glaw-jurisdiction-pack` lists bundled packs, validates source catalog URLs, rejects scaffold/placeholder text, and `jurisdiction_pack_test.sh` asserts the scaffold fails while the populated pack passes with zero review warnings.

### H-4 · Branch seats are thin routing shells — `DONE` `[SSOT]` (roster touch)
- **Files:** `constitutional/SKILL.md`, `legislative/SKILL.md`, `judicial/SKILL.md`, `admin-law/SKILL.md`; ref in `lib/firm-roster.md`.
- **Current state:** ~100-line shells with correct doctrine vocabulary but no embedded frameworks/checklists/model language (vs an 831-line mature seat). The `constitution-score` scorer itself is REAL.
- **Required fix:** add per-branch `references/` + `templates/` (e.g., scrutiny-tier checklist, APA notice-and-comment record template, bench-memo skeleton, model-opinion structure). Bring each to parity with a mid-weight seat.
- **Acceptance:** each branch seat ships at least one substantive reference doc and one model-output template; doctor self-containment still green.
- **Closed:** constitutional, legislative, judicial, and admin-law seats now each ship a substantive reference checklist and model-output template, their `SKILL.md` files route users to those workpapers, and `branch_substance_test.sh` is enforced by `glaw-doctor`/`glaw-policy`.

---

## P2 — Safety defense-in-depth residuals (not active bypasses)

### H-5 · Leaf binding tool doesn't self-check the kill-switch — `DONE`
- **Files:** `bin/glaw-irs-file` (the `submit --live` branch).
- **Current state:** the kill-switch is enforced in the loop/daemon orchestration layer, but `glaw-irs-file --live` itself does not call `oversight_status`. An ADMIN human could transmit **while the firm is halted**.
- **Required fix:** add an `oversight_status` halt check inside the `submit --live` branch (belt-and-suspenders), before the network POST.
- **Acceptance:** `glaw-irs-file submit --live …` returns blocked when the oversight kill-switch is engaged, even with valid ADMIN authority. Add a fixture.
- **Closed:** `glaw-irs-file submit --live` checks `glaw_oversight.status()` before live transmission and `authority_gate_test.sh` asserts ADMIN live transmit is blocked while halted.

### H-6 · Host/MCP execution path doesn't invoke RBAC — `DONE`
- **Files:** `lib/glaw_host.py` (`execute()`), `lib/glaw_mcp.py`.
- **Current state:** host layer enforces conscience pre/post guards only. RBAC ADMIN/human-seal appears in the host manifest `safety_contract` as a documented promise but isn't invoked when a tool runs through `glaw-host`/`glaw-mcp`. (Leaf tools still self-gate, so this is defense-in-depth, not an open hole.)
- **Required fix:** invoke the RBAC permission check at the host execution boundary so the host layer enforces what its manifest advertises.
- **Acceptance:** an MCP-driven call to a human-only action is RBAC-blocked at the host layer (not only at the leaf tool).
- **Closed:** `lib/glaw_host.execute()` now invokes RBAC before conscience/tool execution, `glaw-host` exposes `--role/--actor`, and `glaw-mcp` threads role/actor through `glaw_execute`.

### H-7 · RBAC role is self-asserted — `DONE` (document, don't over-engineer)
- **Files:** `lib/glaw_rbac.py` (role resolution), `tax-legal-shared/guardrails.md`.
- **Current state:** role comes from `--role ADMIN` / `GLAW_RBAC_ROLE` env. "Human authority" = whoever can set the env var. Inherent to a single-operator local CLI; the audit trail is hash-chained (tamper-evident).
- **Required fix:** document the trust boundary explicitly in guardrails (no cryptographic operator identity at this tier); revisit only if GLAW runs multi-operator/hosted. No code change required now.
- **Acceptance:** trust boundary stated in `guardrails.md`.
- **Closed:** `tax-legal-shared/guardrails.md` now states that local CLI RBAC roles are operator assertions recorded in a tamper-evident ledger, not cryptographic identity.

### H-8 · Loop escalation counter resets instead of latching — `DONE`
- **Files:** `bin/glaw-loop`.
- **Current state:** after a human-escalation, the decision signature changes, so the next run resets the iteration counter (can re-loop strategy→cap→escalate cyclically). It always escalates every 4th iteration and never acts, so not a safety hole — but it churns.
- **Required fix:** latch `human_escalation_required` for a route until an oversight `resume`/clear, instead of resetting on signature change.
- **Acceptance:** once escalated, the same route stays escalated until explicitly cleared; add a loop-test assertion.
- **Closed:** `glaw-loop` now latches prior non-convergence escalation until Oversight Board resume and `loop_test.sh` asserts the latch.

---

## P3 — Test coverage thin spots (load-bearing but under-tested)

### H-9 · CCO compliance-audit classifier has no correctness test — `DONE`
- **Files:** `bin/glaw-compliance-audit`, `lib/checklists/*.json`, new `test/compliance_audit_test.sh`.
- **Current state:** it's a named hard gate (HAVE/ACTION/GAP classification against checklists) but only smoke-run with no args. The *manifest* is tested in `gate_test.sh`; the **classification engine itself** has zero correctness test.
- **Required fix:** add a dedicated test asserting HAVE/ACTION/GAP classification on a known fixture (a doc set with a deliberate gap must be classified GAP).
- **Acceptance:** `compliance_audit_test.sh` exists and is picked up by the doctor test-runner loop.
- **Closed:** `test/compliance_audit_test.sh` asserts HAVE/ACTION/GAP/optional-missing classification and is included in `bin/glaw-doctor`.

### H-10 · ~99 tax/practice-group CLI wrappers are smoke-or-less — `IN-PROGRESS`
- **Files:** e.g. `bin/glaw-scorp-aaa`, `glaw-partner-basis`, `glaw-subpart-f`, `glaw-combined-unitary`, `glaw-tfrp`, `glaw-ptet`, `glaw-oic`, `glaw-sfr`, `glaw-wbo-award`, `glaw-qm` (representative).
- **Current state:** load-bearing IRS/state calcs with no test / no lib-engine backing / not even in the doctor smoke array. (Many other tax tools *are* covered via `lib/bookkeeping/test_finance*.py` — these are the ones that are not.)
- **Required fix:** add at least a golden-value test per uncovered calc tool (one known input → known output), or fold them into the existing finance-engine test pattern.
- **Acceptance:** every `bin/glaw-*` calc tool has either a golden-value test or a lib-engine test touching its math.
- **Progress:** `test/tax_wrapper_golden_test.sh` covers the named representative tools in this item with exact wrapper-level golden values: `glaw-scorp-aaa`, `glaw-partner-basis`, `glaw-subpart-f`, `glaw-combined-unitary`, `glaw-tfrp`, `glaw-ptet`, `glaw-oic`, `glaw-sfr`, `glaw-wbo-award`, and `glaw-qm`. `test/tax_wrapper_coverage.json` plus `test/tax_wrapper_coverage_test.sh` now lock 22 wrapper-to-module-to-evidence mappings covering the named representatives and the W3/W4/W5 entity/state/international engine set. Remaining work: inventory every other calc wrapper and either add wrapper goldens or prove lib-engine coverage.

---

## Already closed this cycle (do not re-do)
- Authority/seal gate, figures freshness gate, `glaw-loop`, daemon, oversight kill-switch, RBAC/SOC2, MCP/host/Extism adapters, hallucination typology (4-way), **per-profile golden matters (all 9 profiles)**, **profile-consistency check in `glaw-doctor`**, sandbox fault-injection. All verified.
