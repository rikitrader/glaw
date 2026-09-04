import { classifyIntakeReadiness, validateIntake, type Intake } from './intake.ts';
import { validateSourceReferences } from './citations.ts';
import type { IndexedDocument } from './citations.ts';
import type { WorkflowExecutor, NodeExecutionResult } from './workflow.ts';
import type { AuditFinding } from './types.ts';
import { capitalAdequacy, depositDollarization, loanToDeposit, moneyMultiplier, parallelPremium, reserveCoverage, reserveRatio, fiscalDeficitToGdp, stressLoss } from './formulas.ts';
import { auditCalculationArtifacts } from './math-audit.ts';
import { auditDataBundle } from './data-forensics.ts';
import { canIssueFinalRecommendation } from './guards.ts';
import { validateEvidenceSearchPlan, type EvidenceSearchPlan } from './evidence-search.ts';
import { buildPostureIndex } from './posture-index.ts';
import { validateEvidenceBoundAssessment, type EvidenceBoundAssessment } from './posture-store.ts';
import { creditCounterpartAssetResidual, creditCounterpartsResidual, goldenGrowthGap, goldenGrowthRateQtm, type CreditCounterpartAssetObservation, type MonetaryFlowObservation } from './monetary-flow.ts';
import { buildEvidenceLaneReport } from './evidence-lanes.ts';

export interface HaeisExecutorOptions { intake: Intake; documents: IndexedDocument[]; posture_assessments?: EvidenceBoundAssessment[]; evidence_search_plan?: EvidenceSearchPlan; }

const blocked = (reason: string, gate?: string, evidence_ids: string[] = []): NodeExecutionResult => ({ status: 'BLOCKED', reason, gate_updates: gate ? { [gate]: 'BLOCKED' } : undefined, gate_evidence: gate ? { [gate]: { owner: 'haeis-executor', evidence_ids, reason } } : undefined });
const pass = (artifacts: Record<string, unknown> = {}, gate_updates: Record<string, 'PASS' | 'OPEN' | 'BLOCKED'> = {}, evidence_ids: string[] = []): NodeExecutionResult => ({ status: 'PASS', artifacts, gate_updates, gate_evidence: Object.fromEntries(Object.keys(gate_updates).map((gate) => [gate, { owner: 'haeis-executor', evidence_ids }])) });

type DataItem = { name: string; value: number | string | null; source_ids: string[] };
const normalized = (value: string) => value.toLocaleLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const findItem = (items: DataItem[], aliases: string[]): DataItem | undefined => {
  const names = new Set(aliases.map(normalized));
  return items.find((item) => names.has(normalized(item.name)));
};
const numberValue = (item: DataItem | undefined): number | undefined => typeof item?.value === 'number' && Number.isFinite(item.value) ? item.value : undefined;
const sourceIdsFor = (...items: Array<DataItem | undefined>) => [...new Set(items.flatMap((item) => item?.source_ids ?? []))];
const withSources = (calculation: ReturnType<typeof moneyMultiplier>, source_ids: string[]) => ({ ...calculation, source_data: source_ids });

