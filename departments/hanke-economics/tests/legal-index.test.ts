import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { legalRelianceAllowed, validateLegalInstrument, verifyLocalLegalText } from '../src/legal-verifier.ts';

test('legal index blocks unverified legal authorities from final reliance', () => {
  const index = JSON.parse(readFileSync(new URL('../legal/legal-instrument-index.json', import.meta.url), 'utf8')) as { instruments: Array<{ status: string; official_source_url: string | null; authoritative_source_url?: string | null }>; courtCases: unknown[] };
  assert.ok(index.instruments.every((instrument) => instrument.status !== 'VERIFIED' || instrument.official_source_url || instrument.authoritative_source_url));
  assert.ok(index.courtCases.length >= 1);
  assert.ok(index.courtCases.every((courtCase: { status?: string; citation_anchor?: string | null }) => courtCase.status !== 'VERIFIED' || courtCase.citation_anchor));
});

test('FOUND legal leads remain non-reliance records until local text verification', () => {
  const index = JSON.parse(readFileSync(new URL('../legal/legal-instrument-index.json', import.meta.url), 'utf8')) as { instruments: Array<Record<string, unknown>> };
  for (const instrument of index.instruments.filter((candidate) => candidate.status !== 'VERIFIED')) {
    const record = { ...instrument, citation_anchor: null } as never;
    assert.equal(legalRelianceAllowed(record), false);
    assert.deepEqual(validateLegalInstrument(record), []);
  }
});

test('verified legal reliance requires local hash and locator', () => {
  const errors = validateLegalInstrument({ instrument_id: 'L-1', jurisdiction: 'X', title: 'x', official_source_url: 'https://example.test/law', status: 'VERIFIED' });
  assert.ok(errors.includes('verified legal instrument requires local_path'));
  assert.ok(errors.includes('verified legal instrument requires sha256'));
  assert.ok(errors.includes('verified legal instrument requires citation_anchor'));
});

test('official Argentine convertibility text has verified local hash and article anchors', () => {
  const index = JSON.parse(readFileSync(new URL('../legal/legal-instrument-index.json', import.meta.url), 'utf8')) as { instruments: Array<Record<string, unknown>> };
  const record = index.instruments.find((instrument) => instrument.instrument_id === 'LAW-ARG-CONVERTIBILITY-001') as never;
  assert.equal(record.status, 'VERIFIED');
  assert.equal(legalRelianceAllowed(record), true);
  const local = verifyLocalLegalText(record);
  assert.equal(local.valid, true);
  assert.deepEqual(local.errors, []);
});

test('official Ecuador dollarization law PDF has verified local hash and anchors', () => {
  const index = JSON.parse(readFileSync(new URL('../legal/legal-instrument-index.json', import.meta.url), 'utf8')) as { instruments: Array<Record<string, unknown>> };
  const record = index.instruments.find((instrument) => instrument.instrument_id === 'LAW-ECU-DOLLARIZATION-001') as never;
  assert.equal(record.status, 'VERIFIED');
  assert.equal(legalRelianceAllowed(record), true);
  const local = verifyLocalLegalText(record);
  assert.equal(local.valid, true);
  assert.deepEqual(local.errors, []);
});

test('official Bosnia central-bank law translation has verified local hash and anchors', () => {
  const index = JSON.parse(readFileSync(new URL('../legal/legal-instrument-index.json', import.meta.url), 'utf8')) as { instruments: Array<Record<string, unknown>> };
  const record = index.instruments.find((instrument) => instrument.instrument_id === 'LAW-BIH-CURRENCY-001') as never;
  assert.equal(record.status, 'VERIFIED');
  assert.equal(legalRelianceAllowed(record), true);
  const local = verifyLocalLegalText(record);
  assert.equal(local.valid, true);
  assert.deepEqual(local.errors, []);
});

