export type IntakeStatus = 'DRAFT' | 'RESEARCH_INTAKE_ONLY' | 'READY_FOR_ANALYSIS' | 'BLOCKED';
export type DataStatus = 'KNOWN' | 'ESTIMATED' | 'DISPUTED' | 'UNAVAILABLE';
export type IntakeReadiness = 'RESEARCH_READY' | 'ANALYSIS_READY' | 'RECOMMENDATION_READY' | 'BLOCKED';
export interface IntakeReadinessResult { readiness: IntakeReadiness; blockers: string[]; warnings: string[]; }

export interface IntakeDataItem {
  name: string;
  status: DataStatus;
  value: number | string | null;
  unit: string | null;
  series_id?: string | null;
  observation_date: string | null;
  release_date?: string | null;
  revision_date?: string | null;
  vintage?: string | null;
  source_ids: string[];
}
export interface Intake { intake_id: string; question: string; country: string; output_mode: string; data_intake: IntakeDataItem[]; source_ids: string[]; critical_unknowns: string[]; /** Deprecated compatibility field; never gates execution. */ human_reviewer?: string; status: IntakeStatus; monetary_flow_input?: unknown; historical_comparables?: unknown; }

export function validateIntake(intake: Partial<Intake>, availableSourceIds?: string[]): string[] {
  const errors: string[] = [];
  for (const field of ['intake_id', 'question', 'country', 'output_mode'] as const) if (!intake[field]) errors.push(`${field} is required`);
  if (!Array.isArray(intake.data_intake)) errors.push('data_intake must be an array');
  if (!Array.isArray(intake.source_ids)) errors.push('source_ids must be an array');
  const outputModes = ['RESEARCH', 'ANALYSIS', 'DEBATE', 'POLICY', 'HISTORICAL', 'CALCULATION', 'CRISIS', 'ACADEMIC', 'EXECUTIVE'];
  if (intake.output_mode && !outputModes.includes(intake.output_mode)) errors.push(`invalid output_mode: ${intake.output_mode}`);
  if (availableSourceIds) for (const sourceId of intake.source_ids ?? []) if (!availableSourceIds.includes(sourceId)) errors.push(`unknown source_id: ${sourceId}`);
  for (const item of intake.data_intake ?? []) {
    if (!item.name) errors.push('data item name is required');
    if (!['KNOWN', 'ESTIMATED', 'DISPUTED', 'UNAVAILABLE'].includes(item.status)) errors.push(`invalid data status for ${item.name}`);
    if (item.status !== 'UNAVAILABLE' && item.value === null) errors.push(`data item ${item.name} has status ${item.status} but no value`);
    if (item.status === 'KNOWN' && (!item.source_ids?.length || !item.observation_date || !item.unit || !item.series_id)) errors.push(`known data item ${item.name} requires source, series_id, observation date, and unit`);
    if (item.value !== null && (!item.source_ids?.length || !item.observation_date || !item.unit)) errors.push(`data item ${item.name} requires source, observation date, and unit when populated`);
    for (const dateField of ['observation_date', 'release_date', 'revision_date'] as const) {
      const value = item[dateField];
      if (value !== null && value !== undefined && !/^\d{4}-\d{2}-\d{2}$/.test(value)) errors.push(`data item ${item.name} has invalid ${dateField}; expected YYYY-MM-DD`);
    }
  }
  return errors;
}

export function intakeCanStartAnalysis(intake: Partial<Intake>, availableSourceIds?: string[]): boolean {
  const errors = validateIntake(intake, availableSourceIds);
  return errors.length === 0 && intake.status !== 'BLOCKED';
}

export function classifyIntakeReadiness(intake: Partial<Intake>, availableSourceIds: string[] = [], verifiedSourceIds: string[] = []): IntakeReadinessResult {
  const errors = validateIntake(intake, availableSourceIds);
  if (errors.length || intake.status === 'BLOCKED') return { readiness: 'BLOCKED', blockers: errors.length ? errors : ['intake status is BLOCKED'], warnings: [] };
  const warnings: string[] = []; const blockers: string[] = [];
  if (!intake.source_ids?.length) blockers.push('no source IDs supplied');
  if ((intake.data_intake ?? []).some((item) => item.status === 'UNAVAILABLE')) blockers.push('one or more data items are unavailable');
  if ((intake.source_ids ?? []).some((sourceId) => !verifiedSourceIds.includes(sourceId))) blockers.push('one or more intake sources are not verified');
  if ((intake.data_intake ?? []).some((item) => ['ESTIMATED', 'DISPUTED'].includes(item.status))) warnings.push('estimated or disputed data require explicit disclosure in analysis');
  if (blockers.length) return { readiness: 'RESEARCH_READY', blockers, warnings };
  if ((intake.critical_unknowns ?? []).length) return { readiness: 'ANALYSIS_READY', blockers: ['critical unknowns remain'], warnings };
  if (['POLICY', 'CRISIS', 'EXECUTIVE'].includes(intake.output_mode ?? '')) return { readiness: 'RECOMMENDATION_READY', blockers: [], warnings };
  return { readiness: 'ANALYSIS_READY', blockers: [], warnings };
}