function deterministicCalculations(name: string, raw: unknown): ReturnType<typeof moneyMultiplier>[] {
  if (!Array.isArray(raw)) return [];
  const items = raw as DataItem[];
  const value = (aliases: string[]) => numberValue(findItem(items, aliases));
  const item = (aliases: string[]) => findItem(items, aliases);
  if (name === 'monetary') {
    const money = item(['money supply', 'm2']); const base = item(['monetary base', 'm0']);
    const m = numberValue(money); const b = numberValue(base);
    return m !== undefined && b !== undefined ? [withSources(moneyMultiplier(m, b), sourceIdsFor(money, base))] : [];
  }
  if (name === 'banking') {
    const loans = item(['loans']); const deposits = item(['deposits', 'total deposits']); const reserves = item(['bank reserves', 'reserves']); const capital = item(['bank equity', 'capital']); const rwa = item(['risk weighted assets', 'rwa']);
    const l = numberValue(loans); const d = numberValue(deposits); const r = numberValue(reserves); const c = numberValue(capital); const w = numberValue(rwa);
    const calculations = [] as ReturnType<typeof moneyMultiplier>[];
    if (l !== undefined && d !== undefined) calculations.push(withSources(loanToDeposit(l, d), sourceIdsFor(loans, deposits)));
    if (r !== undefined && d !== undefined) calculations.push(withSources(reserveRatio(r, d), sourceIdsFor(reserves, deposits)));
    if (c !== undefined && w !== undefined) calculations.push(withSources(capitalAdequacy(c, w), sourceIdsFor(capital, rwa)));
    return calculations;
  }
  if (name === 'fiscal') {
    const revenue = item(['government revenue', 'revenue']); const spending = item(['government spending', 'spending']); const gdp = item(['gdp']);
    const rev = numberValue(revenue); const spend = numberValue(spending); const output = numberValue(gdp);
    return rev !== undefined && spend !== undefined && output !== undefined ? [withSources(fiscalDeficitToGdp(rev, spend, output), sourceIdsFor(revenue, spending, gdp))] : [];
  }
  if (name === 'exchange-rate') {
    const parallel = item(['parallel fx', 'parallel exchange rate']); const official = item(['official fx', 'official exchange rate']);
    const p = numberValue(parallel); const o = numberValue(official);
    return p !== undefined && o !== undefined ? [withSources(parallelPremium(p, o), sourceIdsFor(parallel, official))] : [];
  }
  if (name === 'dollarization') {
    const fxDeposits = item(['dollar deposits', 'fx deposits']); const deposits = item(['deposits', 'total deposits']);
    const fx = numberValue(fxDeposits); const total = numberValue(deposits);
    return fx !== undefined && total !== undefined ? [withSources(depositDollarization(fx, total), sourceIdsFor(fxDeposits, deposits))] : [];
  }
  if (name === 'currency-board') {
    const reserves = item(['eligible foreign reserves', 'liquid eligible foreign reserves']); const liabilities = item(['currency board liabilities', 'monetary liabilities']);
    const r = numberValue(reserves); const l = numberValue(liabilities);
    return r !== undefined && l !== undefined ? [withSources(reserveCoverage(r, l), sourceIdsFor(reserves, liabilities))] : [];
  }
  if (name === 'stress-test') {
    const exposure = item(['exposure', 'stressed exposure']); const lgd = item(['lgd', 'loss given default']);
    const e = numberValue(exposure); const l = numberValue(lgd);
    return e !== undefined && l !== undefined ? [withSources(stressLoss(e, l), sourceIdsFor(exposure, lgd))] : [];
  }
  return [];
}

type MonetaryFlowInput = {
  golden_growth_qtm?: { observed_money_growth?: number; inflation_target: number; real_growth: number; velocity_change: number; tolerance?: number; source_ids: string[] };
  golden_growth?: { observed_money_growth: number; real_growth_potential: number; inflation_objective: number; tolerance?: number; source_ids: string[] };
  credit_counterparts_asset?: CreditCounterpartAssetObservation & { tolerance?: number };
  credit_counterparts?: MonetaryFlowObservation & { tolerance?: number };
};

