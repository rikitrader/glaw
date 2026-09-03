import type { WorkflowRun } from './workflow.ts';

export interface HaeisCatalogEntry { id: string; kind: 'department' | 'agent' | 'skill' | 'rag' | 'intake' | 'workflow' | 'posture' | 'legal' | 'schema' | 'benchmark' | 'report' | 'policy' | 'scenario' | 'chart' | 'source'; path: string; status: 'ACTIVE_DEVELOPMENT' | 'VERIFIED' | 'PENDING'; }

export interface HaeisControlPlanePayload {
  run_id: string;
  organization_id: string;
  matter_id: string | null;
  workflow_id: string;
  status: WorkflowRun['status'];
  gate_records: WorkflowRun['gate_records'];
  events: Array<{ sequence: number; type: WorkflowRun['events'][number]['type']; payload?: Record<string, unknown> }>;
  human_review_packet?: { status: string; review_required: false; review_stage?: string; file_path?: string };
}

/** Convert a durable HAEIS run into the shape accepted by GLAW's HAEIS API. */
export function toHaeisControlPlanePayload(run: WorkflowRun, organizationId: string, matterId: string | null = null): HaeisControlPlanePayload {
  const packet = run.artifacts.human_review_packet;
  const human_review_packet = packet && typeof packet === 'object' && (packet as { review_required?: unknown }).review_required === false
    ? {
        status: String((packet as { status?: unknown }).status ?? 'AVAILABLE_FOR_REVIEW'),
        review_required: false as const,
        ...((packet as { review_stage?: unknown }).review_stage ? { review_stage: String((packet as { review_stage: unknown }).review_stage) } : {}),
        ...((packet as { file_path?: unknown }).file_path ? { file_path: String((packet as { file_path: unknown }).file_path) } : {})
      }
    : undefined;
  return {
    run_id: run.run_id,
    organization_id: organizationId,
    matter_id: matterId,
    workflow_id: run.workflow_id,
    status: run.status,
    gate_records: run.gate_records,
    events: run.events.map(({ sequence, type, payload }) => ({ sequence, type, ...(payload ? { payload } : {}) })),
    ...(human_review_packet ? { human_review_packet } : {})
  };
}

