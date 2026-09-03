import type { ClaimDigitalTwin, ClaimStage, DocumentRecord } from './domain.ts';

export interface ClaimApiRequest { claimId:string; matterId?:string; organizationId:string; idempotencyKey:string; }
export interface IngestClaimRequest extends ClaimApiRequest { documents:Array<Omit<DocumentRecord,'sourceStatus'> & {sourceStatus?:DocumentRecord['sourceStatus']}>; }
export interface IngestClaimResponse { claimId:string; acceptedDocumentIds:string[]; rejectedDocuments:Array<{filename:string; reason:string}>; nextStage:ClaimStage; }
export interface ClaimSnapshotResponse { claimId:string; stage:ClaimStage; twin:ClaimDigitalTwin; gates:{policyFirst:boolean; citationVerified:boolean; humanReviewRequired:boolean}; }
export const PROPERTY_CLAIMS_API = {
  ingest: 'POST /api/property-claims/:claimId/documents',
  snapshot: 'GET /api/property-claims/:claimId',
  advance: 'POST /api/property-claims/:claimId/stage',
  adjudicate: 'POST /api/property-claims/:claimId/issues/:issueId/adjudicate',
  appellate: 'POST /api/property-claims/:claimId/appellate-review'
} as const;
