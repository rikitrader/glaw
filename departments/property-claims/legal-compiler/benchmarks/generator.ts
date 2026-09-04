import { SUPPORTED_JURISDICTIONS } from '../jurisdictions/registry.ts';
import type { LegalIssueCode } from '../types/index.ts';
import type { LegalBenchmarkFixture } from './fixture.ts';
const issues:LegalIssueCode[]=['MATCHING','LABOR_DEPRECIATION','APPRAISAL','PROMPT_PAYMENT','BAD_FAITH','ASSIGNMENT','ORDINANCE_LAW','CAUSATION','PROOF_OF_LOSS','ATTORNEY_FEES','CLAIMS_PRACTICES','LATE_NOTICE','LIMITATIONS'];
export function generateBenchmarkCatalog(lossDate='2026-01-01'):LegalBenchmarkFixture[] { return SUPPORTED_JURISDICTIONS.flatMap((jurisdiction)=>issues.map((issue)=>({fixtureId:`${jurisdiction.code}-${issue}-${lossDate}`,jurisdiction:jurisdiction.code,lossDate,issue,policy:{status:'SOURCE_REQUIRED'},facts:{status:'SOURCE_REQUIRED'},expectedAuthorities:[],expectedClassification:'RESEARCH_REQUIRED',prohibitedAuthorities:[],humanReviewExpected:true}))); }
