import type { WorkflowRun } from './workflow.ts';
import { CHART_SPECIFICATIONS } from './chart-registry.ts';
import { buildDataCompletenessDashboard, validateDataCompletenessDashboard, validateEvidenceTable, type DataCompletenessRow, type EvidenceTableRow } from './review-quality.ts';
import { calculateReadinessIndex, type ReadinessEvidence, type ReadinessIndexResult } from './readiness-index.ts';

export const DATA_STATUSES = ['VERIFIED', 'PROVISIONAL', 'ESTIMATED', 'MODELED', 'IMPUTED', 'DISPUTED', 'STALE', 'UNAVAILABLE'] as const;
export type DataStatus = typeof DATA_STATUSES[number];
export const SECTION_STATUSES = ['COMPLETE', 'PARTIAL', 'BLOCKED', 'UNAVAILABLE'] as const;
export type SectionStatus = typeof SECTION_STATUSES[number];
export const CLAIM_LABELS = ['HANKE-DIRECT', 'HANKE-FRAMEWORK', 'SYSTEM-INFERENCE', 'SYSTEM-CALCULATION', 'HISTORICAL-EVIDENCE', 'EXTERNAL-VIEW', 'RED-TEAM-CHALLENGE', 'BLUE-TEAM-RESPONSE', 'UNRESOLVED'] as const;
export type ClaimLabel = typeof CLAIM_LABELS[number];

export interface ReportIndexSection { id: string; title: string; }
export interface ReportIndexPart { id: string; title: string; page_target: string; sections: ReportIndexSection[]; }
export interface FinalReportIndex {
  index_id: string;
  version: string;
  title: string;
  required_data_statuses: string[];
  required_claim_labels: string[];
  parts: ReportIndexPart[];
  required_data_domains: string[];
  required_formulas: string[];
  required_derived_indicators: string[];
  required_charts: string[];
  page_allocation: { main_report_target_pages: number; appendix_target_pages: string };
}

export interface ReportClaim { text: string; label: ClaimLabel; source_ids: string[]; calculation_ids?: string[]; uncertainty?: string; }
export interface ReportSection {
  section_id: string;
  title: string;
  status: SectionStatus;
  data_status: DataStatus;
  narrative: string;
  claims: ReportClaim[];
  source_ids: string[];
  calculation_ids: string[];
  missing_data: string[];
  gate_dependencies: string[];
}
export interface ReportMetric { name: string; status: DataStatus | 'BLOCKED' | 'NOT_EXECUTED'; value?: number | string | null; source_ids: string[]; notes: string; }
export interface IndexedFinalReport {
  report_id: string;
  index_id: string;
  index_version: string;
  run_id: string;
  generated_at: string;
  report_status: 'RECOMMENDATION_READY' | 'BLOCKED' | 'RESEARCH_ONLY';
  decision: string;
  sections: ReportSection[];
  data_inventory: ReportMetric[];
  formulas: ReportMetric[];
  charts: ReportMetric[];
  readiness_index: ReadinessIndexResult;
  data_completeness: DataCompletenessRow[];
  evidence_table: EvidenceTableRow[];
  gates: Record<string, { status: string; owner: string; evidence_ids: string[]; reason?: string }>;
  findings: unknown[];
  source_ids: string[];
  review: { review_required: false; status: 'AVAILABLE_FOR_REVIEW'; stage: 'post-run' };
}

const allSections = (index: FinalReportIndex): ReportIndexSection[] => index.parts.flatMap((part) => part.sections);

