import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(new URL('..', import.meta.url).pathname);
const retrievalDate = '2026-08-25';
const mappings = [
  ['DOC-IMF-MFS-CBS-VEN-CURRENCY-2026', 'DOC-IMF-MFS-CBS-VEN-CURRENCY-2026.json', 'currency_in_circulation', 'MONETARY'],
  ['DOC-IMF-MFS-CBS-VEN-NFA-2026', 'DOC-IMF-MFS-CBS-VEN-S121_N_NFRA_CBS-2026.json', 'central_bank_net_foreign_assets', 'MONETARY'],
  ['DOC-IMF-MFS-CBS-VEN-NCG-2026', 'DOC-IMF-MFS-CBS-VEN-S121_N_NCO_S1311MIXED_CBS-2026.json', 'central_bank_net_claims_on_government', 'MONETARY'],
  ['DOC-IMF-MFS-CBS-VEN-PSCLAIMS-2026', 'DOC-IMF-MFS-CBS-VEN-S121_A_ACO_PS_CBS-2026.json', 'central_bank_claims_private_sector', 'MONETARY'],
  ['DOC-IMF-MFS-CBS-VEN-NRESCLAIMS-2026', 'DOC-IMF-MFS-CBS-VEN-S121_A_ACO_NRES_CBS-2026.json', 'central_bank_claims_nonresidents', 'MONETARY'],
  ['DOC-IMF-MFS-MA-VEN-BM-2026', 'DOC-IMF-MFS-MA-VEN-BM_MAI-2026.json', 'broad_money', 'MONETARY'],
  ['DOC-IMF-MFS-MA-VEN-BASE-2026', 'DOC-IMF-MFS-MA-VEN-NDMBM_MAI-2026.json', 'monetary_base', 'MONETARY'],
  ['DOC-IMF-MFS-MA-VEN-CURRENCY-2026', 'DOC-IMF-MFS-MA-VEN-CIC_OUTDCORP_MAI-2026.json', 'currency_outside_depository_corporations', 'MONETARY'],
  ['DOC-IMF-MFS-ODC-VEN-ODCORP_A_ACO_PS_ODCS-2026', 'DOC-IMF-MFS-ODC-VEN-ODCORP_A_ACO_PS_ODCS-2026.json', 'historical_MFS_ODC_claims_private_sector', 'BANKING'],
  ['DOC-IMF-MFS-ODC-VEN-ODCORP_A_F21_ACO_S121_ODCS-2026', 'DOC-IMF-MFS-ODC-VEN-ODCORP_A_F21_ACO_S121_ODCS-2026.json', 'historical_MFS_ODC_claims_central_bank', 'BANKING'],
  ['DOC-IMF-MFS-ODC-VEN-ODCORP_L_F22_IBM_ODCS-2026', 'DOC-IMF-MFS-ODC-VEN-ODCORP_L_F22_IBM_ODCS-2026.json', 'historical_MFS_ODC_transferable_deposits', 'BANKING'],
  ['DOC-IMF-MFS-ODC-VEN-ODCORP_L_F29_IBM_ODCS-2026', 'DOC-IMF-MFS-ODC-VEN-ODCORP_L_F29_IBM_ODCS-2026.json', 'historical_MFS_ODC_other_deposits', 'BANKING'],
  ['DOC-IMF-MFS-ODC-VEN-ODCORP_L_F4_ODCS-2026', 'DOC-IMF-MFS-ODC-VEN-ODCORP_L_F4_ODCS-2026.json', 'historical_MFS_ODC_loans', 'BANKING'],
  ['DOC-IMF-MFS-ODC-VEN-ODCORP_NETAL_NCO_S1311MIXED_ODCS-2026', 'DOC-IMF-MFS-ODC-VEN-ODCORP_NETAL_NCO_S1311MIXED_ODCS-2026.json', 'historical_MFS_ODC_net_claims_government', 'BANKING']
];
const documents = JSON.parse(readFileSync(resolve(root, 'rag/document-index.json'), 'utf8')).documents;
const byId = new Map(documents.map((document) => [document.document_id, document]));
const observations = [];
const lastDay = (year, month) => new Date(Date.UTC(year, month, 0)).toISOString().slice(0, 10);
for (const [sourceId, file, variable, domain] of mappings) {
  const source = byId.get(sourceId);
  if (!source || source.status !== 'VERIFIED' || !source.sha256) throw new Error(`source is not verified and hashed: ${sourceId}`);
  const payload = JSON.parse(readFileSync(resolve(root, 'documents/acquired', file), 'utf8')).data;
  const dimensions = payload.structures?.[0]?.dimensions;
  const seriesDimensions = dimensions?.series;
  const timeValues = dimensions?.observation?.find((dimension) => dimension.id === 'TIME_PERIOD')?.values;
  const series = payload.dataSets?.[0]?.series?.['0:0:0:0'];
  if (!series || !Array.isArray(timeValues)) throw new Error(`unsupported SDMX shape: ${file}`);
  const country = seriesDimensions?.find((dimension) => dimension.id === 'COUNTRY')?.values?.[0]?.id;
  const frequency = seriesDimensions?.find((dimension) => dimension.id === 'FREQUENCY')?.values?.[0]?.id;
  if (country !== 'VEN' || frequency !== 'M') throw new Error(`unexpected SDMX dimensions: ${file}`);
  for (const [index, tuple] of Object.entries(series.observations ?? {})) {
    const rawDate = timeValues[Number(index)]?.value;
    const value = Number(tuple?.[0]);
    const match = /^(\d{4})-M(\d{2})$/.exec(String(rawDate));
    if (!match || !Number.isFinite(value)) throw new Error(`invalid SDMX observation: ${sourceId}/${rawDate}`);
    observations.push({
      country: 'Venezuela', variable, date: lastDay(Number(match[1]), Number(match[2])), frequency: 'monthly', value,
      unit: 'XDC (provider-defined)', currency: null, real_or_nominal: 'NOMINAL', source: 'IMF SDMX MFS', source_id: sourceId,
      publication_date: null, retrieval_date: retrievalDate, dataset_id: 'VEN-IMF-MFS-HISTORICAL',
      methodology: 'Provider-defined IMF SDMX series; non-null observations only; no relabeling into current monetary, banking, reserve, or fiscal aggregates.',
      transformation_applied: ['SDMX YYYY-M## period converted to month-end YYYY-MM-DD'], confidence_score: 0.7,
      verification_status: 'VERIFIED', revision_status: 'UNKNOWN', domain,
      notes: 'Historical-only source-bound observation. The artifact has no per-observation release dates and cannot satisfy current Venezuela intake gates.'
    });
  }
}
const keys = new Set();
for (const observation of observations) {
  const key = `${observation.variable}|${observation.date}`;
  if (keys.has(key)) throw new Error(`duplicate observation: ${key}`);
  keys.add(key);
}
writeFileSync(resolve(root, 'datasets/venezuela-imf-mfs-observations.json'), JSON.stringify({ dataset_id: 'VEN-IMF-MFS-HISTORICAL', status: 'VERIFIED_SOURCE_BOUND_HISTORICAL_ONLY', observations }, null, 2));
console.log(JSON.stringify({ status: 'PASS', observations: observations.length, output: 'datasets/venezuela-imf-mfs-observations.json' }, null, 2));
