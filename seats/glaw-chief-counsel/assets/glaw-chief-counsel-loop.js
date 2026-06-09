export const meta = {
  name: 'glaw-chief-counsel-loop',
  description: 'Loop-until-bulletproof: distinct-persona adversaries score each position 0-10 per lens each round; defense rebuilds; a position is BULLETPROOF only when a full round leaves no surviving critical/high attack AND panel min-score >= 8; then verify cites and the Chief Counsel decides',
  phases: [
    { title: 'Intel', detail: 'ingest Drive comments/suggestions' },
    { title: 'Debate', detail: 'multi-persona adversaries vs defense, looped to convergence with consensus scoring' },
    { title: 'Remediate', detail: 'Chief orders fix-agents to repair defects, then re-loops with MORE personas' },
    { title: 'Verify', detail: 'verify every cite against public APIs' },
    { title: 'Decide', detail: 'Chief Counsel decision; if all clear, finalize fund-grade dossier + remediation FAQ' },
  ],
}

const HOME = process.env.HOME
const MATTER = process.env.GLAW_MATTER || '<matter-slug>'
const DRAFTS = `${HOME}/.glaw/matters/${MATTER}/drafts`
const FOLDER = '<drive-folder-id>'
const ROSTER = `${HOME}/.claude/skills/glaw/lib/firm-roster.md`
const MAX_ROUNDS = 2
const PASS = 8 // panel minimum score required to declare bulletproof

