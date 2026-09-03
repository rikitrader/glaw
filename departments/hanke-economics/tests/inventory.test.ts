import test from 'node:test';
import assert from 'node:assert/strict';
import { auditCompletion } from '../src/completion-audit.ts';
import { POSTURES } from '../src/posture-index.ts';
import { auditCorpus } from '../src/corpus-audit.ts';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { validateRequiredSkillFields } from '../src/manifest-validator.ts';
import { inspectLocalDocument, inspectLocalHtmlDocument } from '../src/document-ingest.ts';
import { requirePdfAnchor } from '../src/pdf-anchors.ts';
import { createHash } from 'node:crypto';

test('all required skill directories contain complete manifest frontmatter', () => {
  const root = new URL('../skills/', import.meta.url).pathname;
  const dirs = readdirSync(root, { withFileTypes: true }).filter((entry) => entry.isDirectory());
  assert.ok(dirs.length >= 30);
  for (const dir of dirs) {
    const content = readFileSync(join(root, dir.name, 'SKILL.md'), 'utf8');
    const frontmatter = content.split('---')[1] ?? '';
    const manifest = Object.fromEntries(frontmatter.split('\n').filter((line) => line.includes(':')).map((line) => {
      const [key, ...rest] = line.split(':'); return [key.trim(), rest.join(':').trim()];
    }));
    assert.deepEqual(validateRequiredSkillFields(manifest), [], `${dir.name} is missing manifest fields`);
  }
});

test('all required skills expose a non-empty loader description', () => {
  const root = new URL('../skills/', import.meta.url).pathname;
  const dirs = readdirSync(root, { withFileTypes: true }).filter((entry) => entry.isDirectory());
  for (const dir of dirs) {
    const content = readFileSync(join(root, dir.name, 'SKILL.md'), 'utf8');
    const frontmatter = content.split('---')[1] ?? '';
    const manifest = Object.fromEntries(frontmatter.split('\n').filter((line) => line.includes(':')).map((line) => {
      const [key, ...rest] = line.split(':'); return [key.trim(), rest.join(':').trim()];
    }));
    assert.equal(typeof manifest.description, 'string', `${dir.name} must define description`);
    assert.ok(manifest.description.trim().length > 0, `${dir.name} description must not be empty`);
  }
});

test('completion audit exposes open evidence gaps and never claims production readiness', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const country = JSON.parse(readFileSync(new URL('../country-cases/index.json', import.meta.url), 'utf8'));
  const legal = JSON.parse(readFileSync(new URL('../legal/legal-instrument-index.json', import.meta.url), 'utf8'));
  const report = auditCompletion({ documents, episodes: country.episodes, postureAssessments: JSON.parse(readFileSync(new URL('../postures/evidence-backed-assessments.json', import.meta.url), 'utf8')).assessments, legalInstruments: legal.instruments, courtCases: legal.courtCases, benchmarkCases: [{ status: 'fixture' }], forecastAuditRecords: [], todoText: readFileSync(new URL('../HAEIS_TODO.md', import.meta.url), 'utf8') });
  assert.equal(report.posture.expected_cells, country.episodes.length * POSTURES.length);
  assert.ok(report.verified_hanke_primary_count >= 1);
  assert.ok(report.verified_metadata_only_count >= 1);
  assert.equal(report.production_ready, false);
  assert.ok(report.blockers.length > 0);
  assert.equal(report.legal.verified_court_cases, 2);
  assert.equal(report.legal.verified_instruments, 8);
  assert.ok(!report.blockers.includes('legal/institutional authority coverage is incomplete'));
});

test('completion audit counts only validated source-bound posture cells and rejects duplicates', () => {
  const assessment = {
    case_id: 'case-1',
    posture_id: 'hanke',
    shared_facts: ['A bounded fact.'],
    assumptions: ['The source is limited.'],
    mechanism: 'A documented mechanism.',
    supporting_evidence: ['DOC-RESTRICTED'],
    contradictory_evidence: [],
    falsifiers: ['A verified source contradicts the mechanism.'],
    claims: [{ text: 'Blocked claim.', label: 'HANKE-DIRECT', source_ids: ['DOC-RESTRICTED'], citation_anchors: ['p. 1'] }],
    assessment: 'SUPPORT_WITH_CONDITIONS',
    confidence: 'LOW'
  } as never;
  const report = auditCompletion({
    documents: [{ document_id: 'DOC-RESTRICTED', title: 'restricted', author: ['Steve H. Hanke'], source_url: 'https://example.test', status: 'RESTRICTED', local_path: null, citation_anchor: null, authority_level: 1 }],
    episodes: [{ id: 'case-1' }],
    postureAssessments: [assessment, assessment],
    legalInstruments: [],
    courtCases: [{ status: 'VERIFIED' }],
    benchmarkCases: [],
    forecastAuditRecords: [],
    todoText: ''
  });
  assert.equal(report.posture.assessed_cells, 0);
  assert.ok(report.posture_validation_errors.some((entry) => entry.cell === 'case-1:hanke'));
  assert.deepEqual(report.duplicate_posture_cells, ['case-1:hanke']);
  assert.ok(report.blockers.some((blocker) => blocker.includes('posture evidence validation')));
  assert.ok(report.blockers.some((blocker) => blocker.includes('duplicate posture cells')));
});

