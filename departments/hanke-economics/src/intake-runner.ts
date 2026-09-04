import { classifyIntakeReadiness, validateIntake, type Intake, type IntakeReadinessResult } from './intake.ts';
import type { IndexedDocument } from './citations.ts';

export interface IntakeRunReport {
  intake_id: string;
  validation_errors: string[];
  readiness: IntakeReadinessResult;
  source_status_counts: Record<string, number>;
  recommendation_allowed: boolean;
  rule: string;
}

export function createIntakeRunReport(intake: Intake, documents: IndexedDocument[]): IntakeRunReport {
  const availableSourceIds = documents.map((document) => document.document_id);
  const verifiedSourceIds = documents.filter((document) => document.status === 'VERIFIED').map((document) => document.document_id);
  const source_status_counts: Record<string, number> = {};
  for (const document of documents) source_status_counts[document.status] = (source_status_counts[document.status] ?? 0) + 1;
  const validation_errors = validateIntake(intake, availableSourceIds);
  const readiness = classifyIntakeReadiness(intake, availableSourceIds, verifiedSourceIds);
  return { intake_id: intake.intake_id, validation_errors, readiness, source_status_counts, recommendation_allowed: validation_errors.length === 0 && readiness.readiness === 'RECOMMENDATION_READY', rule: 'A report never upgrades sources or data; recommendation_allowed is false unless all intake and readiness controls pass.' };
}
