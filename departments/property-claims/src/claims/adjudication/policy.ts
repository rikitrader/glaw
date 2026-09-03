import type { Endorsement, Policy, PolicyProvision } from '../../domain.ts';
import type { CompiledProvision, EffectivePolicyVersion } from './types.ts';

export function compileProvision(input: PolicyProvision & { form?:string; edition?:string; section?:string; exceptions?:string[]; supersedes?:string[] }): CompiledProvision {
  if (!input.text.trim()) throw new Error(`${input.provisionId}: original policy text is required`);
  return { provisionId:input.provisionId, form:input.form ?? 'UNKNOWN', edition:input.edition ?? 'UNKNOWN', page:input.page, section:input.section ?? input.kind, originalText:input.text, normalizedRule:{kind:input.kind, sourceDocument:input.docId, page:input.page}, exceptions:input.exceptions ?? [], modifiedBy:input.modifiedBy ? [input.modifiedBy] : [], supersedes:input.supersedes ?? [], jurisdictionInterpretations:[], ambiguityFlags:[], citations:[] };
}
export function compilePolicy(policy: Policy): CompiledProvision[] { return policy.provisions.map((provision) => compileProvision(provision)); }
export function resolveEndorsements(policy: Policy, lossDate: string): EffectivePolicyVersion {
  const conflicts:string[] = []; const active = policy.endorsements.filter((endorsement:Endorsement) => endorsement.editionDate === 'UNKNOWN' || endorsement.editionDate <= lossDate);
  const touched = new Map<string,string>(); for (const endorsement of active) for (const provisionId of endorsement.modifies) { const prior=touched.get(provisionId); if (prior) conflicts.push(`${provisionId} modified by both ${prior} and ${endorsement.endorsementId}`); touched.set(provisionId, endorsement.endorsementId); }
  return { policyId:policy.policyId, asOfLossDate:lossDate, provisionIds:policy.provisions.map((p) => p.provisionId), appliedEndorsements:active.map((e) => e.endorsementId), conflicts, status:policy.provisions.length === 0 ? 'INCOMPLETE' : conflicts.length ? 'CONFLICT' : active.some((e) => e.modifies.length === 0) ? 'INCOMPLETE' : 'RESOLVED' };
}