// ── HARD COST GUARDRAILS (a single run must NEVER blow the budget again) ──
const MAX_DEBATE_AGENTS = 48        // hard ceiling on the expensive debate/remediation agents per run
let DEBATE_AGENTS = 0
async function A(prompt, opts) {     // budgeted agent for the compounding phase; null once the cap is hit
  if (DEBATE_AGENTS >= MAX_DEBATE_AGENTS) return null
  DEBATE_AGENTS++
  return agent(prompt, opts)
}
// A position whose blockers are MISSING REAL FACTS cannot be hardened by more rounds — exempt it.
const FACT_GAP = /\[VERIFY|blank|unfilled|not (?:yet )?provided|missing (?:the )?(?:date|fact|figure|number|valuation|cap table|balance sheet)|issuance date|gross[- ]?asset|cap[- ]?table|valuation|\bEIN\b|\bSSN\b|founder name/i
function isFactGap(attacks) {
  const txt = JSON.stringify(attacks || [])
  return FACT_GAP.test(txt)
}

// FAULT-TOLERANT structured agent. The workflow-killer was a subagent that skipped the StructuredOutput tool,
// which threw and failed the whole run. askJSON catches that and retries ONCE in plain-text-JSON mode, then
// parses — so one flaky agent degrades to a parsed result (or null) instead of failing everything.
// budgeted=true counts against MAX_DEBATE_AGENTS (debate phase); false for essential post-debate calls.
async function askJSON(prompt, schema, opts, budgeted) {
  if (budgeted) {
    if (DEBATE_AGENTS >= MAX_DEBATE_AGENTS) return null
    DEBATE_AGENTS++
  }
  try {
    return await agent(prompt, Object.assign({}, opts, { schema }))
  } catch (e) {
    try {
      const keys = Object.keys((schema && schema.properties) || {}).join(', ')
      const txt = await agent(prompt + `\n\nReturn ONLY one JSON object with keys [${keys}] — no prose, no markdown fences.`, opts)
      const m = String(txt).match(/\{[\s\S]*\}/)
      return m ? JSON.parse(m[0]) : null
    } catch (e2) { return null }
  }
}

const ADV = {
  irs:    'THE MOST AGGRESSIVE adversary on the panel: a relentless IRS Revenue Agent + DOJ Tax attorney who attacks EVERY move nonstop, concedes nothing, presumes the worst, and stacks every theory of disallowance, weak substantiation, lack of economic substance, sham/step-transaction, and §6662/§6663 penalties. You do not stop attacking until there is GENUINELY no issue left to raise; only then do you score it defensible',
  cred:   "a creditor's judgment-enforcement litigator attacking for FUFTA/UVTA badges of fraud, veil-piercing, and alter-ego",
  trustee:'a bankruptcy trustee attacking under §548 fraudulent transfer, exemption limits, Clark/inherited-IRA, and self-settled-trust weakness',
  sec:    'an SEC enforcement attorney attacking securities issues: Reg D, QSBS original-issuance, transfer restrictions',
  fincen: 'a FinCEN/OFAC examiner attacking AML, source-of-funds, BOI reporting, and sanctions nexus (e.g., Venezuela)',
  mna:    "a buyer's M&A diligence counsel attacking clean title, the §351 chain, and cap-table integrity",
}

const POSITIONS = [
  { key:'qsbs-1202', doc:'17-qsbs-1202-substantiation-packet.md', adv:['irs','sec','mna'], claim:'Example Holdings stock qualifies for QSBS §1202 exclusion incl. OBBBA 15M/75M/tiered.' },
  { key:'83b',       doc:'15-83b-wiki-dossier.md',                 adv:['irs'],             claim:'Founder §83(b) via Form 15620 within 30 days starts QSBS+LTCG clocks.' },
  { key:'351',       doc:'18-section351-incorporation-statements.md', adv:['irs','mna'],    claim:'Founder IP for stock is tax-free §351; holdco drop-down ok under Rev. Rul. 2003-51.' },
  { key:'409a',      doc:'19-section409a-valuation-file.md',        adv:['irs','sec'],       claim:'Option strikes at independent-appraisal 409A FMV get the presumption of reasonableness.' },
  { key:'rnd-41',    doc:'20-rnd-credit-section41-claim-kit.md',    adv:['irs'],             claim:'Example Holdings can claim §41 R&D credit + 500k payroll offset and expense domestic R&D under §174A.' },
  { key:'fl-state',  doc:'21-tax-elections-and-deadlines-matrix.md',adv:['irs'],             claim:'Example Holdings owes FL 5.5% corporate income tax (F-1120).' },
  { key:'asset-prot',doc:'26-asset-protection-trust-document-set.md',adv:['cred','trustee','fincen','irs'], claim:'The DAPT/third-party/DING structure protects assets and is not a fraudulent transfer when solvent + claim-free.' },
  { key:'exempt',    doc:'27-exempt-assets-and-custodian-reference.md', adv:['cred','trustee','irs'], claim:'ERISA/IRA/Roth/life-insurance are creditor-protected per federal+state law.' },
]

const ATTACK = { type:'object', additionalProperties:false, required:['adversary','score','verdict','surviving'], properties:{
  adversary:{type:'string'},
  score:{type:'number', description:'0-10 how DEFENSIBLE the position is against this lens (10 = cannot be beaten)'},
  verdict:{type:'string', description:'defeated (no blow lands) or lands-blow'},
  surviving:{type:'array', items:{type:'object', additionalProperties:false, required:['theory','severity'], properties:{
    theory:{type:'string'}, severity:{type:'string', description:'critical, high, medium, or low'}}}} }}

const BLUE = { type:'object', additionalProperties:false, required:['defenseScore','fixes','strengthenedClaim'], properties:{
  defenseScore:{type:'number'}, fixes:{type:'array', items:{type:'string'}}, strengthenedClaim:{type:'string'} }}

const VERDICT = { type:'object', additionalProperties:false, required:['citation','status','note'], properties:{
  citation:{type:'string'}, status:{type:'string', description:'confirmed, corrected, or unverified'},
  correctCite:{type:'string'}, holding:{type:'string'}, note:{type:'string'} }}

const DECISION = { type:'object', additionalProperties:false,
  required:['executiveSummary','vision','positions','prioritizedActions','blockers','overallVerdict'], properties:{
  executiveSummary:{type:'string'},
  vision:{type:'string', description:'result-oriented C-corp to fund-management trajectory unlocked'},
  positions:{type:'array', items:{type:'object', additionalProperties:false,
    required:['name','verdict','consensusScore','rounds','topRisk','owningSeat','action'], properties:{
    name:{type:'string'}, verdict:{type:'string', description:'BULLETPROOF / NEEDS-WORK / DO-NOT-FILE'},
    consensusScore:{type:'number'}, rounds:{type:'number'}, topRisk:{type:'string'},
    owningSeat:{type:'string'}, action:{type:'string'} }}},
  prioritizedActions:{type:'array', items:{type:'object', additionalProperties:false, required:['rank','action','owner'], properties:{
    rank:{type:'number'}, action:{type:'string'}, owner:{type:'string'} }}},
  blockers:{type:'array', items:{type:'string'}},
  overallVerdict:{type:'string'} }}

function isCritHigh(s){ return s && s.surviving && s.surviving.some(x => x.severity === 'critical' || x.severity === 'high') }

// LAUNCH-GUARD PREDICATE (fail-closed). The ONLY condition under which the chief loop may start:
// the validator must stamp LAUNCH_STATUS: LAUNCH_AUTHORIZED verbatim. ANYTHING else — FACT_INCOMPLETE,
// FACT_VALIDATION_PENDING, FACT_CONFLICT, null, empty, an error string, a partial match — DENIES.
// No bypass (no args.force). Keep this the single source of truth so the guard stays regression-tested.
function launchAuthorized(guardOutput){ return /LAUNCH_STATUS:\s*LAUNCH_AUTHORIZED/.test(guardOutput || '') }

const PERSONA = { type:'object', additionalProperties:false, required:['personas'], properties:{
  personas:{type:'array', items:{type:'object', additionalProperties:false, required:['name','lens'], properties:{
    name:{type:'string', description:'a vivid distinct adversary identity'},
    lens:{type:'string', description:'the specific theory/angle this persona presses'} }}} }}

// Casting director: invent bespoke adversary personas that do NOT exist in the fixed panel,
// so the adversarial pool self-expands to attack from angles the standard six miss.
async function castAdversaries(p, extraN){
  const base = p.adv.map(a => ({ name: a, lens: ADV[a] }))
  const want = 1   // capped at 1 invented persona (was escalating per macro — that compounded cost)
  const extra = await askJSON(
    `You are the casting director for an adversarial review of "${p.claim}". Read ${DRAFTS}/${p.doc}. ` +
    `Invent ${want} ADDITIONAL distinct adversary personas NOT already on the panel (${p.adv.join(', ')}) who would ` +
    `attack this from angles the standard panel misses — each with a vivid identity and the specific lens/theory ` +
    `they press (e.g., a state AG, a plaintiff's class-action firm, a whistleblower's counsel, a hostile auditor, ` +
    `a divorce/family-law creditor). At least one must be a relentless government/IRS-style attacker.`,
    PERSONA, { label:`cast:${p.key}`, phase:'Debate' }, true)
  return base.concat((extra.personas || []).map(x => ({ name: x.name, lens: x.lens })))
}

// Split surviving attacks into DRAFTING defects (fixable now) vs FACT-GAPS (missing real inputs — can't be
// hardened away, only recorded). This is what lets the Chief CONVERGE instead of looping forever.
function classify(attacks){
  let draftCritHigh = 0
  const factsNeeded = new Set()
  for (const a of (attacks || [])){
    for (const s of (a.surviving || [])){
      if (FACT_GAP.test(s.theory || '')) factsNeeded.add((s.theory || '').slice(0, 140))
      else if (s.severity === 'critical' || s.severity === 'high') draftCritHigh++
    }
  }
  return { draftCritHigh, factsNeeded: [...factsNeeded] }
}
function govDraftingClear(attacks){
  const g = (attacks || []).find(x => /irs|revenue|government/i.test(x.adversary || ''))
  if (!g) return true
  // IRS veto is satisfied on DRAFTING when its only surviving crit/high attacks are documented fact-gaps.
  return !(g.surviving || []).some(s => (s.severity === 'critical' || s.severity === 'high') && !FACT_GAP.test(s.theory || ''))
}

async function harden(p, extraN){
  let fixes = []
  const history = []
  let factsNeeded = []
  const cast = await castAdversaries(p, extraN)
  for (let round = 1; round <= MAX_ROUNDS; round++){
    const fixNote = fixes.length ? ` The defense has already adopted these fixes (assume them in place): ${JSON.stringify(fixes)}.` : ''
    const attacks = (await parallel(cast.map(per => () => askJSON(
      `You are ${per.lens} (identity: "${per.name}"). Read ${DRAFTS}/${p.doc}. Attack this position: "${p.claim}".${fixNote} ` +
      `Set adversary to "${per.name}". Score 0-10 how DEFENSIBLE it is. List only attacks that still SURVIVE, with severity. ` +
      `CRUCIAL: if an attack is that a REAL FACT IS MISSING (a blank, a [VERIFY], no issuance date / gross-assets / cap table / ` +
      `valuation / EIN), phrase the theory to clearly name the missing fact — these are recorded as "facts needed", NOT drafting ` +
      `defects. Ground every attack in real law; do not invent authority.` + LEARN,
      ATTACK, { label:`R${round} ${String(per.name).slice(0,14)}:${p.key}`, phase:'Debate' }, true)
    ))).filter(Boolean)
    if (!attacks.length){ history.push({ round, budgetStopped:true }); break }  // budget hit -> stop, don't spin
    const minScore = Math.min(...attacks.map(x => x.score))
    const { draftCritHigh, factsNeeded: fn } = classify(attacks)
    factsNeeded = [...new Set([...factsNeeded, ...fn])]
    const govOK = govDraftingClear(attacks)
    history.push({ round, attackers: attacks.length, minScore, draftCritHigh, factGaps: factsNeeded.length, govOK })

    if (draftCritHigh === 0 && govOK){
      // No fixable critical/high left and IRS clear on drafting. Terminal — converged.
      const status = factsNeeded.length === 0 ? 'BULLETPROOF' : 'DRAFTING-CLEAN'  // latter = pending real facts
      return { position:p.key, status, bulletproof: factsNeeded.length === 0, rounds:round,
               consensusMin:minScore, factsNeeded, history, fixes }
    }
    // Fixable drafting defects remain -> one defense pass, then re-check (bounded by MAX_ROUNDS + budget).
    const blue = await askJSON(
      `You are senior defense counsel hardening "${p.claim}". Read ${DRAFTS}/${p.doc}. Neutralize ONLY the fixable ` +
      `(non-fact-gap) surviving critical/high attacks with concrete fixes + a strengthened restatement + post-fix score 0-10. ` +
      `Do NOT try to fix missing-fact attacks — those are out of your control. Attacks: ${JSON.stringify(attacks)}.`,
      BLUE, { label:`R${round} BLUE:${p.key}`, phase:'Debate' }, true)
    if (blue) fixes = fixes.concat(blue.fixes || [])
  }
  const last = history[history.length-1] || {}
  // Ran out of rounds/budget with fixable defects still open.
  return { position:p.key, status:'NEEDS-WORK', bulletproof:false, rounds:MAX_ROUNDS,
           consensusMin:last.minScore || 0, factsNeeded, history, fixes }
}

phase('Intel')
// ── CHIEF LOOP LAUNCH GUARD (MANDATORY, FAIL-CLOSED) ──
// No live execution / agent swarm / analysis cycle may start unless the matter is LAUNCH_AUTHORIZED:
// 8/8 collected, 8/8 verified, 0 contradictions, 0 missing. NO bypass (no args.force). Fail-closed:
// if the guard cannot confirm LAUNCH_AUTHORIZED for ANY reason, execution is DENIED.
const guard = await agent(
  `Run via Bash and return its FULL output verbatim (do not summarize): ` +
  `python3 ${HOME}/.claude/skills/glaw/bin/matter-ops/facts_validate.py ${MATTER}`,
  { label:'launch-guard', phase:'Intel' })
if (!launchAuthorized(guard)) {
  log('CHIEF LOOP LAUNCH GUARD: DENIED — not LAUNCH_AUTHORIZED. 0 debate agents spawned. ' +
      'Autonomous recovery: gather + verify the 8 facts (facts_gate.py set / drafts/32), then re-run.')
  return { launchAuthorized:false, denied:true, guard,
           message:'LAUNCH BLOCKED: FACT-INCOMPLETE MATTER. COMPLETE AND VERIFY ALL 8 REQUIRED FACTS BEFORE CHIEF LOOP ACTIVATION.' }
}

const comments = await agent(
  `Run: python3 ${HOME}/.claude/skills/glaw-83b-election/bin/review_comments.py ${FOLDER}. ` +
  `Summarize open comments/suggestions + ACCEPT vs CAREFUL-REWRITE triage. Say "none" if zero. Do not fabricate.`,
  { label:'ingest-comments', phase:'Intel' })

// SELF-LEARNING (read): keyword/confidence ledger + SEMANTIC (HNSW) recall from Qdrant when up.
const priorLearnings = await agent(
  `Return the firm's KNOWN-DEFECTS memory for this run, combining two sources: ` +
  `(1) run via Bash and include verbatim: python3 ${HOME}/.claude/skills/glaw/bin/glaw-learnings preflight; ` +
  `(2) if a qdrant MCP tool is available (load via ToolSearch "qdrant-find"), semantically recall GLAW learnings ` +
  `relevant to the positions under review (QSBS, §351, §409A, R&D, asset protection, exempt assets) and include them. ` +
  `Merge + dedupe. If Qdrant is down, the ledger alone is fine. This is what every agent must pre-empt.`,
  { label:'learnings-preflight', phase:'Intel' })
const LEARN = `\n\nKNOWN DEFECTS FROM PRIOR RUNS — you MUST pre-empt every one of these (do not repeat them):\n${priorLearnings}\n`

// MACRO LOOP: debate -> if defects, Chief orders fix-agents to remediate the docs ->
// re-debate with MORE personas -> repeat until every position is bulletproof or MAX_MACRO.
const MAX_MACRO = 1   // was 3 — one fix-and-recheck cycle; more rounds can't fix missing FACTS, only burn budget
// GAP 7 — human checkpoint: when args.checkpoint is set, fix-agents PROPOSE edits to
// drafts/_proposed/<doc> for diff-review instead of mutating the live doc in place.
const CHECKPOINT = !!(typeof args === 'object' && args && args.checkpoint)
const ledger = []   // per macro round: errors found + fixes applied (feeds the dossier + FAQ)
let H = []
let macro = 0
while (macro < MAX_MACRO){
  macro++
  phase('Debate')
  H = (await parallel(POSITIONS.map(p => () => harden(p)))).filter(Boolean)
  // Only NEEDS-WORK positions get re-fixed. DRAFTING-CLEAN (only facts missing) + BULLETPROOF are TERMINAL —
  // re-fighting them can't help and only burns budget. This is what makes the loop converge.
  const failing = H.filter(h => h.status === 'NEEDS-WORK')
  const errorsFound = failing.reduce((n,h) => n + ((h.fixes && h.fixes.length) || 0), 0)
  ledger.push({ macroRound: macro,
    bulletproof: H.filter(h => h.status === 'BULLETPROOF').map(h => h.position),
    draftingCleanPendingFacts: H.filter(h => h.status === 'DRAFTING-CLEAN').map(h => h.position),
    stillFailing: failing.map(h => h.position), errorsFound, debateAgentsUsed: DEBATE_AGENTS })
  if (!failing.length) break
  phase('Remediate')
  const fixed = await parallel(failing.map(h => {
    const p = POSITIONS.find(x => x.key === h.position) || { doc:'' }
    const target = CHECKPOINT
      ? `WRITE your fully-revised version to a NEW file ${DRAFTS}/_proposed/${p.doc} (create the dir) for human diff-review — do NOT touch the live ${DRAFTS}/${p.doc}`
      : `Apply EVERY required fix directly to ${DRAFTS}/${p.doc} using the Edit/Write tools`
    return () => agent(
      `You are GLAW remediation counsel acting on the Chief Counsel's written order. Position "${h.position}" is NOT yet ` +
      `bulletproof. ${target}: insert primary statutory/regulatory authority, correct or replace any miscited case/ruling, ` +
      `demote wrong lead authority, add the missing substantiation, and mark any unknown fact as a clearly-labeled ` +
      `[VERIFY: ...] placeholder. NEVER fabricate a fact, number, or citation. Required fixes: ${JSON.stringify(h.fixes)}. ` +
      `Return the exact list of edits you made.` + LEARN,
      { label:`FIX:${h.position}`, phase:'Remediate' })
  }))
  ledger[ledger.length-1].fixesApplied = fixed.filter(Boolean)
}
// CONVERGED = no NEEDS-WORK left. Positions may be BULLETPROOF (no gaps) or DRAFTING-CLEAN (only real facts
// pending) — either way the Chief can produce the dossier now, with a "facts needed" section. This is the fix
// for the never-converging loop: drafting is provably done; the only remainder is YOUR inputs.
const allClear = H.length > 0 && H.every(h => h.status !== 'NEEDS-WORK')
const factsNeededAll = [...new Set(H.flatMap(h => h.factsNeeded || []))]

phase('Verify')
const CITES = [
  'Patterson v. Shumate, 504 U.S. 753 (1992)',
  'Clark v. Rameker, 573 U.S. 122 (2014)',
  'United States v. Grace, 395 U.S. 316 (1969)',
  'Rev. Rul. 2003-51',
  'Rev. Proc. 2025-28 (OBBBA 174A)',
  'IRS PLR 202405002 (confirm = IRC 115 governmental trust, NOT asset protection)',
  'Klabacka v. Nelson',
  'Rush University Medical Center v. Sessions',
  'IRC 1202 OBBBA 15M cap / 75M gross-asset ceiling / tiered 50-75-100% at 3-4-5 yrs (post 7/4/2025)',
  'IRC 41(h) 500000 payroll-offset cap',
  'Florida 5.5% corporate income tax (F-1120)',
]
const cites = (await parallel(CITES.map(c => () => askJSON(
  `Verify "${c}" via web + courtlistener.com/case.law/govinfo.gov/irs.gov. confirmed only if confirmable; ` +
  `corrected with the right cite if wrong; unverified if not confirmable. DO NOT FABRICATE.`,
  VERDICT, { label:'verify', phase:'Verify' }, false)))).filter(Boolean)

phase('Decide')
const decision = await agent(
  `You are the GLAW Chief Counsel. Read the roster ${ROSTER} to route fixes to owning seats. ` +
  `LOOP-HARDENING RESULTS (consensus scores per position): ${JSON.stringify(H)}. ` +
  `OPEN COMMENTS: ${comments}. CITE VERIFICATION: ${JSON.stringify(cites)}. ` +
  `Decide per position: BULLETPROOF only if bulletproof=true AND its supporting cites are confirmed; NEEDS-WORK if ` +
  `fixable; DO-NOT-FILE if a critical attack still survives at MAX_ROUNDS. Give consensusScore, rounds, top risk, ` +
  `owning GLAW seat, next action. Then a result-oriented executive summary, the vision, a ranked prioritizedActions ` +
  `list with owners, and hard blockers (any corrected/unverified cite is a blocker). Be decisive and grounded. ` +
  `Macro-loop ledger (errors found + fixes per round): ${JSON.stringify(ledger)}. allClear=${allClear}.`,
  DECISION, { label:'chief-counsel', phase:'Decide' }, false)

// SELF-LEARNING (write-back): persist every NEW defect from this run so the NEXT run (any corp) pre-empts it.
// The more attacks -> more fixes -> more learnings -> fewer new errors next time. scope:firm = applies to all matters.
const learned = await agent(
  `You are the GLAW knowledge keeper closing the self-learning loop. From this run's blockers ` +
  `${JSON.stringify(decision.blockers || [])} and per-position top risks ` +
  `${JSON.stringify((decision.positions || []).map(p => ({ name: p.name, topRisk: p.topRisk })))}, ` +
  `record each DISTINCT defect class as a firm-wide learning. For EACH, run via Bash: ` +
  `python3 ${HOME}/.claude/skills/glaw/bin/glaw-learnings add ` +
  `'{"error_class":"<slug>","scope":"firm","where":"<doc/position>","wrong":"<what was wrong>","fix":"<the correction>","authority":"<grounding cite if any>","confidence":<1-10>}'. ` +
  `Use scope=firm so it applies to ALL corps/matters on future runs. The CLI auto-dedupes known ones (harmless). ` +
  `Do NOT invent defects that did not occur. THEN run the reflection engine to synthesize higher-level ` +
  `meta-rules from the accumulated ledger: python3 ${HOME}/.claude/skills/glaw/bin/glaw-reflect --apply. ` +
  `Return the list of learnings recorded + the new ledger stat ` +
  `(run: python3 ${HOME}/.claude/skills/glaw/bin/glaw-learnings stats).`,
  { label:'learnings-write', phase:'Decide' })

// FINALIZE: the Chief converges when NO position is NEEDS-WORK (drafting is provably done). Positions are either
// BULLETPROOF or DRAFTING-CLEAN (pending real facts). The dossier ships now WITH a "facts needed" section.
let finalize = 'NOT FINALIZED — at least one position is still NEEDS-WORK (fixable drafting defects remain); rerun after fixes.'
if (allClear){
  phase('Decide')
  finalize = await agent(
    `Drafting is DONE: no position is NEEDS-WORK. Per-position status: ` +
    `${JSON.stringify(H.map(h => ({ position: h.position, status: h.status, factsNeeded: (h.factsNeeded||[]).length })))}. ` +
    `Consolidated FACTS NEEDED to reach 100% (real client inputs the agents correctly refused to invent): ` +
    `${JSON.stringify(factsNeededAll)}. Produce two deliverables and WRITE them to disk: ` +
    `(1) ${DRAFTS}/29-final-dossier.md — a fund-grade FINAL dossier (entity+cap table, QSBS §1202, §351, §409A, ` +
    `R&D §41/§174A, asset protection, exempt assets, IRS audit defense). Stamp each section HONESTLY: "BULLETPROOF" ` +
    `only where status=BULLETPROOF; "DRAFTING-CLEAN — pending facts" elsewhere, listing that section's facts needed. ` +
    `Lead the dossier with a prominent "FACTS NEEDED TO REACH 100%" checklist = ${JSON.stringify(factsNeededAll)}. ` +
    `(2) ${DRAFTS}/30-remediation-faq.md — macro rounds (${macro}), errors found per round, and an FAQ of EXACTLY ` +
    `what the agents corrected, from this ledger: ${JSON.stringify(ledger)}. ` +
    `(3) THEN assemble the date+time-stamped final package by running via Bash: ` +
    `bash ${HOME}/.claude/skills/glaw/bin/matter-ops/assemble_package.sh ` +
    `${HOME}/.glaw/matters/${MATTER} /private/tmp/irs_forms ` +
    `— this puts all documents, IRS forms, filings, dossier + FAQ + manifest into one timestamped subfolder. ` +
    `Use the Write tool for both. THEN publish them to Drive by running, via Bash: ` +
    `python3 ${HOME}/.claude/skills/glaw/bin/matter-ops/publish_drafts_to_drive.py ${FOLDER} ` +
    `${DRAFTS}/29-final-dossier.md ${DRAFTS}/30-remediation-faq.md  (GAP 3 auto-publish). ` +
    `Then return a one-paragraph summary including the published Drive links.`,
    { label:'finalize', phase:'Decide' })
}

return { decision, allClear, macroRounds:macro, ledger, learned, hardened:H, finalize, openComments:comments, cites }