test('complete posture matrix covers all 22 episodes without promoting weak evidence', () => {
  const cases = JSON.parse(readFileSync(new URL('../country-cases/index.json', import.meta.url), 'utf8')).episodes;
  const assessments = JSON.parse(readFileSync(new URL('../postures/evidence-backed-assessments.json', import.meta.url), 'utf8')).assessments;
  const cells = new Set(assessments.map((assessment: { case_id: string; posture_id: string }) => `${assessment.case_id}:${assessment.posture_id}`));
  assert.equal(cells.size, cases.length * POSTURES.length);
  for (const caseId of ['angola-1990s', 'poland-1923-24', 'turkey-high-inflation']) {
    const caseAssessments = assessments.filter((assessment: { case_id: string }) => assessment.case_id === caseId);
    assert.equal(caseAssessments.length, POSTURES.length, `${caseId} must have all posture cells`);
    assert.ok(caseAssessments.every((assessment: { assessment: string; confidence: string }) => assessment.assessment === 'INSUFFICIENT_EVIDENCE' && assessment.confidence === 'LOW'));
  }
});

test('corpus audit exposes source coverage without overstating unresolved records', () => {
  const cases = JSON.parse(readFileSync(new URL('../country-cases/index.json', import.meta.url), 'utf8')).episodes;
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const audit = auditCorpus(cases, documents);
  assert.equal(audit.checked_cases, cases.length);
  assert.equal(audit.complete, true);
  assert.ok(!audit.restricted_source_ids.includes('DOC-HK-001'));
  assert.ok(!audit.restricted_source_ids.includes('DOC-IAE-001'));
  assert.ok(audit.verified_source_ids.includes('DOC-HANKE-KRUS-TABLE-WEB-2026'));
  assert.equal(audit.cases_with_gaps.length, 0);
});

test('Venezuela source-gap register preserves unavailable data instead of inventing values', () => {
  const register = JSON.parse(readFileSync(new URL('../datasets/venezuela-source-gap-register.json', import.meta.url), 'utf8'));
  assert.equal(register.status, 'RESEARCH_INTAKE_ONLY');
  assert.ok(register.required_series.length >= 18);
  assert.ok(register.required_series.every((series: { status: string }) => ['UNAVAILABLE', 'PROVISIONAL_SECONDARY_LEAD'].includes(series.status)));
  assert.ok(register.required_series.filter((series: { status: string }) => series.status === 'PROVISIONAL_SECONDARY_LEAD').every((series: { primary_source_required?: boolean }) => series.primary_source_required === true));
  assert.ok(register.limitation_source_ids.includes('DOC-IMF-VEN-REO-2025'));
  assert.equal(register.verified_secondary_context_sources.length, 4);
  assert.ok(register.verified_secondary_context_sources.every((source: { scope: string }) => /secondary|not a primary/i.test(source.scope)));
  assert.equal(register.acquisition_targets.length, 3);
  assert.ok(register.acquisition_targets.every((target: { status: string }) => target.status !== 'VERIFIED'));
});

test('Venezuela disputed-context intake is source-bound but cannot silently become recommendation-grade data', () => {
  const intake = JSON.parse(readFileSync(new URL('../intake/venezuela-disputed-context-2025.json', import.meta.url), 'utf8'));
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  assert.equal(intake.output_mode, 'ANALYSIS');
  assert.equal(intake.status, 'RESEARCH_INTAKE_ONLY');
  assert.ok(intake.data_intake.length >= 5);
  assert.ok(intake.data_intake.every((item: { status: string; value: unknown; source_ids: string[]; vintage: string }) => item.status === 'DISPUTED' && typeof item.value === 'number' && item.source_ids.length > 0 && item.vintage));
  for (const sourceId of intake.source_ids) {
    const source = documents.find((document: { document_id: string }) => document.document_id === sourceId);
    assert.equal(source.status, 'VERIFIED');
    assert.equal(source.primary_source, false);
  }
  assert.ok(intake.critical_unknowns.length >= 5);
  assert.ok(intake.evidence_limitations.some((limitation: string) => /secondary|recommendation/i.test(limitation)));
});

test('verified Venezuela macro-context API artifacts preserve local hashes and bounded scope', () => {
  const register = JSON.parse(readFileSync(new URL('../datasets/venezuela-source-gap-register.json', import.meta.url), 'utf8'));
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  assert.equal(register.verified_context_sources.length, 5);
  for (const context of register.verified_context_sources) {
    const document = documents.find((candidate: { document_id: string }) => candidate.document_id === context.source_id);
    assert.equal(document.status, 'VERIFIED');
    const bytes = readFileSync(new URL(`../${document.local_path}`, import.meta.url));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), document.sha256);
    assert.match(document.citation_anchor, /JSON\[0\]\.source/);
    assert.match(document.notes, /macro|proxy|not/i);
  }
});

