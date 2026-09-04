import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(new URL('..', import.meta.url).pathname);
const retrievalDate = '2026-08-25';
const mappings = [
  { file: 'DOC-WB-VEN-GDP-2026.json', source_id: 'DOC-WB-VEN-GDP-2026', indicator: 'NY.GDP.MKTP.CD', variable: 'nominal_GDP_USD', domain: 'MACRO', unit: 'USD current', currency: 'USD', real_or_nominal: 'NOMINAL' },
  { file: 'DOC-WB-VEN-GDP-GROWTH-2026.json', source_id: 'DOC-WB-VEN-GDP-GROWTH-2026', indicator: 'NY.GDP.MKTP.KD.ZG', variable: 'real_GDP_growth', domain: 'MACRO', unit: 'percent', currency: null, real_or_nominal: 'REAL' },
  { file: 'DOC-WB-VEN-INFLATION-2026.json', source_id: 'DOC-WB-VEN-INFLATION-2026', indicator: 'FP.CPI.TOTL.ZG', variable: 'CPI_inflation', domain: 'MACRO', unit: 'percent', currency: null, real_or_nominal: 'NOT_APPLICABLE' },
  { file: 'DOC-WB-VEN-OIL-RENTS-2026.json', source_id: 'DOC-WB-VEN-OIL-RENTS-2026', indicator: 'NY.GDP.PETR.RT.ZS', variable: 'oil_rents_percent_GDP', domain: 'OIL', unit: 'percent of GDP', currency: null, real_or_nominal: 'NOT_APPLICABLE' },
  { file: 'DOC-WB-VEN-REMITTANCES-2026.json', source_id: 'DOC-WB-VEN-REMITTANCES-2026', indicator: 'BX.TRF.PWKR.CD.DT', variable: 'remittances_received_USD', domain: 'EXTERNAL', unit: 'USD current', currency: 'USD', real_or_nominal: 'NOMINAL' }
];
const documents = JSON.parse(readFileSync(resolve(root, 'rag/document-index.json'), 'utf8')).documents;
const byId = new Map(documents.map((document) => [document.document_id, document]));
const observations = [];
for (const mapping of mappings) {
  const source = byId.get(mapping.source_id);
  if (!source || source.status !== 'VERIFIED') throw new Error(`source is not VERIFIED: ${mapping.source_id}`);
  const payload = JSON.parse(readFileSync(resolve(root, 'documents/acquired', mapping.file), 'utf8'));
  const rows = Array.isArray(payload) ? payload[1] : null;
  if (!Array.isArray(rows)) throw new Error(`unexpected World Bank response shape: ${mapping.file}`);
  for (const row of rows) {
    if (row.indicator?.id !== mapping.indicator || row.value === null || row.value === undefined) continue;
    const year = String(row.date);
    if (!/^\d{4}$/.test(year) || !Number.isFinite(row.value)) throw new Error(`invalid World Bank row: ${mapping.file}/${row.date}`);
    observations.push({
      country: 'Venezuela', variable: mapping.variable, date: `${year}-12-31`, frequency: 'annual', value: row.value, unit: mapping.unit, currency: mapping.currency,
      real_or_nominal: mapping.real_or_nominal, source: 'World Bank API', source_id: mapping.source_id, publication_date: null, retrieval_date: retrievalDate,
      dataset_id: 'VEN-WORLD-BANK-MACRO-CONTEXT', methodology: `World Bank API indicator ${mapping.indicator}; null rows omitted without imputation.`,
      transformation_applied: ['API year converted to YYYY-12-31'], confidence_score: 0.75, verification_status: 'VERIFIED', revision_status: 'UNKNOWN', domain: mapping.domain,
      notes: 'Verified macro-context observation. The source artifact lacks a publication/release date and does not populate BCV, banking, reserve, fiscal, or monetary-flow gates.'
    });
  }
}
const keys = new Set();
for (const observation of observations) {
  const key = `${observation.variable}|${observation.date}`;
  if (keys.has(key)) throw new Error(`duplicate observation: ${key}`);
  keys.add(key);
}
writeFileSync(resolve(root, 'datasets/venezuela-world-bank-observations.json'), JSON.stringify({ dataset_id: 'VEN-WORLD-BANK-MACRO-CONTEXT', status: 'VERIFIED_SOURCE_BOUND_CONTEXT_ONLY', observations }, null, 2));
console.log(JSON.stringify({ status: 'PASS', observations: observations.length, output: 'datasets/venezuela-world-bank-observations.json' }, null, 2));
