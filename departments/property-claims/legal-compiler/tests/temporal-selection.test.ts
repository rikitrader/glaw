import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveApplicableAuthorityVersion } from '../temporal/engine.ts';
import type { AuthorityVersion } from '../types/index.ts';

const version=(id:string,from:string,to:string|null,systemFrom='2026-01-01'):AuthorityVersion=>({authorityId:'FL-XXXX',versionId:id,temporal:{validFrom:from,validTo:to,systemFrom,systemTo:null},operativeText:id,sourceSnapshotId:`SNAP-${id}`,contentHash:id.padEnd(64,'0').slice(0,64)});
test('claim date selects the legally effective version, not the newest version',()=>{const versions=[version('A','2023-01-01','2025-07-01'),version('B','2025-07-01','2027-07-01'),version('C','2027-07-01',null)];const result=resolveApplicableAuthorityVersion(versions,'2026-03-15','2026-08-01');assert.equal(result.version?.versionId,'B');assert.equal(result.status,'SELECTED');});
test('bitemporal query reports when the compiler learned a version after the requested system date',()=>{const result=resolveApplicableAuthorityVersion([version('B','2025-07-01','2027-07-01','2027-08-01')],'2026-03-15','2026-08-01');assert.equal(result.version?.versionId,'B');assert.equal(result.status,'KNOWN_ONLY_AFTER_DATE');assert.ok(result.warnings.length>0);});