test('verified Venezuela secondary monetary reports preserve PDF integrity and non-primary scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  for (const id of ['DOC-VEN-BANESCO-H1-2025', 'DOC-VEN-BDV-H2-2024', 'DOC-VEN-CEDICE-DEC-2024', 'DOC-VEN-UNDP-Q3-2025']) {
    const document = documents.find((candidate: { document_id: string }) => candidate.document_id === id);
    assert.equal(document.status, 'VERIFIED');
    assert.equal(document.primary_source, false);
    assert.match(document.document_type, /report/);
    assert.match(document.citation_anchor, /PDF p/);
    assert.match(document.notes, /secondary|not a BCV/);
    const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
    assert.equal(integrity.valid, true);
    assert.equal(integrity.sha256, document.sha256);
  }
});

test('current Hanke-Krus web table is verified separately from restricted Cato PDF', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const web = documents.find((document: { document_id: string }) => document.document_id === 'DOC-HANKE-KRUS-TABLE-WEB-2026');
  const cato = documents.find((document: { document_id: string }) => document.document_id === 'DOC-HK-001');
  assert.equal(web.status, 'VERIFIED');
  assert.equal(web.primary_source, true);
  assert.match(web.citation_anchor, /50%/);
  assert.match(web.notes, /supersedes|restricted/);
  const integrity = inspectLocalHtmlDocument(new URL(`../${web.local_path}`, import.meta.url).pathname, ['The Hanke-Krus World Hyperinflation Table', 'at least 50% inflation per month', '🇻🇪 Venezuela']);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, web.sha256);
  assert.equal(cato.status, 'RESTRICTED');
  assert.equal(cato.local_path, null);
});

test('bounded replacements cover restricted file leads without relabeling the original file', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  for (const [replacementId, restrictedId] of [
    ['DOC-CONGRESS-VEN-HEARING-2017', 'DOC-HANKE-VEN-TESTIMONY-2017'],
    ['DOC-IMF-011-ECOMOD-COPY-2003', 'DOC-IMF-011'],
    ['DOC-IMF-003-ARCHIVES-PDF-1991', 'DOC-IMF-003-HTML-1991'],
    ['DOC-IMF-004-FANDD-PDF-2003', 'DOC-IMF-004-HTML-2003'],
    ['BOOK-HANKE-JUNTAS-CEDICE-2015', 'BOOK-HANKE-JUNTAS-2015'],
    ['DOC-BOOK-HANKE-JAMAICA-PSOJ-1995', 'BOOK-HANKE-JAMAICA-1995']
  ]) {
    const replacement = documents.find((candidate: { document_id: string }) => candidate.document_id === replacementId);
    const restricted = documents.find((candidate: { document_id: string }) => candidate.document_id === restrictedId);
    assert.equal(replacement.status, 'VERIFIED');
    assert.ok(replacement.bounded_replacement_for.includes(restrictedId));
    assert.equal(restricted.status, 'RESTRICTED');
    assert.equal(restricted.local_path, null);
  }
  const cases = JSON.parse(readFileSync(new URL('../country-cases/index.json', import.meta.url), 'utf8')).episodes;
  const audit = auditCorpus(cases, documents);
  assert.ok(audit.verified_source_ids.includes('DOC-IMF-011-ECOMOD-COPY-2003'));
  assert.ok(!audit.restricted_source_ids.includes('DOC-IMF-011'));
  assert.ok(!audit.restricted_source_ids.includes('DOC-IMF-003-HTML-1991'));
  assert.ok(!audit.restricted_source_ids.includes('DOC-IMF-004-HTML-2003'));
});

test('official Hanke witness statement and IMF Turkey legacy report are hash-bound and page-scoped', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const witness = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-HANKE-VEN-TESTIMONY-HOUSE-WITNESS-2017');
  assert.equal(witness.status, 'VERIFIED');
  assert.equal(witness.sha256, '05fa9fb0d096b8f9a1f26dba8132f834b1cd039669b2d6e10e37fffdb254499e');
  assert.match(witness.citation_anchor, /PDF p\. 1/);
  assert.match(witness.citation_anchor, /PDF pp\. 4–7/);
  assert.equal(inspectLocalDocument(new URL(`../${witness.local_path}`, import.meta.url).pathname).sha256, witness.sha256);
  const turkey = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-IMF-012-LEGACY-PDF-2002');
  assert.equal(turkey.status, 'VERIFIED');
  assert.equal(turkey.sha256, 'b42ce86c9eedcc5ed4ae6d130778513c1191c72fbfc54a6017a281ac9e6f7e9a');
  assert.match(turkey.notes, /scanned|OCR|image/i);
  assert.equal(inspectLocalDocument(new URL(`../${turkey.local_path}`, import.meta.url).pathname).sha256, turkey.sha256);
});

test('IMF archive copy of Stopping High Inflation preserves OCR scope and physical anchors', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-IMF-003-ARCHIVES-PDF-1991');
  assert.equal(document.status, 'VERIFIED');
  assert.deepEqual(document.author, ['Carlos A. Végh']);
  assert.equal(document.sha256, 'ad776bd61a657b513f17309366b80d07e106474111b19b90cf0643160c2bf45a');
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.ok(requirePdfAnchor(extracted, 'StoDDing        High').includes(1));
  assert.ok(requirePdfAnchor(extracted, 'Bolivian  Hyperinflation').includes(19));
  assert.ok(requirePdfAnchor(extracted, 'Bolivian    Stabilization').includes(20));
  assert.match(document.notes, /OCR|historical/);
});

