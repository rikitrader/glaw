export interface ForensicDataItem {
  name: string;
  status: string;
  value: number | string | null;
  unit?: string | null;
  series_id?: string | null;
  observation_date?: string | null;
  release_date?: string | null;
  revision_date?: string | null;
  source_ids?: string[];
}

export interface DataForensicsResult { errors: string[]; warnings: string[]; checked: number; source_ids: string[]; }
const date = (value: unknown) => typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value);

export function auditDataBundle(raw: unknown, verifiedSourceIds: string[]): DataForensicsResult {
  if (!Array.isArray(raw)) return { errors: ['data bundle must be an array'], warnings: [], checked: 0, source_ids: [] };
  const errors: string[] = []; const warnings: string[] = []; const names = new Set<string>(); const source_ids = new Set<string>(); const verified = new Set(verifiedSourceIds);
  raw.forEach((item: ForensicDataItem, index) => {
    if (!item || typeof item !== 'object') { errors.push(`data item ${index} is not an object`); return; }
    const key = item.series_id || item.name;
    if (names.has(key)) errors.push(`duplicate data series: ${key}`); names.add(key);
    for (const sourceId of item.source_ids ?? []) { source_ids.add(sourceId); if (!verified.has(sourceId)) errors.push(`data item ${item.name} references non-verified source: ${sourceId}`); }
    if (!item.source_ids?.length) errors.push(`data item ${item.name} requires source_ids`);
    if (!item.unit) errors.push(`data item ${item.name} requires unit`);
    if (item.value !== null && typeof item.value !== 'number') errors.push(`data item ${item.name} requires numeric value for analysis`);
    if (typeof item.value === 'number' && !Number.isFinite(item.value)) errors.push(`data item ${item.name} has non-finite value`);
    if (item.status !== 'UNAVAILABLE' && !date(item.observation_date)) errors.push(`data item ${item.name} requires observation_date`);
    if (item.release_date && !date(item.release_date)) errors.push(`data item ${item.name} has invalid release_date`);
    if (item.revision_date && !date(item.revision_date)) errors.push(`data item ${item.name} has invalid revision_date`);
    if (date(item.observation_date) && date(item.release_date) && item.release_date! < item.observation_date!) warnings.push(`data item ${item.name} was released before its observation date; confirm vintage metadata`);
    if (date(item.release_date) && date(item.revision_date) && item.revision_date! < item.release_date!) errors.push(`data item ${item.name} has revision_date before release_date`);
  });
  return { errors, warnings, checked: raw.length, source_ids: [...source_ids] };
}