function monetaryFlowExecutor(context: Parameters<WorkflowExecutor>[0], verifiedSourceIds: string[]): NodeExecutionResult {
  const input = context.artifacts.monetary_flow_input as MonetaryFlowInput | undefined;
  if (!input) return blocked('monetary-flow analysis BLOCKED — explicit monetary_flow_input is absent.');
  const sourceIds = [...new Set([...(input.golden_growth?.source_ids ?? []), ...(input.credit_counterparts?.source_ids ?? [])])];
  sourceIds.push(...(input.golden_growth_qtm?.source_ids ?? []), ...(input.credit_counterparts_asset?.source_ids ?? []));
  const uniqueSourceIds = [...new Set(sourceIds)];
  const frameworkVerified = ['PAPER-HANKE-GG-232', 'PAPER-HANKE-GG-233', 'PAPER-HANKE-GG-234'].every((id) => verifiedSourceIds.includes(id));
  if (!uniqueSourceIds.length) return blocked('monetary-flow analysis BLOCKED — source_ids are required for every monetary-flow calculation.');
  const unverified = uniqueSourceIds.filter((id) => !verifiedSourceIds.includes(id));
  if (unverified.length) return blocked(`monetary-flow analysis BLOCKED — unverified or restricted source IDs: ${unverified.join(', ')}`, 'citations-verified', unverified);
  if (!input.golden_growth_qtm && !input.golden_growth && !input.credit_counterparts_asset && !input.credit_counterparts) return blocked('monetary-flow analysis BLOCKED — at least one explicit Golden Growth or Credit Counterparts input is required.');
  const calculations: Array<Record<string, unknown>> = [];
  const warnings: string[] = [];
  if (input.golden_growth_qtm) {
    const growth = input.golden_growth_qtm;
    const result = goldenGrowthRateQtm(growth.inflation_target, growth.real_growth, growth.velocity_change, growth.source_ids);
    calculations.push({ formula: result.formula, inputs: result.inputs, result: result.result, source_data: result.source_ids, observed_money_growth: growth.observed_money_growth, gap: growth.observed_money_growth === undefined ? undefined : growth.observed_money_growth - result.result, tolerance: growth.tolerance ?? 0.005 });
  }
  if (input.golden_growth) {
    const growth = input.golden_growth;
    const result = goldenGrowthGap(growth.observed_money_growth, growth.real_growth_potential, growth.inflation_objective, growth.tolerance ?? 0.005, growth.source_ids);
    calculations.push({ formula: result.formula, inputs: result.inputs, result: result.result, source_data: result.source_ids, observed_money_growth: result.observed_money_growth, gap: result.gap, interpretation: result.interpretation, tolerance: result.tolerance });
  }
  if (input.credit_counterparts) {
    const flow = input.credit_counterparts;
    const result = creditCounterpartsResidual(flow, flow.tolerance ?? 1e-9);
    calculations.push({ formula: result.formula, inputs: { private_credit_change: flow.private_credit_change, public_credit_change: flow.public_credit_change, net_foreign_assets_change: flow.net_foreign_assets_change, other_items_net_change: flow.other_items_net_change }, result: result.implied_broad_money_change, source_data: result.source_ids, broad_money_change: result.broad_money_change, identity_error: result.identity_error, reconciled: result.reconciled, tolerance: result.tolerance });
    warnings.push(...result.warnings);
  }
  if (input.credit_counterparts_asset) {
    const result = creditCounterpartAssetResidual(input.credit_counterparts_asset, input.credit_counterparts_asset.tolerance ?? 1e-9);
    calculations.push({ formula: result.formula, inputs: { bank_lending_change: input.credit_counterparts_asset.bank_lending_change, securities_change: input.credit_counterparts_asset.securities_change, bank_reserves_change: input.credit_counterparts_asset.bank_reserves_change, other_items_net_change: input.credit_counterparts_asset.other_items_net_change }, result: result.implied_broad_money_change, source_data: result.source_ids, broad_money_change: result.broad_money_change, identity_error: result.identity_error, reconciled: result.reconciled, tolerance: result.tolerance });
    warnings.push(...result.warnings);
  }
  return pass({ monetary_flow_analysis: { status: 'COMPUTED', attribution_status: frameworkVerified ? 'FRAMEWORK_VERIFIED_SAE_232_234' : 'FRAMEWORK_PARTIAL_VERIFICATION', calculations, warnings, source_ids: uniqueSourceIds, interpretation_blocked: warnings.length > 0 } }, {}, uniqueSourceIds);
}

type AdversarialFinding = AuditFinding & { attacked_assumption: string; steelman_relevance: string };
const computedAnalyses = (artifacts: Record<string, unknown>) => Object.entries(artifacts)
  .filter(([key, value]) => key.endsWith('_analysis') && (value as { status?: string })?.status === 'COMPUTED')
  .map(([, value]) => value as { calculations?: Array<{ result: number; source_data: string[] }> })
  .filter((value): value is { calculations: Array<{ result: number; source_data: string[] }> } => Array.isArray(value.calculations));

