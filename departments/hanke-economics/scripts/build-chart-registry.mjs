import { writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { CHART_SPECIFICATIONS, validateChartSpecifications } from '../src/chart-registry.ts';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const errors = validateChartSpecifications(CHART_SPECIFICATIONS);
if (errors.length) throw new Error(errors.join('; '));
writeFileSync(resolve(root, 'reports/chart-registry.json'), JSON.stringify({ registry_id: 'HAEIS-VENEZUELA-CHART-REGISTRY', version: '1.0.0', charts: CHART_SPECIFICATIONS }, null, 2));
console.log(JSON.stringify({ status: 'PASS', charts: CHART_SPECIFICATIONS.length, output: 'reports/chart-registry.json' }, null, 2));
