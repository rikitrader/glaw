import type { IndexedDocument } from './citations.ts';
import { POSTURES } from './posture-index.ts';
import type { LegalInstrumentRecord } from './legal-verifier.ts';
import { validateEvidenceBoundAssessment, type EvidenceBoundAssessment } from './posture-store.ts';

export interface CompletionAuditInput {
  documents: IndexedDocument[];
  episodes: Array<{ id: string }>;
  postureAssessments: EvidenceBoundAssessment[];
  legalInstruments: LegalInstrumentRecord[];
  courtCases: Array<{ status?: string }>;
  benchmarkCases: Array<{ status?: string }>;
  forecastAuditRecords: string[];
  todoText: string;
}

export interface CompletionAuditReport {
  generated_at: string;
  source_status_counts: Record<string, number>;
  superseded_restricted_source_count: number;
  unresolved_restricted_source_count: number;
  verified_source_count: number;
  verified_primary_source_count: number;
  verified_hanke_primary_count: number;
  verified_metadata_only_count: number;
  posture: { expected_cells: number; assessed_cells: number; coverage_ratio: number };
  posture_validation_errors: Array<{ cell: string; errors: string[] }>;
  duplicate_posture_cells: string[];
  legal: { instrument_count: number; verified_instruments: number; court_case_count: number; verified_court_cases: number };
  benchmarks: { declared: number; executable: number; forecast_audit_records: number };
  unchecked_ledger_items: number;
  production_ready: boolean;
  blockers: string[];
  rule: string;
}

export function auditCompletion(input: CompletionAuditInput): CompletionAuditReport {
  const source_status_counts: Record<string, number> = {};
  for (const document of input.documents) source_status_counts[document.status] = (source_status_counts[document.status] ?? 0) + 1;
  const expectedCells = input.episodes.length * POSTURES.length;
  const postureValidationErrors = input.postureAssessments.flatMap((assessment) => {
    const cell = `${assessment.case_id}:${assessment.posture_id}`;
    const errors = validateEvidenceBoundAssessment(assessment, input.documents);
    return errors.length ? [{ cell, errors }] : [];
  });
  const seenPostureCells = new Set<string>();
  const duplicatePostureCells = new Set<string>();
  for (const assessment of input.postureAssessments) {
    const cell = `${assessment.case_id}:${assessment.posture_id}`;
    if (seenPostureCells.has(cell)) duplicatePostureCells.add(cell);
    seenPostureCells.add(cell);
  }
  const invalidPostureCells = new Set(postureValidationErrors.map((entry) => entry.cell));
  const assessedCells = new Set(input.postureAssessments
    .map((assessment) => `${assessment.case_id}:${assessment.posture_id}`)
    .filter((cell) => !invalidPostureCells.has(cell))).size;
  const blockers: string[] = [];
  const verifiedDocuments = input.documents.filter((document) => document.status === 'VERIFIED');
  const verifiedSuperseded = new Set(verifiedDocuments.flatMap((document) => [...(document.supersedes ?? []), ...(document.bounded_replacement_for ?? [])]));
  const restrictedDocuments = input.documents.filter((document) => document.status === 'RESTRICTED');
  const supersededRestrictedSourceCount = restrictedDocuments.filter((document) => verifiedSuperseded.has(document.document_id)).length;
  const unresolvedRestrictedSourceCount = restrictedDocuments.length - supersededRestrictedSourceCount;
  const verifiedMetadataOnly = verifiedDocuments.filter((document) => document.document_type === 'bibliographic-record' || document.primary_source === false);
  const verifiedPrimary = verifiedDocuments.filter((document) => !verifiedMetadataOnly.includes(document));
  const verifiedHankePrimary = verifiedPrimary.filter((document) => document.author.some((author) => author.toLocaleLowerCase().includes('hanke')));
  if (unresolvedRestrictedSourceCount || (source_status_counts.FOUND ?? 0)) blockers.push('source corpus contains unresolved restricted or unverified records');
  if (!verifiedHankePrimary.length) blockers.push('no verified primary Hanke publication is available');
  if (assessedCells < expectedCells) blockers.push(`posture coverage is incomplete: ${assessedCells}/${expectedCells}`);
  if (postureValidationErrors.length) blockers.push(`posture evidence validation failed for ${new Set(postureValidationErrors.map((entry) => entry.cell)).size} cell(s)`);
  if (duplicatePostureCells.size) blockers.push(`duplicate posture cells detected: ${duplicatePostureCells.size}`);
  const verifiedLegal = input.legalInstruments.filter((instrument) => instrument.status === 'VERIFIED').length;
  const verifiedCourtCases = input.courtCases.filter((courtCase) => courtCase.status === 'VERIFIED').length;
  if (verifiedLegal < input.legalInstruments.length || input.courtCases.length === 0 || verifiedCourtCases < input.courtCases.length) blockers.push('legal/institutional authority coverage is incomplete');
  const executableBenchmarks = input.benchmarkCases.filter((benchmark) => benchmark.status === 'executable').length;
  if (!executableBenchmarks) blockers.push('no executable historical benchmark is cataloged');
  if (input.forecastAuditRecords.length === 0) blockers.push('Hanke forecast audit has no verified primary records');
  const uncheckedLedgerItems = (input.todoText.match(/^- \[ \]/gm) ?? []).length;
  if (uncheckedLedgerItems) blockers.push(`${uncheckedLedgerItems} ledger work items remain unchecked`);
  return { generated_at: new Date().toISOString(), source_status_counts, superseded_restricted_source_count: supersededRestrictedSourceCount, unresolved_restricted_source_count: unresolvedRestrictedSourceCount, verified_source_count: verifiedDocuments.length, verified_primary_source_count: verifiedPrimary.length, verified_hanke_primary_count: verifiedHankePrimary.length, verified_metadata_only_count: verifiedMetadataOnly.length, posture: { expected_cells: expectedCells, assessed_cells: assessedCells, coverage_ratio: expectedCells ? assessedCells / expectedCells : 0 }, posture_validation_errors: postureValidationErrors, duplicate_posture_cells: [...duplicatePostureCells], legal: { instrument_count: input.legalInstruments.length, verified_instruments: verifiedLegal, court_case_count: input.courtCases.length, verified_court_cases: verifiedCourtCases }, benchmarks: { declared: input.benchmarkCases.length, executable: executableBenchmarks, forecast_audit_records: input.forecastAuditRecords.length }, unchecked_ledger_items: uncheckedLedgerItems, production_ready: blockers.length === 0, blockers, rule: 'This audit never treats missing, restricted, or unverified evidence as complete; explicit supersession or bounded-replacement records are counted only for the documented scope of the verified replacement.' };
}
