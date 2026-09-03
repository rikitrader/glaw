import type { SourceRecord, SourceStatus } from './types.ts';
import { validateSourceRecord } from './manifest-validator.ts';

export interface IntakeDecision { status: SourceStatus; errors: string[]; nextAction: string; }

export function intakeSource(record: Partial<SourceRecord>): IntakeDecision {
  const errors = validateSourceRecord(record);
  if (errors.length) return { status: 'MISSING', errors, nextAction: 'SOURCE REQUIRED — complete metadata before retrieval or attribution.' };
  if (!record.source_url && record.status !== 'RESTRICTED') return { status: 'FOUND', errors: ['source_url'], nextAction: 'SOURCE REQUIRED — add lawful public location or document access basis.' };
  if (record.primary_source && record.status === 'VERIFIED' && !record.citation_anchor) return { status: 'FOUND', errors: ['citation_anchor'], nextAction: 'ATTRIBUTION BLOCKED — add page or section anchor.' };
  return { status: record.status as SourceStatus, errors: [], nextAction: record.status === 'VERIFIED' ? 'Eligible for citation audit.' : 'Independent verification required.' };
}