test('IMF Finance and Development hyperinflation PDF preserves authorship and bounded anchors', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-IMF-004-FANDD-PDF-2003');
  assert.equal(document.status, 'VERIFIED');
  assert.deepEqual(document.author, ['Carmen M. Reinhart', 'Miguel A. Savastano']);
  assert.equal(document.sha256, '347b8b5da75cd54426018d772b2cbcf60fc17ba7ccb9fe2a972a688c148f738f');
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.ok(requirePdfAnchor(extracted, 'The Realities').includes(1));
  assert.ok(requirePdfAnchor(extracted, 'hyperinflation').length > 0);
  assert.ok(requirePdfAnchor(extracted, 'convertibility').includes(2));
  assert.match(document.notes, /external-view|external-view/i);
});

test('Venezuela secondary monetary context preserves conflicting observations as disputed', () => {
  const context = JSON.parse(readFileSync(new URL('../datasets/venezuela-secondary-monetary-context.json', import.meta.url), 'utf8'));
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const verified = new Set(documents.filter((document: { status: string }) => document.status === 'VERIFIED').map((document: { document_id: string }) => document.document_id));
  assert.ok(context.observations.length >= 10);
  assert.equal(new Set(context.observations.map((observation: { observation_id: string }) => observation.observation_id)).size, context.observations.length);
  for (const observation of context.observations) {
    assert.equal(observation.status, 'DISPUTED');
    assert.ok(observation.source_ids.every((sourceId: string) => verified.has(sourceId)));
    assert.match(observation.citation_anchor, /PDF p/);
  }
  assert.match(context.promotion_rule, /cannot populate current critical intake/);
});

test('verified IMF Venezuela SDMX artifact preserves historical-only scope and exact series identity', () => {
  const register = JSON.parse(readFileSync(new URL('../datasets/venezuela-source-gap-register.json', import.meta.url), 'utf8'));
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  assert.equal(register.verified_historical_series.length, 14);
  for (const context of register.verified_historical_series) {
    const document = documents.find((candidate: { document_id: string }) => candidate.document_id === context.source_id);
    assert.equal(document.status, 'VERIFIED');
    const bytes = readFileSync(new URL(`../${document.local_path}`, import.meta.url));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), document.sha256);
    assert.ok(context.observation_count > 0);
    assert.match(context.observation_end, /^\d{4}-M\d{2}$/);
    assert.match(document.notes, /historical/);
    assert.match(document.notes, /release date/);
  }
  assert.equal(register.verified_historical_series.find((candidate: { source_id: string }) => candidate.source_id === 'DOC-IMF-MFS-CBS-VEN-CURRENCY-2026').series_id, 'S121_L_CIC_IMB_CBS');
  for (const seriesId of ['ODCORP_A_ACO_PS_ODCS', 'ODCORP_A_F21_ACO_S121_ODCS', 'ODCORP_L_F22_IBM_ODCS', 'ODCORP_L_F29_IBM_ODCS', 'ODCORP_L_F4_ODCS', 'ODCORP_NETAL_NCO_S1311MIXED_ODCS']) {
    const candidate = register.verified_historical_series.find((entry: { series_id: string }) => entry.series_id === seriesId);
    assert.equal(candidate.observation_count, 169);
    assert.equal(candidate.observation_end, '2015-M12');
  }
});

test('verified IMF Venezuela appendix remains historical and OCR-anchored', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-IMF-VEN-1999-SA');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, '4c0b58a937727c509419dbe1b94e3d1cbab1f12aac2707ddb4591f73757afc44');
  assert.match(document.citation_anchor, /pp\. 44–48/);
  assert.match(document.notes, /Historical source only/);
});

test('verified IMF comparative chapters carry local hashes and bounded anchors', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const inflation = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-IMF-002');
  const banking = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-IMF-008');
  assert.equal(inflation.status, 'VERIFIED');
  assert.equal(inflation.sha256, '0374352fc6e093da4c34f92d0b06fb454faf06cd169c107e4125a2a044ce562c');
  assert.match(inflation.citation_anchor, /pp\. 2–5/);
  assert.equal(banking.status, 'VERIFIED');
  assert.equal(banking.sha256, '4cc40091128083ea79eabb1b35a2831f03e6a8b6119633610cff9e94bb1e700e');
  assert.match(banking.citation_anchor, /pp\. 7–8/);
});

test('verified corrected IMF hyperinflation working paper preserves image/OCR scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-IMF-WP02197-CORRECTED-2002');
  assert.equal(document.status, 'VERIFIED');
  assert.deepEqual(document.author, ['Stanley Fischer', 'Ratna Sahay', 'Carlos Végh']);
  assert.equal(document.sha256, '80e7eb513a70bc92cab2dd6c40f574f0a409bff408933c431e1554ac90264926');
  assert.match(document.citation_anchor, /image-reviewed\/OCR-assisted PDF/);
  assert.match(document.notes, /no usable text layer/);
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.match(extracted, /Modern Hyper- and High Inflations/);
  assert.match(extracted, /China from October 1947 to March 1948/);
  assert.match(extracted, /fiscal deficit = seigniorage \+ borrowing/);
});

