import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, extname, resolve } from 'node:path';

const root = resolve(new URL('..', import.meta.url).pathname);
const registry = JSON.parse(await readFile(resolve(root, 'intake/venezuela-bank-site-registry.json'), 'utf8'));
const runDate = '2026-08-25';
const outRoot = resolve(root, 'documents/acquired/banking/official', runDate);
await mkdir(outRoot, { recursive: true });

const absolute = (href, base) => {
  try { return new URL(href, base).toString(); } catch { return null; }
};
const safe = (value) => value.replace(/[^a-zA-Z0-9._-]+/g, '_').slice(-180);
const isPdf = (url) => /\.pdf(?:[?#].*)?$/i.test(url);
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const fetchWithTimeout = async (url, timeoutMs = 20000) => {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try { return await fetch(url, { redirect: 'follow', signal: controller.signal }); }
  finally { clearTimeout(timer); }
};

const results = [];
for (const bank of registry.banks) {
  const bankDir = resolve(outRoot, safe(bank.bank_id));
  await mkdir(bankDir, { recursive: true });
  const record = { bank_id: bank.bank_id, name: bank.name, financial_page: bank.financial_page, landing_page: null, pdfs: [], errors: [], status: 'ACQUISITION_REQUIRED' };
  try {
    const response = await fetchWithTimeout(bank.financial_page);
    const html = await response.text();
    const htmlPath = resolve(bankDir, 'financial-information.html');
    await writeFile(htmlPath, html, 'utf8');
    record.landing_page = { url: bank.financial_page, final_url: response.url, http_status: response.status, local_path: htmlPath.replace(`${root}/`, ''), retrieved_at: new Date().toISOString() };
    const hrefs = [...html.matchAll(/(?:href|data-href|data-url)=["']([^"']+)["']/gi)].map((match) => absolute(match[1], response.url)).filter(Boolean).filter(isPdf);
    const urls = [...new Set(hrefs)].sort((a, b) => {
      const priority = (url) => /2026|2025/i.test(url) ? 0 : 1;
      return priority(a) - priority(b) || a.localeCompare(b);
    }).slice(0, 12);
    for (const pdfUrl of urls) {
      try {
        const pdfResponse = await fetchWithTimeout(pdfUrl, 60000);
        const bytes = new Uint8Array(await pdfResponse.arrayBuffer());
        const magic = new TextDecoder().decode(bytes.slice(0, 5));
        const contentType = pdfResponse.headers.get('content-type') || '';
        if (!pdfResponse.ok || magic !== '%PDF-' || !/application\/pdf/i.test(contentType)) {
          record.errors.push({ url: pdfUrl, http_status: pdfResponse.status, content_type: contentType, reason: 'Response was not a valid PDF artifact; not persisted as evidence.' });
          continue;
        }
        const hash = sha256(bytes);
        const urlTag = createHash('sha1').update(pdfUrl).digest('hex').slice(0, 10);
        const fileName = safe(`${basename(new URL(pdfResponse.url).pathname) || bank.bank_id}-${urlTag}.pdf`);
        const localPath = resolve(bankDir, fileName);
        await writeFile(localPath, bytes);
        record.pdfs.push({ source_url: pdfUrl, final_url: pdfResponse.url, http_status: pdfResponse.status, content_type: contentType, bytes: bytes.byteLength, sha256: hash, local_path: localPath.replace(`${root}/`, ''), verification_status: 'DOWNLOADED_UNREVIEWED' });
      } catch (error) {
        record.errors.push({ url: pdfUrl, error: error instanceof Error ? error.message : String(error) });
      }
    }
    record.status = record.pdfs.length ? 'FOUND_UNREVIEWED' : 'LANDING_PAGE_ACQUIRED';
  } catch (error) {
    record.errors.push({ url: bank.financial_page, error: error instanceof Error ? error.message : String(error) });
  }
  results.push(record);
  console.log(JSON.stringify({ bank_id: bank.bank_id, status: record.status, pdfs: record.pdfs.length, errors: record.errors.length }));
}

const summary = { registry_id: registry.registry_id, run_date: runDate, rule: 'Downloaded artifacts remain unreviewed until document-level extraction, date/unit checks, and balance-sheet reconciliation are complete.', total_banks: results.length, landing_pages: results.filter((x) => x.landing_page).length, banks_with_pdfs: results.filter((x) => x.pdfs.length).length, total_pdfs: results.reduce((n, x) => n + x.pdfs.length, 0), results };
await writeFile(resolve(outRoot, 'acquisition-summary.json'), JSON.stringify(summary, null, 2), 'utf8');