export const HAEIS_CATALOG: HaeisCatalogEntry[] = [
  { id: 'hanke-applied-economics', kind: 'department', path: 'department.yaml', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-agent-registry', kind: 'agent', path: 'agents/agent-registry.yaml', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-monetary-flow-agent', kind: 'agent', path: 'agents/monetary-flow-agent/agent-manifest.yaml', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-agent-manifest', kind: 'agent', path: 'agents/manifest.yaml', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-red-team-manifest', kind: 'agent', path: 'agents/red-team/agent-manifests.yaml', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-blue-team-manifest', kind: 'agent', path: 'agents/blue-team/agent-manifests.yaml', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-opposition-counsel-manifest', kind: 'agent', path: 'counsel/opposition-counsel/manifest.yaml', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-opposition-personas', kind: 'posture', path: 'counsel/opposition-counsel/persona-profiles.yaml', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-economic-review-committee', kind: 'agent', path: 'counsel/committee/committee-manifest.yaml', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-committee-opinion', kind: 'report', path: 'counsel/committee/final-committee-opinion.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-skill-root', kind: 'skill', path: 'skills', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-document-index', kind: 'rag', path: 'rag/document-index.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-book-corpus', kind: 'rag', path: 'books/hanke/index.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-monetary-flow-papers', kind: 'rag', path: 'books/hanke/monetary-flow-papers.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-source-gap-register', kind: 'rag', path: 'datasets/venezuela-source-gap-register.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-disputed-context-intake', kind: 'intake', path: 'intake/venezuela-disputed-context-2025.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-source-registry', kind: 'rag', path: 'rag/source-registry.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-posture-registry', kind: 'posture', path: 'postures/posture-registry.yaml', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-posture-evidence', kind: 'posture', path: 'postures/evidence-backed-assessments.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-legal-index', kind: 'legal', path: 'legal/legal-instrument-index.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-courtlistener-venezuela-index', kind: 'legal', path: 'legal/courtlistener-venezuela-index.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-case-index', kind: 'legal', path: 'legal/venezuela-case-index.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-case-index-schema', kind: 'schema', path: 'legal/venezuela-case-index.schema.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-court-record-balance-sheet-facts', kind: 'source', path: 'data/derived/court-record-balance-sheet-facts.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-citgo-primary-record-evidence', kind: 'source', path: 'data/derived/citgo-primary-record-evidence-2026-08-26.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-batch1-case-evidence', kind: 'source', path: 'data/derived/venezuela-batch1-case-evidence.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-schema-root', kind: 'schema', path: 'schemas', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-institutional-observation-schema', kind: 'schema', path: 'schemas/institutional-observation.schema.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-source-conflict-schema', kind: 'schema', path: 'schemas/source-conflict.schema.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-chart-spec-schema', kind: 'schema', path: 'schemas/chart-spec.schema.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-data-completeness-schema', kind: 'schema', path: 'schemas/data-completeness.schema.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-evidence-table-schema', kind: 'schema', path: 'schemas/evidence-table.schema.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-source-hierarchy', kind: 'source', path: 'sources/source-hierarchy.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-scenario-library', kind: 'scenario', path: 'scenarios/scenario-library.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-domain-registry', kind: 'rag', path: 'datasets/domain-registry.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-variable-inventory', kind: 'rag', path: 'datasets/venezuela-variable-inventory.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-source-of-truth-intake', kind: 'intake', path: 'intake/venezuela-source-of-truth-2026-08-25.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-current-secondary-leads', kind: 'source', path: 'datasets/venezuela-current-secondary-leads.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-encaje-event-schema', kind: 'schema', path: 'datasets/venezuela-encaje-event-schema.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-parallel-fx-schema', kind: 'schema', path: 'datasets/venezuela-parallel-fx-schema.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-banking-source-of-truth', kind: 'source', path: 'datasets/venezuela-banking-source-of-truth.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-bank-registry', kind: 'rag', path: 'datasets/venezuela-bank-registry.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-bank-stress-schema', kind: 'schema', path: 'schemas/bank-stress-test.schema.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-official-bank-site-registry', kind: 'intake', path: 'intake/venezuela-bank-site-registry.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-bank-site-acquisition', kind: 'source', path: 'scripts/acquire-bank-sites.mjs', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-reserve-liquidity-framework', kind: 'source', path: 'datasets/venezuela-reserve-liquidity-framework.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-sdr-observations', kind: 'rag', path: 'datasets/venezuela-sdr-observations.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-reserve-asset-schema', kind: 'schema', path: 'schemas/reserve-asset.schema.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-reserve-waterfall-schema', kind: 'schema', path: 'schemas/reserve-liquidity-waterfall.schema.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-world-bank-observations', kind: 'rag', path: 'datasets/venezuela-world-bank-observations.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-imf-mfs-observations', kind: 'rag', path: 'datasets/venezuela-imf-mfs-observations.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-historical-monetary-flow-audit', kind: 'report', path: 'datasets/venezuela-historical-monetary-flow-audit.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-venezuela-fiscal-debt-legal-workplan', kind: 'intake', path: 'datasets/venezuela-fiscal-debt-legal-workplan.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-debt-obligation-schema', kind: 'schema', path: 'schemas/debt-obligation.schema.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-debt-procedural-stage-schema', kind: 'schema', path: 'schemas/debt-procedural-stage.schema.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-source-conflict-registry', kind: 'rag', path: 'datasets/source-conflict-registry.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-policy-readiness-contract', kind: 'policy', path: 'policy/policy-readiness-contract.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-readiness-index-runtime', kind: 'policy', path: 'src/readiness-index.ts', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-policy-stop-go-conditions', kind: 'policy', path: 'policy/policy-stop-go-conditions.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-final-report-index', kind: 'report', path: 'reports/final-report-index.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-chart-registry', kind: 'chart', path: 'reports/chart-registry.json', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'hanke-benchmark-catalog', kind: 'benchmark', path: 'benchmarks/cases.jsonl', status: 'ACTIVE_DEVELOPMENT' },
  { id: 'venezuela-monetary-reform', kind: 'workflow', path: 'workflows/venezuela-monetary-reform.json', status: 'ACTIVE_DEVELOPMENT' }
  ,{ id: 'venezuela-opposition-counsel-review', kind: 'workflow', path: 'workflows/venezuela-opposition-counsel-review.yaml', status: 'ACTIVE_DEVELOPMENT' }
  ,{ id: 'hanke-opposition-counsel-schema', kind: 'schema', path: 'schemas/opposition-counsel-review.schema.json', status: 'ACTIVE_DEVELOPMENT' }
  ,{ id: 'hanke-committee-opinion-schema', kind: 'schema', path: 'schemas/committee-opinion.schema.json', status: 'ACTIVE_DEVELOPMENT' }
];

export function validateCatalog(resolve: (path: string) => boolean): string[] { return HAEIS_CATALOG.filter((entry) => !resolve(entry.path)).map((entry) => `${entry.kind} path missing: ${entry.path}`); }