test('verified IMF Peru history excerpt preserves physical anchors and scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-IMF-PERU-HISTORY-2015');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, '6fe4bba03592bb1ba8d15b5854ccee07880f806146198ff404021b03680f7db0');
  assert.match(document.citation_anchor, /p\. 26/);
  assert.match(document.notes, /uncorrected page proofs/);
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.match(extracted, /Peru’s Recent Economic History/);
  assert.match(extracted, /THE GREAT STABILIZATION/);
  assert.match(extracted, /63 percent in July/);
});

test('verified Nicaragua strategy preserves historical and document-type scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-IMF-NIC-PRSP-2000');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'bfb4e30939b9d0ca7b71bccf2c1910efe6565bbfc6e6c3168aa243e70a099fc9');
  assert.match(document.citation_anchor, /p\. 25/);
  assert.match(document.notes, /government strategy document/);
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.match(extracted, /Government of Nicaragua/);
  assert.match(extracted, /33,000 percent in 1988/);
  assert.match(extracted, /reserve requirements restored/);
});

test('verified Russia IMF scan preserves image-page citation scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-IMF-RUS-MONETARY-INSTRUMENTS-1997');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'b490c74300eef0c8518753a1ac1f371c3d36c3d178faba9437032485def4559c');
  assert.match(document.citation_anchor, /image-reviewed PDF p\. 1/);
  assert.match(document.notes, /no usable text layer/);
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
});

test('verified Georgia IMF scan preserves image-page citation scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-IMF-GEO-HYPER-1999');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, '2348d81c42756ff31ab22e4e0886a91eca0f6d4e740cdfe251c675ae48bc7f09');
  assert.match(document.citation_anchor, /image-reviewed PDF p\. 1/);
  assert.match(document.notes, /no usable text layer/);
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
});

test('verified Yugoslavia IMF scan preserves image-page citation scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-IMF-YUG-FRY-2001');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'a196d9b9bd627dc2ff9593770c73339267819231b0d3069e424c073d22aee701');
  assert.match(document.citation_anchor, /image-reviewed PDF p\. 8/);
  assert.match(document.notes, /no usable text layer/);
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
});

test('verified Bank of Greece bulletin preserves hyperinflation anchors', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-BOG-GREECE-HYPER-2015');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, '799c1684c7e824d4cd3220001383b1be2a59ea48f8110e9061297a4e0d09b9f4');
  assert.match(document.citation_anchor, /pp\. 17–18/);
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.match(extracted, /THE GREEK HYPERINFLATION/);
  assert.match(extracted, /November 1943/);
  assert.match(extracted, /Seigniorage revenue/);
});

test('verified NBER Poland paper preserves historical scope and local integrity', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-NBER-DORNBUSCH-FISCHER-POLAND-1986');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'e68216886c85a3a64eb3436f732871ec377e76499a3df2f7eaf18877db09bc94');
  assert.match(document.citation_anchor, /pp\. 23–30/);
  assert.match(document.notes, /not Hanke attribution/);
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.match(extracted, /THE POLISH STABILIZATIONS/);
  assert.match(extracted, /A new currency, the zloty/);
});

test('verified Deutsches Historisches Museum Weimar page preserves HTML license and reform anchors', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-DHM-WEIMAR-REFORM-1923');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'f2f46da3d7ca453d9bb1a10864a873959e88362dad58c888fbb219dd0d9b6482');
  assert.match(document.citation_anchor, /15 November 1923/);
  assert.match(document.notes, /CC BY NC SA 4\.0/);
  const integrity = inspectLocalHtmlDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.match(extracted, /Die Währungsreform 1923/);
  assert.match(extracted, /15\. November 1923/);
  assert.match(extracted, /30\. August 1924/);
});

test('verified MNB forint volume preserves Hungary historical anchors and chapter scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-MNB-FORINT-70Y-2016');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'bfb5026c9930a8e6716c9bf3a04c40d13b8e7ce15838d86470b370726a5bec5f');
  assert.match(document.citation_anchor, /pp\. 19–20/);
  assert.match(document.notes, /does not establish Hanke attribution/);
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.match(extracted, /Post-war inflation and the introduction of forint/);
  assert.match(extracted, /1 August 1946/);
  assert.match(extracted, /10 July 1946/);
});

test('verified State Department China memorandum preserves contemporaneous HTML scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-STATE-DEPT-CHINA-HYPER-1945');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'c5130aa59edd83bcfe09119681b613e147815c1aa96d2da2922e3a10a75c74ab');
  assert.match(document.citation_anchor, /19 December 1945/);
  assert.match(document.notes, /contemporaneous external evidence/);
  const integrity = inspectLocalHtmlDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.match(extracted, /wartime currency hyperinflation/);
  assert.match(extracted, /CN \$900 billion/);
  assert.match(extracted, /printing press/);
});