function buildRedTeamFindings(artifacts: Record<string, unknown>): { steelman: string; findings: AdversarialFinding[]; evidence_ids: string[] } {
  const analyses = computedAnalyses(artifacts);
  const evidence_ids = [...new Set(analyses.flatMap((analysis) => analysis.calculations.flatMap((calculation) => calculation.source_data)))];
  const findings: AdversarialFinding[] = [];
  if (!artifacts['stress-test_analysis']) findings.push({ finding_id: 'RED-STRESS-001', severity: 'CRITICAL', category: 'DATA', text: 'The proposal has no computed stress-loss result in the evidence bundle.', evidence_ids, owner: 'red-team-monetary', status: 'OPEN', attacked_assumption: 'The reform remains viable under a banking or funding shock.', steelman_relevance: 'A hard monetary constraint can improve credibility, but it does not by itself prove crisis liquidity capacity.' });
  const banking = artifacts.banking_analysis as { calculations?: Array<{ formula: string; result: number; source_data: string[] }> } | undefined;
  const loanDeposit = banking?.calculations?.find((calculation) => calculation.formula === 'loans / deposits');
  if (loanDeposit && loanDeposit.result > 1) findings.push({ finding_id: 'RED-BANK-001', severity: 'HIGH', category: 'DATA', text: 'Computed loans-to-deposits exceeds one; deposit funding alone does not cover loans.', evidence_ids: loanDeposit.source_data, owner: 'red-team-banking', status: 'OPEN', attacked_assumption: 'Bank credit can continue without additional liquidity or capital support.', steelman_relevance: 'Monetary discipline may reduce inflation, but transition credit continuity remains a separate constraint.' });
  if (!findings.length) findings.push({ finding_id: 'RED-CAUSAL-001', severity: 'MEDIUM', category: 'CAUSALITY', text: 'The available calculations do not establish that the proposed regime caused the projected outcome.', evidence_ids, owner: 'red-team-causality', status: 'OPEN', attacked_assumption: 'Observed relationships are sufficient to identify the policy effect.', steelman_relevance: 'The framework may still be operationally coherent, but causal identification requires a counterfactual and additional evidence.' });
  return { steelman: 'Steelman: a monetary-stability proposal can impose a credible nominal constraint and reduce financing discretion; the challenge is whether fiscal, banking, and institutional conditions make that constraint durable.', findings, evidence_ids };
}

function redTeamExecutor(context: Parameters<WorkflowExecutor>[0]): NodeExecutionResult {
  if (!context.artifacts.verified_source_count) return blocked('red team BLOCKED — no verified sources in the evidence bundle.');
  if (!context.artifacts.data_bundle) {
    const diagnostic = context.workflow.diagnostic_continuation?.allowed_nodes.includes(context.node.id);
    if (!diagnostic) return blocked('red team BLOCKED — no data bundle has passed data forensics.');
    const evidence_ids = Array.isArray(context.artifacts.verified_source_ids) ? context.artifacts.verified_source_ids as string[] : [];
    const finding: AdversarialFinding = {
      finding_id: 'RED-DATA-001', severity: 'CRITICAL', category: 'DATA',
      text: 'Diagnostic review cannot test the proposed monetary reform because the critical Venezuela data bundle did not pass intake and data forensics.',
      evidence_ids, owner: 'red-team-data', status: 'OPEN',
      attacked_assumption: 'A policy conclusion can be assessed without reconciled monetary, banking, fiscal, reserve, and FX observations.',
      steelman_relevance: 'A credible nominal anchor may improve expectations, but the absence of reconciled balance-sheet and fiscal data prevents a claim about liquidity, credit, or systemic stability.'
    };
    return { status: 'PASS', artifacts: { red_team: { steelman: 'Steelman: a monetary-stability proposal can impose a credible nominal constraint and reduce financing discretion; the challenge is whether fiscal, banking, and institutional conditions make that constraint durable.', findings: [finding], evidence_ids, status: 'DIAGNOSTIC_ONLY' } }, findings: [finding] };
  }
  const result = buildRedTeamFindings(context.artifacts);
  return { status: 'PASS', artifacts: { red_team: result }, findings: result.findings };
}

