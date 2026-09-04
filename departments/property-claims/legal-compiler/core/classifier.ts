import { PROPERTY_CLAIMS_ISSUES, type PropertyClaimsIssue } from '../ontology/issues.ts';
export interface ClassifiedIssue { issue:PropertyClaimsIssue; matchedTerms:string[]; confidence:number; humanReview:boolean; }
const aliases:Record<string,PropertyClaimsIssue>={matching:'MATCHING',depreciation:'DEPRECIATION',appraisal:'APPRAISAL','prompt payment':'PROMPT_PAYMENT','bad faith':'BAD_FAITH','late notice':'LATE_NOTICE','proof of loss':'PROOF_OF_LOSS'};
export function classifyIssue(text:string):ClassifiedIssue[] { const normalized=text.toLowerCase(); return Object.entries(aliases).filter(([term])=>normalized.includes(term)).map(([term,issue])=>({issue,matchedTerms:[term],confidence:80,humanReview:true})); }
export function isKnownIssue(issue:string):issue is PropertyClaimsIssue{return (PROPERTY_CLAIMS_ISSUES as readonly string[]).includes(issue);}