test('official Zimbabwe Reserve Bank Act text has verified local hash and anchors', () => {
  const index = JSON.parse(readFileSync(new URL('../legal/legal-instrument-index.json', import.meta.url), 'utf8')) as { instruments: Array<Record<string, unknown>> };
  const record = index.instruments.find((instrument) => instrument.instrument_id === 'LAW-ZWE-RBZ-ACT-2009') as never;
  assert.equal(record.status, 'VERIFIED');
  assert.equal(legalRelianceAllowed(record), true);
  const local = verifyLocalLegalText(record);
  assert.equal(local.valid, true);
  assert.deepEqual(local.errors, []);
});

test('official Zimbabwe 2019 legal-tender regulations have verified scope and anchors', () => {
  const index = JSON.parse(readFileSync(new URL('../legal/legal-instrument-index.json', import.meta.url), 'utf8')) as { instruments: Array<Record<string, unknown>> };
  const record = index.instruments.find((instrument) => instrument.instrument_id === 'LAW-ZWE-SI-142-2019') as never;
  assert.equal(record.status, 'VERIFIED');
  assert.equal(record.sha256, '1db079b6b2480ce102e7b822dffa1e0106e3e4476859e5eb42430cf7ca760550');
  assert.equal(legalRelianceAllowed(record), true);
  const local = verifyLocalLegalText(record);
  assert.equal(local.valid, true);
  assert.deepEqual(local.errors, []);
  assert.match(record.verification_notes, /2019 legal-tender instrument/);
  assert.match(record.verification_notes, /not the 2009 multicurrency-introduction instrument/);
});

test('authoritative Zimbabwe Finance Act copy verifies the 2009 multicurrency legal basis without being mislabeled official', () => {
  const index = JSON.parse(readFileSync(new URL('../legal/legal-instrument-index.json', import.meta.url), 'utf8')) as { instruments: Array<Record<string, unknown>> };
  const record = index.instruments.find((instrument) => instrument.instrument_id === 'LAW-ZWE-MULTICURRENCY-001') as never;
  assert.equal(record.status, 'VERIFIED');
  assert.equal(record.official_source_url, null);
  assert.equal(record.authoritative_source_url, 'https://www.veritaszim.net/sites/veritas_d/files/Finance%20%28No.%202%29%2C%202009.pdf');
  assert.equal(record.source_class, 'authoritative_reporter_copy');
  assert.equal(record.sha256, 'd51a2031c6b28a4b7f7a2adc884bf3bbd1de62d5c01765a1a1d21a1b40cd9bb8');
  assert.equal(legalRelianceAllowed(record), true);
  const local = verifyLocalLegalText(record);
  assert.equal(local.valid, true);
  assert.deepEqual(local.errors, []);
  assert.match(String(record.verification_notes), /not an official government-hosted copy/);
});

test('official BNB consolidated English translation has bounded legal reliance', () => {
  const index = JSON.parse(readFileSync(new URL('../legal/legal-instrument-index.json', import.meta.url), 'utf8')) as { instruments: Array<Record<string, unknown>> };
  const record = index.instruments.find((instrument) => instrument.instrument_id === 'LAW-BGR-BNB-CONSOLIDATED-2021') as never;
  assert.equal(record.status, 'VERIFIED');
  assert.equal(record.sha256, '3eca7c34d61b1347ba89e5dcc858b56561725d54b9c49651d3d17793170a9819');
  assert.equal(legalRelianceAllowed(record), true);
  const local = verifyLocalLegalText(record);
  assert.equal(local.valid, true);
  assert.deepEqual(local.errors, []);
  assert.match(record.verification_notes, /consolidated English translation/);
  assert.match(record.verification_notes, /original Bulgarian State Gazette/);
});

