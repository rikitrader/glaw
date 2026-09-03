import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateIndexedFinalReport } from '../src/final-report.ts';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const index = JSON.parse(readFileSync(resolve(root, 'reports/final-report-index.json'), 'utf8'));
const report = JSON.parse(readFileSync(resolve(root, process.argv[2] ?? 'reports/venezuela-final-indexed-report.json'), 'utf8'));
const errors = validateIndexedFinalReport(report, index);
console.log(JSON.stringify({ status: errors.length ? 'BLOCKED' : 'PASS', errors, section_count: report.sections.length, chart_count: report.charts.length, formula_count: report.formulas.length }, null, 2));
if (errors.length) process.exitCode = 1;