function blueTeamExecutor(context: Parameters<WorkflowExecutor>[0]): NodeExecutionResult {
  const red = context.artifacts.red_team as { findings?: AdversarialFinding[] } | undefined;
  if (!red?.findings?.length) return blocked('blue team BLOCKED — Red Team findings are absent.');
  const supplied = context.artifacts.blue_team_resolutions as Record<string, { defense: string; evidence_for_defense: string[]; residual_risk: string; status: 'RESOLVED' | 'PARTIALLY_RESOLVED' | 'UNRESOLVED' }> | undefined;
  const responses = red.findings.map((finding) => {
    const response = supplied?.[finding.finding_id];
    if (response) return { finding_id: finding.finding_id, criticism: finding.text, severity: finding.severity, ...response };
    return { finding_id: finding.finding_id, criticism: finding.text, severity: finding.severity, defense: 'The available evidence can narrow the claim but cannot eliminate the stated risk without additional data or institutional safeguards.', evidence_for_defense: finding.evidence_ids, residual_risk: finding.attacked_assumption, status: 'PARTIALLY_RESOLVED' as const };
  });
  return pass({ blue_team: { responses, status: 'PARTIALLY_RESOLVED' } });
}

function secondRedExecutor(context: Parameters<WorkflowExecutor>[0]): NodeExecutionResult {
  const blue = context.artifacts.blue_team as { responses?: Array<{ finding_id: string; severity?: string; status: string; residual_risk: string; evidence_for_defense: string[] }> } | undefined;
  if (!blue?.responses?.length) return blocked('second Red Team BLOCKED — Blue Team responses are absent.');
  const findings = blue.responses.map((response) => ({ finding_id: response.finding_id, criticism: response.residual_risk, attacked_assumption: response.residual_risk, evidence_against: response.evidence_for_defense, severity: response.severity === 'CRITICAL' ? 'CRITICAL' as const : 'HIGH' as const, status: response.status === 'RESOLVED' ? 'RESOLVED' as const : 'UNRESOLVED' as const }));
  const evidence_ids = [...new Set(findings.flatMap((finding) => finding.evidence_against))];
  const criticalOpen = blue.responses.some((response) => response.severity === 'CRITICAL' && response.status !== 'RESOLVED');
  const unresolved = blue.responses.some((response) => response.status === 'UNRESOLVED');
  if (criticalOpen || unresolved) return { status: 'BLOCKED', reason: 'second Red Team BLOCKED — critical or explicitly unresolved residual risks remain.', artifacts: { second_red_team: { findings, status: 'UNRESOLVED' } }, gate_updates: { 'red-blue-red-complete': 'BLOCKED' }, gate_evidence: { 'red-blue-red-complete': { owner: 'second-red-team', evidence_ids, reason: 'Residual risks remain unresolved after Blue Team response.' } } };
  const conditional = blue.responses.some((response) => response.status === 'PARTIALLY_RESOLVED');
  const status = conditional ? 'CONDITIONAL' : 'SURVIVES';
  return { status: 'PASS', artifacts: { second_red_team: { findings, status, residual_risks: blue.responses.filter((response) => response.status !== 'RESOLVED').map((response) => response.residual_risk) } }, gate_updates: { 'red-blue-red-complete': 'PASS' }, gate_evidence: { 'red-blue-red-complete': { owner: 'second-red-team', evidence_ids, reason: conditional ? 'No critical or explicitly unresolved risk remains; residual risks are disclosed as conditions.' : 'All Red Team findings were resolved with source-bound Blue Team evidence.' } } };
}