test('verified Makoni reporter copy preserves judgment scope and local integrity', () => {
  const index = JSON.parse(readFileSync(new URL('../legal/legal-instrument-index.json', import.meta.url), 'utf8')) as { courtCases: Array<Record<string, unknown>> };
  const record = index.courtCases.find((courtCase) => courtCase.case_id === 'CASE-ZWE-MAKONI-2015') as Record<string, unknown>;
  assert.equal(record.status, 'VERIFIED');
  assert.equal(record.sha256, '2bbb11337e2b2d2b2d444e2b4145c56611b0328843d54e8182435c275e2989c6');
  assert.match(String(record.verification_notes), /not an official court-hosted copy/);
  assert.match(String(record.citation_anchor), /application dismissed with costs/);
});

test('verified Mbundire reporter copy preserves 2009 transition scope', () => {
  const index = JSON.parse(readFileSync(new URL('../legal/legal-instrument-index.json', import.meta.url), 'utf8')) as { courtCases: Array<Record<string, unknown>> };
  const record = index.courtCases.find((courtCase) => courtCase.case_id === 'CASE-ZWE-MBUNDIRE-2011') as Record<string, unknown>;
  assert.equal(record.status, 'VERIFIED');
  assert.equal(record.sha256, 'aff43afa92f378e23bd2f8b0590511050597fa168c95866426ab56b148ba2fa2');
  assert.match(String(record.citation_anchor), /S\.I\. 6\/2009/);
  assert.match(String(record.verification_notes), /does not replace/);
});

test('legal retrieval audit preserves failed access without fabricating artifacts', () => {
  const lines = readFileSync(new URL('../legal/retrieval-attempts.jsonl', import.meta.url), 'utf8').trim().split('\n').map((line) => JSON.parse(line) as { result: string; local_artifact: string | null; status_after_attempt: string });
  assert.ok(lines.length >= 2);
  for (const line of lines.filter((line) => !['LEGAL-ATTEMPT-20260825-004', 'LEGAL-ATTEMPT-20260825-006'].includes(line.attempt_id))) {
    assert.notEqual(line.result, 'VERIFIED');
    assert.equal(line.local_artifact, null);
    assert.notEqual(line.status_after_attempt, 'VERIFIED');
  }
});

test('legal retrieval audit records the verified reporter copy separately', () => {
  const lines = readFileSync(new URL('../legal/retrieval-attempts.jsonl', import.meta.url), 'utf8').trim().split('\n').map((line) => JSON.parse(line) as { attempt_id: string; result: string; status_after_attempt: string; local_artifact: string | null; sha256?: string });
  const line = lines.find((candidate) => candidate.attempt_id === 'LEGAL-ATTEMPT-20260825-004');
  assert.equal(line?.result, 'HTTP 200 PDF; reporter copy verified');
  assert.equal(line?.status_after_attempt, 'VERIFIED');
  assert.equal(line?.local_artifact, 'documents/acquired/DOC-COURT-ZWE-MAKONI-2015.pdf');
  assert.equal(line?.sha256, '2bbb11337e2b2d2b2d444e2b4145c56611b0328843d54e8182435c275e2989c6');
});

test('legal retrieval audit preserves the official failure and reporter success for Mbundire', () => {
  const lines = readFileSync(new URL('../legal/retrieval-attempts.jsonl', import.meta.url), 'utf8').trim().split('\n').map((line) => JSON.parse(line) as { attempt_id: string; result: string; status_after_attempt: string; local_artifact: string | null });
  const failed = lines.find((candidate) => candidate.attempt_id === 'LEGAL-ATTEMPT-20260825-005');
  const verified = lines.find((candidate) => candidate.attempt_id === 'LEGAL-ATTEMPT-20260825-006');
  assert.equal(failed?.status_after_attempt, 'RESTRICTED');
  assert.equal(failed?.local_artifact, null);
  assert.equal(verified?.status_after_attempt, 'VERIFIED');
  assert.equal(verified?.local_artifact, 'documents/acquired/DOC-COURT-ZWE-MBUNDIRE-2011.pdf');
});
