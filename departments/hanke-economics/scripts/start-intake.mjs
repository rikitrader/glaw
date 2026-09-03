import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { createIntakeRunReport } from '../src/intake-runner.ts';

const root = resolve(new URL('..', import.meta.url).pathname);
const inputPath = process.argv[2];
if (!inputPath) {
  console.error('Usage: node scripts/start-intake.mjs intake/<file>.json');
  process.exit(2);
}
const intake = JSON.parse(readFileSync(resolve(process.cwd(), inputPath), 'utf8'));
const documents = JSON.parse(readFileSync(resolve(root, 'rag/document-index.json'), 'utf8')).documents;
const report = createIntakeRunReport(intake, documents);
console.log(JSON.stringify(report, null, 2));
process.exit(report.validation_errors.length || report.readiness.readiness === 'BLOCKED' ? 1 : 0);
