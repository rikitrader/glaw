import type { SourceRecord } from './types.ts';

export const REQUIRED_SKILL_FIELDS = ['id', 'name', 'version', 'description', 'category', 'topics', 'purpose', 'inputs', 'outputs', 'required_sources', 'retrieval_strategy', 'calculations', 'assumptions', 'failure_conditions', 'evaluation_rubric', 'red_team_tests', 'blue_team_tests', 'unit_tests', 'integration_tests'];

export function validateSourceRecord(record: Partial<SourceRecord>): string[] {
  const required: Array<keyof SourceRecord> = ['document_id', 'author', 'title', 'document_type', 'country', 'topic', 'primary_source', 'authority_level', 'confidence', 'status'];
  return required.filter((key) => record[key] === undefined || record[key] === null || (typeof record[key] === 'string' && record[key] === '')) as string[];
}

export function validateRequiredSkillFields(manifest: Record<string, unknown>): string[] {
  return REQUIRED_SKILL_FIELDS.filter((field) => {
    const value = manifest[field];
    return value === undefined || value === null || (typeof value === 'string' && value.trim() === '');
  });
}
