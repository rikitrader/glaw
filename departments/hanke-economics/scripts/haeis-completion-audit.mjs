import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { auditCompletion } from '../src/completion-audit.ts';

const root = resolve(new URL('..', import.meta.url).pathname);
const json = (path) => JSON.parse(readFileSync(resolve(root, path), 'utf8'));
const cases = readFileSync(resolve(root, 'benchmarks/cases.jsonl'), 'utf8').trim().split('\n').filter(Boolean).map((line) => JSON.parse(line));
const forecastAudit = readFileSync(resolve(root, 'benchmarks/hanke-forecast-audit.jsonl'), 'utf8').trim();
const report = auditCompletion({ documents: json('rag/document-index.json').documents, episodes: json('country-cases/index.json').episodes, postureAssessments: json('postures/evidence-backed-assessments.json').assessments, legalInstruments: json('legal/legal-instrument-index.json').instruments, courtCases: json('legal/legal-instrument-index.json').courtCases, benchmarkCases: cases, forecastAuditRecords: forecastAudit ? forecastAudit.split('\n') : [], todoText: readFileSync(resolve(root, 'HAEIS_TODO.md'), 'utf8') });
console.log(JSON.stringify(report, null, 2));
process.exit(report.production_ready ? 0 : 1);
