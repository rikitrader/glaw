import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { runExecutableBenchmarks, validateBenchmarkCatalog } from '../src/benchmark-catalog.ts';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const lines = readFileSync(resolve(root, 'benchmarks/cases.jsonl'), 'utf8').split('\n').map((line) => line.trim()).filter(Boolean);
const entries = lines.map((line) => JSON.parse(line));
const documents = JSON.parse(readFileSync(resolve(root, 'rag/document-index.json'), 'utf8')).documents;
const validations = validateBenchmarkCatalog(entries, documents);
const execution = runExecutableBenchmarks(entries, documents, (observations) => {
  if (!observations.length) throw new Error('cannot forecast from an empty information set');
  return observations[observations.length - 1].value;
});
const executableDeclared = entries.filter((entry) => entry.status === 'executable').length;
const report = { declared: entries.length, executable_declared: executableDeclared, validations, executed: execution.results.length, blocked: execution.blocked, results: execution.results };
console.log(JSON.stringify(report, null, 2));
if (execution.blocked.length || executableDeclared === 0) process.exitCode = 1;
