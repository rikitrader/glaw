#!/usr/bin/env node
// T1 — Loop self-test harness (zero spend). Mocks the agent() layer and exercises the ACTUAL
// engine helpers (extracted from glaw-chief-counsel-loop.js) to prove the cost-fix works:
//   1. classify() splits missing-fact attacks from fixable drafting defects
//   2. govDraftingClear() lets the IRS veto pass when only fact-gaps remain
//   3. askJSON() recovers when an agent "forgets" StructuredOutput (the bug that killed the run)
//   4. the MAX_DEBATE_AGENTS budget cap actually stops spend
//   5. harden() CONVERGES to DRAFTING-CLEAN on fact-gaps instead of looping forever
// No LLM calls. No tokens. Run: node test/loop-selftest.mjs
import { readFileSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const here = dirname(fileURLToPath(import.meta.url))
const engine = readFileSync(join(here, '..', 'assets', 'glaw-chief-counsel-loop.js'), 'utf8')

// Slice the pure-helper prefix: from `const DRAFTS` up to the workflow body `phase('Intel')`.
const start = engine.indexOf('const DRAFTS')
const end = engine.indexOf("phase('Intel')")
if (start < 0 || end < 0) { console.error('FAIL: could not locate engine helper prefix'); process.exit(1) }
const prefix = engine.slice(start, end)

// Build the helpers with mocked globals. `LEARN` is defined after the slice, so stub it.
function buildHelpers(agent, parallel) {
  const body = `var LEARN='';\n${prefix}\n;return {classify,govDraftingClear,askJSON,A,FACT_GAP,harden,launchAuthorized,MAX_DEBATE_AGENTS,MAX_ROUNDS,POSITIONS};`
  return new Function('agent', 'parallel', body)(agent, parallel)
}
const mkParallel = () => (thunks) => Promise.all(thunks.map(t => Promise.resolve().then(t).catch(() => null)))

let pass = 0, fail = 0
const ok = (name, cond) => { if (cond) { pass++; console.log('  ✓', name) } else { fail++; console.log('  ✗ FAIL:', name) } }

// --- Test 1+2: classify + govDraftingClear ---
{
  const h = buildHelpers(async () => null, mkParallel())
  const attacks = [
    { adversary: 'IRS Revenue Agent', surviving: [{ theory: 'no issuance date provided [VERIFY]', severity: 'critical' }] },
    { adversary: 'SEC', surviving: [{ theory: 'transfer restriction wording is loose', severity: 'high' }] },
  ]
  const c = h.classify(attacks)
  ok('classify: 1 fact-gap recorded', c.factsNeeded.length === 1)
  ok('classify: 1 fixable drafting crit/high', c.draftCritHigh === 1)
  ok('govDraftingClear: IRS clear when only fact-gap', h.govDraftingClear(attacks) === true)
  const irsHard = [{ adversary: 'IRS', surviving: [{ theory: 'economic substance sham', severity: 'critical' }] }]
  ok('govDraftingClear: IRS blocks on real drafting defect', h.govDraftingClear(irsHard) === false)
}

// --- Test 3: askJSON fallback when StructuredOutput is skipped ---
{
  let calls = 0
  const agent = async (_p, opts) => {
    calls++
    if (opts && opts.schema) throw new Error('subagent completed without calling StructuredOutput')
    return '```json\n{"adversary":"x","score":9,"verdict":"defeated","surviving":[]}\n```'
  }
  const h = buildHelpers(agent, mkParallel())
  const r = await h.askJSON('attack', { type: 'object' }, { label: 't', phase: 'Debate' }, false)
  ok('askJSON: recovered a parsed object after StructuredOutput skip', r && r.score === 9)
  ok('askJSON: used exactly 2 underlying calls (schema + fallback)', calls === 2)
}

// --- Test 4: budget cap stops spend ---
{
  const h = buildHelpers(async () => ({ ok: true }), mkParallel())
  let nulls = 0, oks = 0
  for (let i = 0; i < h.MAX_DEBATE_AGENTS + 5; i++) {
    const r = await h.A('x', { schema: {} }, true)   // note: A(prompt, opts) — budgeted
    if (r === null) nulls++; else oks++
  }
  ok(`budget: stopped after ${h.MAX_DEBATE_AGENTS} agents`, oks === h.MAX_DEBATE_AGENTS && nulls === 5)
}

// --- Test 5: harden CONVERGES to DRAFTING-CLEAN on fact-gaps (no infinite loop) ---
{
  // every adversary returns only a missing-fact attack -> not fixable -> must terminate as DRAFTING-CLEAN
  const agent = async (_p, opts) => {
    if (opts && opts.schema) {
      // cast (PERSONA) returns personas; attacks return fact-gap surviving; blue returns fixes
      return { personas: [{ name: 'Extra', lens: 'edge' }],
               adversary: 'IRS', score: 5, verdict: 'lands-blow',
               surviving: [{ theory: 'gross-assets balance sheet missing [VERIFY]', severity: 'critical' }],
               defenseScore: 5, fixes: [], strengthenedClaim: 'x' }
    }
    return '{}'
  }
  const h = buildHelpers(agent, mkParallel())
  const res = await Promise.race([
    h.harden(h.POSITIONS[0]),
    new Promise((_, rej) => setTimeout(() => rej(new Error('TIMEOUT — loop did not converge')), 4000)),
  ]).catch(e => ({ error: e.message }))
  ok('harden: converged (no infinite loop)', res && !res.error)
  ok('harden: status DRAFTING-CLEAN (facts pending, not NEEDS-WORK)', res && res.status === 'DRAFTING-CLEAN')
  ok('harden: recorded facts needed', res && (res.factsNeeded || []).length > 0)
  ok('harden: stayed within MAX_ROUNDS', res && res.rounds <= h.MAX_ROUNDS)
}

// --- Test 6: LAUNCH GUARD is fail-closed (the 358-agent-burn regression) ---
{
  const h = buildHelpers(async () => null, mkParallel())
  // The ONLY string that may authorize a launch:
  ok('guard: AUTHORIZES on exact LAUNCH_AUTHORIZED stamp',
     h.launchAuthorized('LAUNCH_STATUS: LAUNCH_AUTHORIZED   STATE: READY') === true)
  // Everything else DENIES — fail-closed:
  ok('guard: DENIES FACT_INCOMPLETE', h.launchAuthorized('LAUNCH_STATUS: FACT_INCOMPLETE') === false)
  ok('guard: DENIES FACT_VALIDATION_PENDING', h.launchAuthorized('LAUNCH_STATUS: FACT_VALIDATION_PENDING') === false)
  ok('guard: DENIES FACT_CONFLICT', h.launchAuthorized('LAUNCH_STATUS: FACT_CONFLICT') === false)
  ok('guard: DENIES null (validator crashed/no output)', h.launchAuthorized(null) === false)
  ok('guard: DENIES empty string', h.launchAuthorized('') === false)
  ok('guard: DENIES an error string', h.launchAuthorized('Traceback: python error') === false)
  // Real validator output for the live matter must DENY (it is FACT_INCOMPLETE, 0/8):
  let real = ''
  try {
    real = execFileSync('python3',
      [join(here, '..', '..', 'glaw', 'bin', 'matter-ops', 'facts_validate.py'),
       'example-matter-slug'], { encoding: 'utf8' })
  } catch (e) { real = (e.stdout || '') + (e.stderr || '') }  // validator exits 1 when blocked — capture stdout
  ok('guard: live validator output present', /LAUNCH_STATUS:/.test(real))
  ok('guard: live matter is correctly DENIED (fact-incomplete)', h.launchAuthorized(real) === false)
}

console.log(`\n${fail === 0 ? 'ALL PASS' : 'FAILURES'} — ${pass} passed, ${fail} failed`)
process.exit(fail === 0 ? 0 : 1)
