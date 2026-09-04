import type { Policy } from '../../domain.ts';
import type { CoverageChain, CoverageStatus } from './types.ts';
import { resolveEndorsements } from './policy.ts';

export class CoverageAuthorityEngine {
  evaluate(input:Omit<CoverageChain,'coverageStatus'> & { policy?:Policy; lossDate?:string }):CoverageChain { let status:CoverageStatus='NOT_PROVEN'; let humanReview=input.humanReview; if (input.physicalDamageProven === false) status='NOT_PROVEN'; else if (input.physicalDamageProven === null || input.evidence.length === 0) { status='NOT_PROVEN'; humanReview=true; } else if (!input.policy) { status='REQUIRES_LEGAL_REVIEW'; humanReview=true; } else { const effective=resolveEndorsements(input.policy,input.lossDate ?? 'UNKNOWN'); if (effective.status !== 'RESOLVED') { status=effective.status === 'CONFLICT' ? 'POLICY_AMBIGUOUS' : 'REQUIRES_LEGAL_REVIEW'; humanReview=true; } else if (input.exclusions.length && !input.exceptions.length) status='EXCLUDED'; else if (input.operationId.toLowerCase().includes('access')) status='COVERED_ACCESS_OPERATION'; else status='COVERED_BUT_SCOPE_DISPUTED'; } return {...input,coverageStatus:status,humanReview}; }
}