export function validateIndexedFinalReport(report: IndexedFinalReport, index: FinalReportIndex): string[] {
  const errors: string[] = [];
  if (index.parts.length !== 24) errors.push(`enforced report index must contain 24 parts, found ${index.parts.length}`);
  for (const status of DATA_STATUSES) if (!index.required_data_statuses.includes(status)) errors.push(`report index omits required data status: ${status}`);
  if (report.index_id !== index.index_id) errors.push('report index_id does not match the enforced report index');
  if (report.index_version !== index.version) errors.push('report index_version does not match the enforced report index');
  const expected = allSections(index);
  const actualIds = report.sections.map((section) => section.section_id);
  const expectedIds = expected.map((section) => section.id);
  if (new Set(actualIds).size !== actualIds.length) errors.push('duplicate report section');
  for (const id of expectedIds) if (!actualIds.includes(id)) errors.push(`missing required report section: ${id}`);
  for (const id of actualIds) if (!expectedIds.includes(id)) errors.push(`unexpected report section: ${id}`);
  for (const section of report.sections) {
    if (!SECTION_STATUSES.includes(section.status)) errors.push(`invalid section status: ${section.section_id}`);
    if (!DATA_STATUSES.includes(section.data_status)) errors.push(`invalid data status: ${section.section_id}`);
    if (!section.narrative.trim()) errors.push(`section narrative is required: ${section.section_id}`);
    for (const claim of section.claims) {
      if (!CLAIM_LABELS.includes(claim.label)) errors.push(`invalid claim label: ${section.section_id}`);
      if (!claim.source_ids.length && !claim.calculation_ids?.length && !claim.uncertainty) errors.push(`claim lacks evidence or uncertainty: ${section.section_id}`);
      if (claim.label === 'HANKE-DIRECT' && !claim.source_ids.length) errors.push(`HANKE-DIRECT claim lacks source: ${section.section_id}`);
    }
  }
  for (const required of index.required_data_domains) if (!report.data_inventory.some((metric) => metric.name === required)) errors.push(`missing required data-domain record: ${required}`);
  for (const required of [...index.required_formulas, ...index.required_derived_indicators]) if (!report.formulas.some((metric) => metric.name === required)) errors.push(`missing required formula/indicator record: ${required}`);
  if (report.charts.length !== CHART_SPECIFICATIONS.length) errors.push(`report must carry all ${CHART_SPECIFICATIONS.length} chart records`);
  for (const chart of CHART_SPECIFICATIONS) if (!report.charts.some((metric) => metric.name === chart.title)) errors.push(`missing chart specification: ${chart.chart_id}`);
  for (const [gate, record] of Object.entries(report.gates)) {
    if (!['OPEN', 'PASS', 'BLOCKED'].includes(record.status)) errors.push(`invalid gate status: ${gate}`);
    if (!record.owner.trim()) errors.push(`gate owner is required: ${gate}`);
    if (!Array.isArray(record.evidence_ids)) errors.push(`gate evidence_ids must be an array: ${gate}`);
  }
  if (report.report_status === 'RECOMMENDATION_READY' && Object.values(report.gates).some((gate) => gate.status !== 'PASS')) errors.push('recommendation-ready report has a non-PASS gate');
  if (report.review.review_required !== false) errors.push('human review must remain post-run and non-gating');
  if (!Array.isArray(report.data_completeness)) errors.push('data completeness dashboard is required');
  else errors.push(...validateDataCompletenessDashboard(report.data_completeness).map((error) => `data completeness: ${error}`));
  if (!Array.isArray(report.evidence_table)) errors.push('evidence table is required');
  else errors.push(...validateEvidenceTable(report.evidence_table).map((error) => `evidence table: ${error}`));
  if (!report.readiness_index || !['CALCULATED', 'DATA_INSUFFICIENT'].includes(report.readiness_index.status)) errors.push('readiness index status is required');
  if (report.readiness_index.status === 'CALCULATED' && report.readiness_index.overall_score === null) errors.push('calculated readiness index requires a score');
  if (report.readiness_index.status === 'DATA_INSUFFICIENT' && report.readiness_index.overall_score !== null) errors.push('data-insufficient readiness index cannot carry a score');
  return [...new Set(errors)];
}

const gateRecords = (run: WorkflowRun) => Object.fromEntries(Object.entries(run.gate_records).map(([gate, record]) => [gate, { status: record.status, owner: record.owner, evidence_ids: record.evidence_ids, ...(record.reason ? { reason: record.reason } : {}) }]));

export function buildIndexedFinalReport(index: FinalReportIndex, run: WorkflowRun): IndexedFinalReport {
  const firstBlock = Object.values(run.gate_records).find((record) => record.status === 'BLOCKED')?.reason ?? 'Required evidence is not yet verified.';
  const sourceIds = Array.isArray(run.artifacts.verified_source_ids) ? run.artifacts.verified_source_ids as string[] : [];
  const dataBundle = Array.isArray(run.artifacts.data_bundle) ? run.artifacts.data_bundle as Array<{ status?: string }> : [];
  const bundleStatus: DataStatus = dataBundle.some((item) => item.status === 'DISPUTED') ? 'DISPUTED' : dataBundle.length ? 'ESTIMATED' : 'UNAVAILABLE';
  const sections = allSections(index).map((section) => ({
    section_id: section.id,
    title: section.title,
    status: 'BLOCKED' as const,
    data_status: 'UNAVAILABLE' as const,
    narrative: `BLOCKED — ${firstBlock} This section requires source-bound data before a conclusion can be issued.`,
    claims: [{ text: 'No conclusion is issued from the current evidence bundle.', label: 'UNRESOLVED' as const, source_ids: [], uncertainty: firstBlock }],
    source_ids: [], calculation_ids: [], missing_data: index.required_data_domains, gate_dependencies: Object.keys(run.gates)
  }));
  const dataInventory = index.required_data_domains.map((name) => ({ name, status: bundleStatus, source_ids: sourceIds, notes: bundleStatus === 'UNAVAILABLE' ? 'Not supplied or not reconciled in the current run.' : `The run contains ${dataBundle.length} source-bound data item(s), but this domain is not promoted beyond ${bundleStatus} without domain-specific reconciliation.` }));
  const formulas = [...index.required_formulas, ...index.required_derived_indicators].map((name) => ({ name, status: 'BLOCKED' as const, source_ids: [], notes: 'Not executed because required inputs or gates are blocked; no value is inferred.' }));
  const charts = CHART_SPECIFICATIONS.map((chart) => ({ name: chart.title, status: 'UNAVAILABLE' as const, source_ids: [], notes: `${chart.chart_id}: chart withheld until the underlying dated series is verified.` }));
  const inventory = Array.isArray(run.artifacts.variable_inventory) ? run.artifacts.variable_inventory as Array<{ variable: string; domain: string; expected_observations?: number }> : index.required_data_domains.map((name) => ({ variable: `domain:${name}`, domain: 'REPORT-DOMAIN', expected_observations: 1 }));
  const observations = Array.isArray(run.artifacts.institutional_observations) ? run.artifacts.institutional_observations as Parameters<typeof buildDataCompletenessDashboard>[1] : [];
  const dataCompleteness = buildDataCompletenessDashboard(inventory.map((item) => ({ variable: item.variable, domain: item.domain, expected_observations: item.expected_observations ?? 1 })), observations, new Date().toISOString().slice(0, 10));
  const evidenceTable = [{
    claim_id: 'EVIDENCE-STATUS-001', claim: 'The current evidence bundle is not recommendation-grade.', evidence_supporting: [], evidence_contradicting: [], primary_sources: [], model_result: null,
    confidence: 'UNRESOLVED' as const, sensitivity: 'Not assessed because critical gates remain blocked.', final_assessment: 'UNRESOLVED', uncertainty: firstBlock
  }];
  const readinessEvidence = Array.isArray(run.artifacts.readiness_evidence) ? run.artifacts.readiness_evidence as ReadinessEvidence[] : [];
  const readiness_index = calculateReadinessIndex(readinessEvidence);
  return {
    report_id: `${run.run_id}-INDEXED-FINAL`, index_id: index.index_id, index_version: index.version, run_id: run.run_id,
    generated_at: new Date().toISOString(), report_status: 'BLOCKED',
    decision: 'DECISION BLOCKED — INSUFFICIENT EVIDENCE. The enforced report index is complete structurally, but no policy recommendation may be issued while critical gates remain open or blocked.',
    sections, data_inventory: dataInventory, formulas, charts, readiness_index, data_completeness: dataCompleteness, evidence_table: evidenceTable, gates: gateRecords(run), findings: run.findings, source_ids: sourceIds,
    review: { review_required: false, status: 'AVAILABLE_FOR_REVIEW', stage: 'post-run' }
  };
}

