import type { AuthorityNode } from '../../src/claims/adjudication/types.ts';
import type { AuthorityType, LegalAuthority } from '../types/index.ts';
const RANK:Record<AuthorityType,number>={STATE_CONSTITUTION:100,STATE_STATUTE:95,ADMINISTRATIVE_REGULATION:90,STATE_SUPREME_CASE:88,STATE_APPELLATE_CASE:80,FEDERAL_CIRCUIT_CASE:75,FEDERAL_DISTRICT_CASE:65,STATE_TRIAL_CASE:55,AGENCY_GUIDANCE:45,APPROVED_FORM:40,NAIC_MODEL:20,SECONDARY:10};
export function authorityRank(type:AuthorityType):number{return RANK[type];}
export function orderAuthorities(authorities:LegalAuthority[], jurisdiction:string):LegalAuthority[]{ return [...authorities].sort((a,b)=>(b.jurisdiction===jurisdiction?1:0)*authorityRank(b.authorityType)-(a.jurisdiction===jurisdiction?1:0)*authorityRank(a.authorityType)); }
export function primaryAuthorityRequired(authority:Pick<LegalAuthority,'authorityType'|'officialSourceUrl'|'verificationStatus'>):boolean { return authority.verificationStatus==='VERIFIED'&&authority.officialSourceUrl.length>0&&authority.authorityType!=='SECONDARY'&&authority.authorityType!=='NAIC_MODEL'; }