test('verified State Department Gold Yuan document preserves reform and failure scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-STATE-DEPT-CHINA-GOLD-YUAN-1949');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'ad886633e1c8fc02e4670d81016e54d0fb20537ac1bb7267c415dfbb775d0806');
  assert.match(document.citation_anchor, /4 January 1949/);
  assert.match(document.notes, /contemporaneous external evidence/);
  const integrity = inspectLocalHtmlDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.match(extracted, /Gold Yuan/);
  assert.match(extracted, /3,000,000 to 1 GY/);
  assert.match(extracted, /budget was hopelessly unbalanced/);
});

test('verified Bulgarian National Bank annual report has local integrity and physical anchors', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-BNB-ANNUAL-1997');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, '75aec6d843dabd386d0a21f7611ad5df45d441a844c7a1a1b5eec67a467df500');
  assert.match(document.citation_anchor, /pp\. 7, 58, 67, 84/);
});

test('verified Bulgarian National Bank 1998 annual report has local integrity and monetary anchors', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-BNB-ANNUAL-1998');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, '4ef789643fdcc6636a936b1fcb5b35b965e724de55213e408df9c33f44fc5f3f');
  assert.match(document.citation_anchor, /pp\. 21–22.*p\. 46/);
});

test('verified BNB consolidated law preserves local integrity and legal scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-LAW-BGR-BNB-CONSOLIDATED-2021');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, '3eca7c34d61b1347ba89e5dcc858b56561725d54b9c49651d3d17793170a9819');
  assert.match(document.citation_anchor, /pp\. 11–13/);
  assert.match(document.notes, /Later consolidated English translation/);
  assert.match(document.notes, /not original Bulgarian State Gazette text|exact original BNB web record/);
});

test('verified Bulgarian-language BNB consolidation preserves historical legal scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-LAW-BGR-BNB-BG-CONSOLIDATED-2023');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'a958ab4a5974f05ac30ea5d8761246c6b2dcccd0ffafba3a91816d86282876b4');
  assert.match(document.citation_anchor, /Articles 28–29/);
  assert.match(document.notes, /not a scanned copy of State Gazette issue 46\/1997/);
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.ok(requirePdfAnchor(extracted, 'Чл. 28.').length > 0);
  assert.ok(requirePdfAnchor(extracted, 'Чл. 29.').length > 0);
});

test('verified Hanke/Kargı open-access volume preserves chapter authorship, license, and Venezuela anchors', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-HANKE-KARGI-MONETARY-BOARDS-2023');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'a8d2b15ca819da0c5b8a8213291dc931ace650fc7ec37b8ad3a4bf318af75b8b');
  assert.equal(document.license, 'CC BY-NC 4.0 IGO');
  assert.match(document.citation_anchor, /pp\. 14–30/);
  assert.match(document.notes, /Wu/);
  assert.ok(document.bounded_replacement_for.includes('DOC-HANKE-BUSHNELL-VEN-2017'));
  assert.ok(document.bounded_replacement_for.includes('DOC-HANKE-BUSHNELL-VEN-CATO-2017'));
  assert.ok(document.bounded_replacement_for.includes('DOC-IAE-001'));
  assert.ok(document.bounded_replacement_for.includes('DOC-WU-VEN-REFORM-2016'));
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.ok(requirePdfAnchor(extracted, 'Venezuela enters the record').length > 0);
  assert.ok(requirePdfAnchor(extracted, 'Issues in Venezuelan').length > 0);
});