export function renderIndexedFinalReport(report: IndexedFinalReport, index: FinalReportIndex): string {
  const lines = [`# ${index.title}`, '', `Report ID: \`${report.report_id}\`  `, `Run: \`${report.run_id}\`  `, `Status: **${report.report_status}**`, '', `## Decision`, '', report.decision, '', '## Enforced data-status legend', '', DATA_STATUSES.map((status) => `- **${status}**`).join('\n'), ''];
  for (const part of index.parts) {
    lines.push(`## PART ${part.id} — ${part.title}`, '', `Page target: ${part.page_target}`, '');
    for (const section of part.sections) {
      const record = report.sections.find((candidate) => candidate.section_id === section.id)!;
      lines.push(`### ${section.id} ${section.title}`, '', `Status: **${record.status}**  `, `Data status: **${record.data_status}**`, '', record.narrative, '', `Missing data: ${record.missing_data.join('; ')}`, '');
    }
  }
  lines.push('## Gate status', '', '| Gate | Status | Owner | Evidence | Reason |', '|---|---|---|---|---|');
  for (const [gate, record] of Object.entries(report.gates)) lines.push(`| ${gate} | ${record.status} | ${record.owner} | ${record.evidence_ids.join(', ') || 'none'} | ${record.reason ?? ''} |`);
  lines.push('', '## Dollarization Readiness Index', '', `Status: **${report.readiness_index.status}**`, `Score: **${report.readiness_index.overall_score ?? 'DATA INSUFFICIENT'}**`, `Band: **${report.readiness_index.band}**`, `Blockers: ${report.readiness_index.blockers.join('; ') || 'none'}`, '', '## Data completeness dashboard', '', '| Variable/domain | Coverage | Observed | Missing | Latest | Sources | Confidence | Quality |', '|---|---:|---:|---:|---|---:|---:|---|', ...report.data_completeness.map((row) => `| ${row.variable} | ${row.coverage_percentage}% | ${row.observed_observations} | ${row.missing_observations} | ${row.latest_observation ?? 'UNAVAILABLE'} | ${row.source_count} | ${row.confidence ?? 'UNAVAILABLE'} | ${row.quality} |`), '', '## Evidence table', '', '| Claim ID | Claim | Supporting | Contradicting | Confidence | Assessment | Uncertainty |', '|---|---|---|---|---|---|---|', ...report.evidence_table.map((row) => `| ${row.claim_id} | ${row.claim} | ${row.evidence_supporting.join(', ') || 'none'} | ${row.evidence_contradicting.join(', ') || 'none'} | ${row.confidence} | ${row.final_assessment} | ${row.uncertainty} |`), '', '## Required formulas', '', ...report.formulas.map((formula) => `- **${formula.name}** — ${formula.status}. ${formula.notes}`), '', '## Required charts', '', ...report.charts.map((chart) => `- **${chart.name}** — ${chart.status}. ${chart.notes}`), '', '## Review', '', 'Human review is optional and post-run only: `review_required: false`.');
  return `${lines.join('\n')}\n`;
}
