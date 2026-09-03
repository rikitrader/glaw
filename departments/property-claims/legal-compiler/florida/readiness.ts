export type FloridaCorpusStatus='RESEARCH_REQUIRED'|'POLICY_REQUIRED'|'CASE_VERIFICATION_REQUIRED'|'PROVENANCE_REQUIRED'|'HUMAN_REVIEW_REQUIRED'|'COMPLETE_WITH_REVIEW'|'COMPLETE_VERIFIED';
export interface FloridaCorpusGates { historicalStatutesVerified:boolean; judicialOpinionsVerified:boolean; actualPolicyVerified:boolean; provenanceComplete:boolean; humanReviewComplete:boolean; criticalConflicts:number; }
export interface FloridaCorpusReadiness { status:FloridaCorpusStatus; canPromote:boolean; blockers:string[]; requiredGates:string[]; }

export function assessFloridaCorpus(gates:FloridaCorpusGates):FloridaCorpusReadiness {
  const blockers:string[]=[];
  if(!gates.historicalStatutesVerified) blockers.push('complete historical statutory snapshots are not verified');
  if(!gates.judicialOpinionsVerified) blockers.push('full Florida judicial opinions and pinpoints are not verified');
  if(!gates.actualPolicyVerified) blockers.push('actual claim policy, declarations, forms, and endorsements are not verified');
  if(!gates.provenanceComplete) blockers.push('source-to-proposition provenance is incomplete');
  if(gates.criticalConflicts>0) blockers.push('critical authority conflicts remain unresolved');
  if(blockers.some((item)=>item.includes('actual claim policy'))) return {status:'POLICY_REQUIRED',canPromote:false,blockers,requiredGates:['historicalStatutesVerified','judicialOpinionsVerified','actualPolicyVerified','provenanceComplete']};
  if(blockers.some((item)=>item.includes('judicial opinions'))) return {status:'CASE_VERIFICATION_REQUIRED',canPromote:false,blockers,requiredGates:['historicalStatutesVerified','judicialOpinionsVerified','provenanceComplete']};
  if(blockers.some((item)=>item.includes('historical statutory'))) return {status:'RESEARCH_REQUIRED',canPromote:false,blockers,requiredGates:['historicalStatutesVerified','provenanceComplete']};
  if(blockers.some((item)=>item.includes('provenance'))) return {status:'PROVENANCE_REQUIRED',canPromote:false,blockers,requiredGates:['provenanceComplete']};
  if(gates.criticalConflicts>0) return {status:'HUMAN_REVIEW_REQUIRED',canPromote:false,blockers,requiredGates:['humanReviewComplete','criticalConflicts']};
  if(!gates.humanReviewComplete) return {status:'COMPLETE_WITH_REVIEW',canPromote:false,blockers:['required human review is incomplete'],requiredGates:['humanReviewComplete']};
  return {status:'COMPLETE_VERIFIED',canPromote:true,blockers:[],requiredGates:[]};
}

export function promoteFloridaRule(gates:FloridaCorpusGates):'PRODUCTION' { const readiness=assessFloridaCorpus(gates); if(!readiness.canPromote) throw new Error(`Florida rule promotion blocked: ${readiness.status}; ${readiness.blockers.join('; ')}`); return 'PRODUCTION'; }