test('verified Lund repository artifact is metadata-only and does not replace the restricted Russian book', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const metadata = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-LUND-RCF-METADATA-2026');
  const restrictedBook = documents.find((candidate: { document_id: string }) => candidate.document_id === 'BOOK-HANKE-RCF-TRANSLATION-2014');
  assert.equal(metadata.status, 'VERIFIED');
  assert.equal(metadata.sha256, '12251b8baa5576b69c67a21d6d780297928b566f2298086b3a91c74c8d6e78de');
  assert.equal(metadata.primary_source, false);
  assert.equal(metadata.document_type, 'repository-metadata-pdf');
  assert.ok(metadata.bounded_replacement_for.includes('BOOK-HANKE-RCF-TRANSLATION-2014'));
  assert.match(metadata.notes, /not the full book|not a chapter-text source/i);
  assert.match(metadata.notes, /must not be used for full-book quotations/i);
  assert.equal(restrictedBook.status, 'RESTRICTED');
  assert.equal(restrictedBook.local_path, null);
  const integrity = inspectLocalDocument(new URL(`../${metadata.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, metadata.sha256);
  const extracted = readFileSync(new URL(`../${metadata.text_path}`, import.meta.url).pathname, 'utf8');
  assert.ok(requirePdfAnchor(extracted, 'Russian currency and finance').length > 0);
  assert.ok(requirePdfAnchor(extracted, 'Hanke, Steve H.; Jonung, Lars; Schuler, Kurt').length > 0);
  assert.ok(requirePdfAnchor(extracted, 'Routledge').length > 0);
});

test('verified Ciela BNB law archive preserves Bulgarian legal anchors and amendment scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-LAW-BGR-BNB-1997-CIELA');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'ae4d23b0e226230ab41ec9ef22173b699e096b63073494cd9373b165e63dde36');
  assert.match(document.citation_anchor, /Article 28/);
  assert.match(document.notes, /not treated as the exact unamended State Gazette text/);
  const integrity = inspectLocalHtmlDocument(new URL(`../${document.local_path}`, import.meta.url).pathname, ['ЗАКОН ЗА БЪЛГАРСКАТА НАРОДНА БАНКА ОТ 1997 Г.']);
  assert.equal(integrity.valid, true);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.ok(requirePdfAnchor(extracted, 'Чл. 28.').length > 0);
  assert.ok(requirePdfAnchor(extracted, 'Чл. 29.').length > 0);
  assert.match(extracted, /Отразена деноминацията/);
});

test('verified BLS API artifact preserves revised-vintage scope without scoring the forecast', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-BLS-CPI-API-2026');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'd609aa60438b2c7b89d9ccd5973b208acf87f95869fc5c8ea793a5ec03ab8bc3');
  assert.match(document.notes, /not treated as the contemporaneous January 2022 release vintage/);
  const payload = JSON.parse(readFileSync(new URL(`../${document.local_path}`, import.meta.url), 'utf8'));
  assert.equal(payload.Results.series[0].seriesID, 'CUSR0000SA0');
  const december2021 = payload.Results.series[0].data.find((row: { year: string; period: string }) => row.year === '2021' && row.period === 'M12');
  assert.equal(december2021.value, '280.845');
});

test('verified Zimbabwe 2019 legal-tender regulation preserves effective-date scope', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-LAW-ZWE-SI-142-2019');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, '1db079b6b2480ce102e7b822dffa1e0106e3e4476859e5eb42430cf7ca760550');
  assert.match(document.citation_anchor, /pp\. 1–2/);
  assert.match(document.notes, /2019 legal-tender instrument/);
  assert.match(document.notes, /not the 2009 multicurrency-introduction instrument/);
});

test('verified BNB yearbook preserves institutional chronology without becoming a statute', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-BNB-YEARBOOK-1998-2002');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, '4d37d754a295f69c92b3b24ff5e15b821d1ee48d35fdd1858346554da5f65881');
  assert.match(document.citation_anchor, /p\. 144/);
  assert.match(document.notes, /not treated as the operative statute/);
});

test('verified Bulgarian currency-board discussion paper has local integrity and bounded anchors', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-BNB-CBA-1999');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'bca5399116614d63bef84af25f7e1cb5e711ac32f7f99face0e72ee4a1ae4fa6');
  assert.match(document.citation_anchor, /pp\. 7, 10/);
});

test('verified Bulgarian currency-board structure paper has local integrity and bounded anchors', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-BNB-CBA-199911');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, '3db8153ebf05777b5e8488e81eb83ee72d6f6c750bda85598175ef4453520621');
  assert.match(document.citation_anchor, /pp\. 5–6, 8–9/);
});

test('user-provided Bulgaria research PDF is verified with license, hash, and anchors', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-BGR-CHARLES-MARIE-2017');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.license, 'CC BY 4.0');
  assert.equal(document.sha256, 'ccd0398fd649d9ac9161caf4a06ea711fb8b81f2069a80840acaad49286d7eae');
  assert.match(document.citation_anchor, /pp\. 2, 6, 12, 14–15/);
});

test('local INTERNET materials have explicit intake dispositions', () => {
  const review = JSON.parse(readFileSync(new URL('../intake/local-material-review-2026-08-25.json', import.meta.url), 'utf8'));
  assert.equal(review.materials.length, 4);
  assert.equal(review.materials.filter((item: { disposition: string }) => item.disposition === 'INGESTED_VERIFIED').length, 1);
  assert.equal(review.materials.filter((item: { disposition: string }) => item.disposition === 'REVIEWED_NOT_INGESTED').length, 3);
  assert.ok(review.materials.every((item: { sha256: string; reason: string }) => /^[a-f0-9]{64}$/.test(item.sha256) && item.reason));
});

test('dork discovery preserves restricted Hanke leads without admitting search snippets as evidence', () => {
  const discovery = JSON.parse(readFileSync(new URL('../intake/dork-discovery-2026-08-25.json', import.meta.url), 'utf8')) as { leads: Array<{ disposition: string; evidence_allowed: boolean }> };
  assert.ok(discovery.leads.length >= 7);
  assert.ok(discovery.leads.filter((lead) => lead.disposition === 'RESTRICTED_HTTP_403').every((lead) => lead.evidence_allowed === false));
  assert.ok(discovery.leads.some((lead) => lead.disposition === 'VERIFIED_LOCAL_HASH_AND_ANCHORS' && lead.evidence_allowed === true));
});

test('current source registry never labels an unacquired artifact FOUND', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  for (const document of documents.filter((candidate: { status: string }) => candidate.status === 'FOUND')) {
    assert.ok(document.local_path, `${document.document_id} is FOUND without a local artifact`);
  }
});

test('Hanke major-book and monetary-flow registries preserve metadata/text boundaries', () => {
  const books = JSON.parse(readFileSync(new URL('../books/hanke/index.json', import.meta.url), 'utf8')).books;
  const requiredTitles = [
    'Making Money Work: How to Rewrite the Rules of Our Financial System',
    'Capital, Interest, and Waiting: Controversies, Puzzles, and New Additions to Capital Theory',
    'Public Debt Sustainability: International Perspectives',
    'Currency Boards for Developing Countries: A Handbook',
    'Juntas Monetarias para países en desarrollo: Dinero, inflación y estabilidad económica',
    'Russian Currency and Finance: A Currency Board Approach to Reform',
    'Currency Reform for a Market-Oriented Cuba',
    'Alternative Monetary Regimes for Jamaica',
    'Monetary Policy and Currency Boards: Latin America and Caribbean Countries Examples, Vol. 2'
  ];
  assert.deepEqual(books.map((book: { title: string }) => book.title), requiredTitles);
  assert.ok(books.every((book: { metadata_source_url: string; full_text_status: string }) => book.metadata_source_url && book.full_text_status));
  assert.ok(books.filter((book: { full_text_status: string }) => book.full_text_status === 'NOT_ACQUIRED').length >= 3);
  const currencyBoards = books.find((book: { book_id: string }) => book.book_id === 'HANKE-BOOK-CB-2015');
  assert.equal(currencyBoards.full_text_status, 'VERIFIED_OPEN_ACCESS_EDITION');
  assert.equal(currencyBoards.open_access_edition.document_id, 'DOC-BOOK-HANKE-CB-OPEN-2021');
  assert.equal(currencyBoards.open_access_edition.license, 'CC BY 4.0');
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const bookDocument = documents.find((document: { document_id: string }) => document.document_id === 'DOC-BOOK-HANKE-CB-OPEN-2021');
  assert.equal(bookDocument.status, 'VERIFIED');
  assert.equal(bookDocument.sha256, '1924a0d358d12bd8b30cb4941d699cd8cbd0593e718ad4ec2e806c8b914ee277');
  assert.match(bookDocument.citation_anchor, /pp\. 2, 6, 15, 21/);

  const papers = JSON.parse(readFileSync(new URL('../books/hanke/monetary-flow-papers.json', import.meta.url), 'utf8')).papers;
  assert.deepEqual(papers.map((paper: { paper_id: string }) => paper.paper_id), ['SAE-232', 'SAE-233', 'SAE-234']);
  assert.ok(papers.every((paper: { full_text_status: string; local_pdf: string; text_path: string }) => paper.full_text_status === 'VERIFIED_WITH_PAGE_ANCHORS' && paper.local_pdf && paper.text_path));

  const agent = readFileSync(new URL('../agents/monetary-flow-agent/agent-manifest.yaml', import.meta.url), 'utf8');
  assert.match(agent, /prohibited_actions: \[invent-data, infer-unverified-paper-formulas/);
  assert.match(agent, /required_evidence: \[verified-framework-text, monetary-sector-perimeter/);
});

test('PSOJ Jamaica book copy has OCR, hash, physical anchors, and access-scope disclosure', () => {
  const books = JSON.parse(readFileSync(new URL('../books/hanke/index.json', import.meta.url), 'utf8')).books;
  const book = books.find((candidate: { book_id: string }) => candidate.book_id === 'HANKE-BOOK-JAMAICA-1995');
  assert.equal(book.full_text_status, 'VERIFIED_PUBLIC_PUBLISHER_COPY');
  assert.equal(book.verified_document_id, 'DOC-BOOK-HANKE-JAMAICA-PSOJ-1995');
  assert.equal(book.verified_sha256, 'f53288cb1b6f927d4966d0a1c74a2eee7213aaac1a809a41bda62aad7235c124');
  assert.match(book.notes, /no explicit reuse license/);
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'DOC-BOOK-HANKE-JAMAICA-PSOJ-1995');
  assert.equal(document.status, 'VERIFIED');
  assert.equal(document.sha256, 'f53288cb1b6f927d4966d0a1c74a2eee7213aaac1a809a41bda62aad7235c124');
  assert.match(document.citation_anchor, /PDF p\. 1/);
  assert.match(document.citation_anchor, /PDF pp\. 81–85/);
  assert.match(document.notes, /reuse\/redistribution rights are not asserted/);
});

test('Cedice Spanish Hanke book copy preserves primary attribution and reuse limits', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const document = documents.find((candidate: { document_id: string }) => candidate.document_id === 'BOOK-HANKE-JUNTAS-CEDICE-2015');
  assert.equal(document.status, 'VERIFIED');
  assert.deepEqual(document.author, ['Steve H. Hanke', 'Kurt Schuler']);
  assert.equal(document.sha256, '9cac48e8b96a1c3403ff4b5ab823c33fece12825a8593cb31727c29674fb729b');
  assert.match(document.citation_anchor, /173-page PDF/);
  assert.match(document.citation_anchor, /PDF pp\. 12–15/);
  assert.match(document.notes, /no separate reuse license/);
  const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
  assert.equal(integrity.valid, true);
  assert.equal(integrity.sha256, document.sha256);
  const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url).pathname, 'utf8');
  assert.match(extracted, /Juntas Monetarias para países en desarrollo/);
  assert.match(extracted, /Steve H\. Hanke/);
  assert.match(extracted, /30 de diciembre, 2014/);
  assert.match(extracted, /Ecuador.*dolarización/s);
});