export function createHaeisExecutors(options: HaeisExecutorOptions): Record<string, WorkflowExecutor> {
  const sourceIds = options.documents.map((document) => document.document_id);
  const verifiedDocuments = options.documents.filter((document) => document.status === 'VERIFIED');
  const postureExecutor = (): NodeExecutionResult => {
    const caseId = `${options.intake.country.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-current`;
    const assessments = options.posture_assessments ?? [];
    const errors = assessments.flatMap((assessment) => validateEvidenceBoundAssessment(assessment, options.documents).map((error) => `${assessment.posture_id}: ${error}`));
    if (errors.length) return blocked(`posture matrix BLOCKED — ${errors.join('; ')}`);
    const cells = buildPostureIndex([caseId]);
    const assessedByPosture = new Map(assessments.filter((assessment) => assessment.case_id === caseId).map((assessment) => [assessment.posture_id, assessment]));
    const matrix = cells.map((cell) => {
      const assessment = assessedByPosture.get(cell.posture_id);
      return assessment ? { ...cell, status: 'ASSESSED' as const, claims: assessment.claims.map((claim) => ({ text: claim.text, label: claim.label, source_ids: claim.source_ids })) } : cell;
    });
    return pass({ posture_matrix: { case_id: caseId, status: assessments.length ? 'PARTIAL_EVIDENCE' : 'PENDING_SOURCE_REVIEW', cells: matrix, assessments } });
  };
  const analysisNeeds = (name: string, context: Parameters<WorkflowExecutor>[0]): NodeExecutionResult => {
    if (!context.artifacts.verified_source_count) return blocked(`${name} BLOCKED — no verified sources in the evidence bundle.`);
    if (!context.artifacts.data_bundle) return blocked(`${name} BLOCKED — no data bundle has passed data forensics.`);
    const calculations = deterministicCalculations(name, context.artifacts.data_bundle);
    if (!calculations.length) return blocked(`${name} analysis BLOCKED — no supported numeric inputs with lineage were supplied.`);
    return pass({ [`${name}_analysis`]: { status: 'COMPUTED', claims: [], calculations } });
  };
  const executors: Record<string, WorkflowExecutor> = {
    intake: () => { const errors = validateIntake(options.intake, sourceIds); const readiness = classifyIntakeReadiness(options.intake, sourceIds, verifiedDocuments.map((document) => document.document_id)); return errors.length ? blocked(`intake BLOCKED — ${errors.join('; ')}`, 'intake-ready', options.intake.source_ids) : pass({ intake: options.intake, intake_readiness: readiness }, { 'intake-ready': 'PASS' }, options.intake.source_ids); },
    'source-search': () => options.evidence_search_plan
      ? pass({ source_candidates: options.intake.source_ids, evidence_lanes: buildEvidenceLaneReport(options.evidence_search_plan, options.documents), evidence_search_plans: [options.evidence_search_plan] })
      : pass({ source_candidates: options.intake.source_ids, evidence_lanes: { status: 'PENDING_PLAN', recommendation_status: 'BLOCKED_PENDING_EVIDENCE_REVIEW', rule: 'No evidence lane is inferred without an explicit three-lane search plan.' } }),
    'source-verification': () => { const unknown = validateSourceReferences(options.intake.source_ids, options.documents); if (unknown.length) return blocked(`source verification BLOCKED — unknown source IDs: ${unknown.join(', ')}`, 'citations-verified', unknown); const restricted = options.intake.source_ids.filter((id) => !verifiedDocuments.some((document) => document.document_id === id)); if (restricted.length) return blocked(`source verification BLOCKED — unverified or restricted source IDs: ${restricted.join(', ')}`, 'citations-verified', restricted); return pass({ verified_source_count: verifiedDocuments.length, verified_source_ids: options.intake.source_ids }, { 'citations-verified': 'PASS' }, options.intake.source_ids); },
    'data-intake': () => { const unavailable = options.intake.data_intake.filter((item) => item.status === 'UNAVAILABLE'); return unavailable.length ? blocked(`data intake BLOCKED — unavailable critical data: ${unavailable.map((item) => item.name).join(', ')}`, 'critical-data-reconciled') : pass({ data_bundle: options.intake.data_intake, ...(options.intake.monetary_flow_input ? { monetary_flow_input: options.intake.monetary_flow_input } : {}), ...(options.intake.historical_comparables ? { historical_comparables: options.intake.historical_comparables } : {}) }, { 'critical-data-reconciled': 'PASS' }); },
    'data-forensics': (context) => {
      if (!context.artifacts.data_bundle) return blocked('data forensics BLOCKED — data bundle is absent.', 'critical-data-reconciled');
      const audit = auditDataBundle(context.artifacts.data_bundle, verifiedDocuments.map((document) => document.document_id));
      if (audit.errors.length) return blocked(`data forensics BLOCKED — ${audit.errors.join('; ')}`, 'critical-data-reconciled', audit.source_ids);
      return pass({ data_forensics: audit }, { 'critical-data-reconciled': 'PASS' }, audit.source_ids);
    },
    'monetary-analysis': (context) => analysisNeeds('monetary', context),
    'banking-analysis': (context) => analysisNeeds('banking', context),
    'fiscal-analysis': (context) => analysisNeeds('fiscal', context),
    'exchange-rate-analysis': (context) => analysisNeeds('exchange-rate', context),
    'dollarization-analysis': (context) => analysisNeeds('dollarization', context),
    'monetary-flow-analysis': (context) => monetaryFlowExecutor(context, verifiedDocuments.map((document) => document.document_id)),
    'currency-board-analysis': (context) => analysisNeeds('currency-board', context),
    'historical-comparables': (context) => {
      if (!context.artifacts.verified_source_count) return blocked('historical comparables BLOCKED — no verified sources in the evidence bundle.');
      const comparables = context.artifacts.historical_comparables;
      if (!comparables) return blocked('historical comparables BLOCKED — explicit historical_comparables evidence is absent.');
      return pass({ historical_comparables_analysis: { status: 'EVIDENCE_BOUND', comparables } });
    },
    'stress-test': (context) => analysisNeeds('stress-test', context),
    'posture-matrix': postureExecutor,
    'red-team': redTeamExecutor,
    'blue-team': blueTeamExecutor,
    'red-team-2': secondRedExecutor,
    'data-audit': (context) => {
      const audit = context.artifacts.data_forensics as { errors?: string[]; checked?: number } | undefined;
      if (!audit) return blocked('data audit BLOCKED — data-forensics artifact is absent.');
      if (audit.errors?.length) return blocked(`data audit BLOCKED — ${audit.errors.join('; ')}`, 'critical-data-reconciled');
      return pass({ data_audit: { status: 'PASS', checked: audit.checked ?? 0 } });
    },
    'math-audit': (context) => {
      const audit = auditCalculationArtifacts(context.artifacts);
      if (!audit.checked) return blocked('math audit BLOCKED — no calculation artifacts are available.', 'calculations-reproduced');
      if (audit.errors.length) return blocked(`math audit BLOCKED — ${audit.errors.join('; ')}`, 'calculations-reproduced', audit.source_ids);
      return pass({ math_audit: audit }, { 'calculations-reproduced': 'PASS' }, audit.source_ids);
    },
    'citation-audit': (context) => context.gates['citations-verified'] === 'PASS' ? pass({ citation_audit: { status: 'PASS' } }) : blocked('citation audit BLOCKED — citation gate is not passed.'),
    chief: (context) => {
      if (context.gates['red-blue-red-complete'] !== 'PASS') return blocked('Chief arbitration BLOCKED — Red/Blue/Red II gate is not passed.', 'chief-approved');
      const packet = { status: 'AVAILABLE_FOR_REVIEW', review_required: false, review_stage: 'post-run', review_scope: 'policy/crisis output and supporting evidence', generated_by: 'haeis-chief', note: 'Optional human review is available after automated execution and does not gate the run.' };
      return pass({ chief_approval: { status: 'AUTOMATED_ARBITRATION' }, human_review_packet: packet }, { 'chief-approved': 'PASS' });
    },
    'policy-decision': (context) => {
      const controls = canIssueFinalRecommendation({ criticalDataReconciled: context.gates['critical-data-reconciled'] === 'PASS', calculationsReproduced: context.gates['calculations-reproduced'] === 'PASS', citationsVerified: context.gates['citations-verified'] === 'PASS', redBlueRedComplete: context.gates['red-blue-red-complete'] === 'PASS', catastrophicRiskOpen: Boolean(context.artifacts.catastrophic_risk_open) });
      if (!controls) return blocked('policy decision BLOCKED — one or more final recommendation controls are not passed.');
      const readiness = context.artifacts.intake_readiness as { readiness?: string } | undefined;
      if (readiness?.readiness !== 'RECOMMENDATION_READY') return blocked('policy decision BLOCKED — intake is not recommendation-ready.');
      const plans = context.artifacts.evidence_search_plans as EvidenceSearchPlan[] | undefined;
      if (!plans?.length) return blocked('policy decision BLOCKED — anti-confirmation evidence-search plans are absent.');
      for (const plan of plans) { const errors = validateEvidenceSearchPlan(plan, options.documents); if (errors.length) return blocked(`policy decision BLOCKED — evidence-search plan invalid: ${errors.join('; ')}`); }
      return pass({ policy_decision: { status: 'REVIEWED', evidence_search_plan_count: plans.length } });
    }
  };
  return executors;
}
