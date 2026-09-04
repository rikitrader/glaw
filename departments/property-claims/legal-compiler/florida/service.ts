import { analyzeDCAConflict } from './conflicts.ts';
import { selectFloridaStatutoryVersion, verifyHistoricalVersion, type FloridaStatutoryVersion, type LegalTemporalContext } from './historical.ts';
import { verifyOpinionSnapshot, type FloridaCaseOpinion, type OpinionSnapshot } from './opinions.ts';
import { analyzeFloridaMatching, type PolicyMatchingContext, type MatchingFinding } from '../policy/matching.ts';
import { ingestClaimPolicy, type PolicyDocument } from '../policy/ingestion.ts';
import type { HumanLegalReviewRequest } from '../review/human.ts';

export interface FloridaMatchingAnalysisInput { context:Omit<PolicyMatchingContext,'policyHash'|'policyForm'|'policyEdition'|'coverageProvisions'|'lossSettlementProvisions'|'valuationProvisions'|'repairReplaceProvisions'|'pairSetProvisions'|'matchingRelatedEndorsements'|'roofEndorsements'|'cosmeticEndorsements'|'ordinanceLawEndorsements'>; policyDocuments:PolicyDocument[]; statutoryVersions:FloridaStatutoryVersion[]; temporalContext:LegalTemporalContext; opinions:Array<{opinion:FloridaCaseOpinion;snapshot:OpinionSnapshot}>; }
export interface FloridaMatchingAnalysis { finding:MatchingFinding; policyReady:boolean; selectedStatute:FloridaStatutoryVersion|null; verifiedCases:string[]; caseErrors:Record<string,string[]>; conflict:ReturnType<typeof analyzeDCAConflict>; reviewRequest:HumanLegalReviewRequest|null; status:'COMPLETE_VERIFIED'|'HUMAN_REVIEW_REQUIRED'|'POLICY_REQUIRED'|'RESEARCH_REQUIRED'|'CASE_VERIFICATION_REQUIRED'; }

export function analyzeFloridaMatchingClaim(input:FloridaMatchingAnalysisInput):FloridaMatchingAnalysis {
  const policy=ingestClaimPolicy(input.policyDocuments,input.context.dateOfLoss);
  const selectedStatute=selectFloridaStatutoryVersion(input.statutoryVersions,input.temporalContext);
  const statuteErrors=input.statutoryVersions.flatMap(verifyHistoricalVersion);
  const verifiedCases:string[]=[];const caseErrors:Record<string,string[]>={};
  for(const item of input.opinions){const errors=verifyOpinionSnapshot(item.snapshot,item.opinion);if(!errors.length&&item.opinion.verificationStatus==='VERIFIED')verifiedCases.push(item.opinion.caseId);else caseErrors[item.opinion.caseId]=errors.length?errors:['case verification status is not VERIFIED'];}
  const conflict=analyzeDCAConflict(input.opinions.map((item)=>item.opinion),'MATCHING');
  const finding=analyzeFloridaMatching({...input.context,policyHash:policy.policyHash,policyForm:policy.policyForm??'',policyEdition:policy.policyEdition??'',coverageProvisions:policy.provisions.filter((p)=>p.section==='DECLARATIONS'||p.section==='POLICY_FORM').map((p)=>p.text),lossSettlementProvisions:policy.provisions.filter((p)=>p.section==='POLICY_FORM').map((p)=>p.text),valuationProvisions:[],repairReplaceProvisions:[],pairSetProvisions:[],matchingRelatedEndorsements:policy.endorsements.map((p)=>p.text),roofEndorsements:[],cosmeticEndorsements:[],ordinanceLawEndorsements:[]},Boolean(selectedStatute&&!statuteErrors.length),verifiedCases.length>0);
  const reviewNeeded=!policy.ready||!selectedStatute||verifiedCases.length===0||conflict.humanReviewRequired||finding.status==='HUMAN_REVIEW_REQUIRED';
  const status=!policy.ready?'POLICY_REQUIRED':!selectedStatute||statuteErrors.length?'RESEARCH_REQUIRED':!verifiedCases.length?'CASE_VERIFICATION_REQUIRED':reviewNeeded?'HUMAN_REVIEW_REQUIRED':'COMPLETE_VERIFIED';
  const reviewRequest=reviewNeeded?{reviewId:`FL-MATCH-${input.context.claimId}`,claimId:input.context.claimId,jurisdiction:'FL' as const,issue:'MATCHING' as const,question:'Does the supplied Florida policy require adjoining-area matching for this claim?',policyText:policy.provisions.map((p)=>p.text),policyDifferences:[],candidateAuthorities:selectedStatute?[selectedStatute.authorityId]:[],candidateRules:['FL-MATCHING-626.9744-2026-CANDIDATE'],redTeam:{},blueTeam:{},whiteTeam:{},conflicts:conflict.cases,recommendedResolution:finding.status,confidence:{policy:policy.ready?80:20,caseLaw:verifiedCases.length?70:0},reviewerType:'PROPERTY_COVERAGE_COUNSEL' as const,status:'PENDING' as const,scope:'CLAIM_ONLY' as const}:null;
  return {finding,policyReady:policy.ready,selectedStatute,verifiedCases,caseErrors,conflict,reviewRequest,status};
}
