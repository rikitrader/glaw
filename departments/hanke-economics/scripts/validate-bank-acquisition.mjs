import { readFile, stat } from 'node:fs/promises';
import { resolve } from 'node:path';

const root = resolve(new URL('..', import.meta.url).pathname);
const registry = JSON.parse(await readFile(resolve(root, 'intake/venezuela-bank-site-registry.json'), 'utf8'));
const summaryPath = resolve(root, 'documents/acquired/banking/official/2026-08-25/acquisition-summary.json');
const summary = JSON.parse(await readFile(summaryPath, 'utf8'));
const failures = [];
const bankIds = new Set(registry.banks.map((bank) => bank.bank_id));

if (summary.total_banks !== registry.banks.length) failures.push(`bank count mismatch: registry=${registry.banks.length}, summary=${summary.total_banks}`);
for (const result of summary.results) {
  if (!bankIds.has(result.bank_id)) failures.push(`unknown bank in summary: ${result.bank_id}`);
  for (const pdf of result.pdfs) {
    try {
      const artifact = await stat(resolve(root, pdf.local_path));
      if (artifact.size !== pdf.bytes) failures.push(`${result.bank_id}: byte mismatch for ${pdf.local_path}`);
    } catch { failures.push(`${result.bank_id}: missing artifact ${pdf.local_path}`); }
    if (pdf.verification_status !== 'DOWNLOADED_UNREVIEWED') failures.push(`${result.bank_id}: unsafe status ${pdf.verification_status}`);
  }
}

const report = {
  status: failures.length ? 'FAIL' : 'PASS',
  registry_banks: registry.banks.length,
  landing_pages_acquired: summary.landing_pages,
  banks_with_downloads: summary.banks_with_pdfs,
  candidate_pdf_records: summary.total_pdfs,
  rule: 'This validator verifies acquisition integrity only. It does not verify statement content, accounting date, units, or balance-sheet reconciliation.',
  failures
};
console.log(JSON.stringify(report, null, 2));
process.exit(failures.length ? 1 : 0);
