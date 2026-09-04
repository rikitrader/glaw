import type { SourceDocument } from '../sources/registry.ts';
export type ChangeStage='DETECTED'|'FETCHED'|'HASHED'|'DIFFED'|'CLASSIFIED'|'VERIFIED'|'RULE_IMPACT_ANALYZED'|'REVIEW_REQUIRED'|'PUBLISHED';
export interface LegalChange { changeId:string; sourceId:string; fromHash?:string; toHash:string; stage:ChangeStage; material:boolean; affectedRules:string[]; detectedAt:string; }
export function classifyChange(input:{before:string;after:string}):{material:boolean;reason:string} { if(input.before===input.after) return {material:false,reason:'content hash unchanged'}; return {material:true,reason:'source hash changed; semantic diff required'}; }
export function sourceStatusForPublication(source:SourceDocument):boolean{return source.status==='VERIFIED'&&source.contentHash.length===64;}
