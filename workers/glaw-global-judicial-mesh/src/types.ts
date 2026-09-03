export interface Env {
  DB: D1Database;
  DOCUMENTS: R2Bucket;
  CACHE: KVNamespace;
  INGESTION_QUEUE: Queue<IngestionMessage>;
  LEGAL_VECTORS: VectorizeIndex;
  ROUTER_COORDINATOR: DurableObjectNamespace;
  COURTLISTENER_TOKEN?: string;
  COURTLISTENER_BASE_URL: string;
  GLAW_API_KEY?: string;
  GLAW_ADMIN_API_KEY?: string;
  GLAW_TENANT_ID?: string;
  GLAW_ALLOWED_ORIGINS?: string;
  GLAW_RATE_LIMIT_PER_MINUTE?: string;
  ENVIRONMENT?: 'local' | 'staging' | 'production' | string;
  MOCK_PROVIDER_MODE?: string;
  JUDGE_PROFILE_COORDINATOR?: DurableObjectNamespace;
  MATTER_COORDINATOR?: DurableObjectNamespace;
}

export type JudgeSourceClass = 'official-procedure' | 'published-order' | 'published-opinion' | 'docket' | 'secondary' | 'user-record';
export type JudgeProfileDimension = 'procedure' | 'discovery' | 'evidence' | 'case-management' | 'sanctions' | 'hearing' | 'appellate-safety';
export interface JudgeObservation { id: string; tenantId?: string; judgeId: string; matterId?: string; sourceId?: string; dimension: JudgeProfileDimension; proposition: string; value: string; sourceClass: JudgeSourceClass; sourceUrl?: string; sourceHash?: string; observedAt: string; recordedAt?: string; confidence: number; status: 'VERIFIED' | 'UNVERIFIED' | 'DISPUTED'; verificationNote?: string; }
export interface JudgePrediction { judgeId: string; matterId?: string; issue: string; status: 'PREDICTION_AVAILABLE' | 'RECORD_TOO_INCOMPLETE'; outcomes: Array<{ outcome: string; score: number }>; rationale: string[]; sourceObservationIds: string[]; uncertainty: { level: 'LOW' | 'MEDIUM' | 'HIGH'; reasons: string[] }; limitation: 'MODEL-BASED — NOT A GUARANTEE'; model: 'evidence-weighted-heuristic-v1'; humanReview: 'REQUIRED' | 'APPROVED' | 'REJECTED'; createdAt: string; }
export interface JudgeSource { id: string; tenantId: string; judgeId: string; matterId?: string; sourceClass: JudgeSourceClass; sourceUrl?: string; sourceHash?: string; r2Key?: string; title?: string; effectiveDate?: string; retrievedAt: string; verificationStatus: 'UNVERIFIED' | 'VERIFIED' | 'REJECTED'; }
export interface JudgeProfileIdentity { tenantId: string; judgeId: string; judgeName: string; court: string; county?: string; judicialCircuit?: string; division?: string; assignment?: string; profileAsOf: string; lastVerified: string; status: 'CURRENT' | 'STALE' | 'NEEDS_VERIFICATION'; }
export interface AdversarialReview { id: string; tenantId: string; matterId?: string; judgeId: string; issue: string; status: 'DRAFT' | 'HUMAN_REVIEW_REQUIRED' | 'APPROVED' | 'REJECTED'; red: string[]; blue: string[]; purple: Array<{ position: string; classification: 'STRONG' | 'DEFENSIBLE' | 'WEAK' }>; createdAt: string; }
export interface JudgeCaseObservation { id: string; tenantId: string; judgeId: string; matterId?: string; caseId: string; court: string; division?: string; caseType?: string; proceduralPosture: string; issueClass: string; motionType?: string; requestedRelief?: string; ruling: string; reasons?: string; comparabilityScore: number; sourceId?: string; status: 'UNVERIFIED' | 'VERIFIED' | 'DISPUTED'; createdAt: string; }
export type DiscoveryObjectKind = 'INTERROGATORY' | 'REQUEST_FOR_PRODUCTION' | 'REQUEST_FOR_ADMISSION' | 'DEPOSITION' | 'MOTION_TO_COMPEL' | 'RESPONSE' | 'ORDER' | 'OTHER';
export interface Matter { tenantId: string; matterId: string; caseNumber?: string; court?: string; county?: string; circuit?: string; division?: string; judgeId?: string; status: 'ACTIVE' | 'CLOSED' | 'ARCHIVED'; createdAt: string; updatedAt: string; }
export interface DiscoveryObject { id: string; tenantId: string; matterId: string; kind: DiscoveryObjectKind; requestNumber?: string; exactText?: string; responseText?: string; objectionText?: string; servedAt?: string; responseDue?: string; respondedAt?: string; productionStatus: 'UNKNOWN' | 'NOT_PRODUCED' | 'PARTIAL' | 'PRODUCED' | 'NO_RESPONSIVE_DOCUMENTS' | 'PRIVILEGE_REVIEW'; sourceId?: string; status: 'UNVERIFIED' | 'VERIFIED' | 'DISPUTED'; createdAt: string; }
export interface DiscoveryDeadline { status: 'CANDIDATE' | 'DATE_VERIFICATION_REQUIRED' | 'NOT_APPLICABLE'; rule: string; serviceDate?: string; responseDue?: string; candidateDueDate?: string; explanation: string; warnings: string[]; }
export interface DiscoveryAuditFinding { requirement: string; authority: string; status: 'SATISFIED' | 'DEFECT' | 'RECORD_REQUIRED' | 'UNKNOWN'; evidenceIds: string[]; notes: string; requestedRemedy?: string; }
export interface DiscoveryRequestFinding { discoveryId: string; requestNumber?: string; governingRule: string; deadline: DiscoveryDeadline; result: 'CONCEDE' | 'SUPPLEMENT' | 'NARROW' | 'OBJECT' | 'PROTECTIVE_ORDER' | 'IN_CAMERA_REVIEW' | 'NO_RESPONSIVE_DOCUMENTS' | 'NOT_IN_POSSESSION_CUSTODY_CONTROL' | 'RECORD_REQUIRED'; findings: string[]; missingRecord: string[]; }
export interface DiscoveryAudit { tenantId: string; matterId: string; posture: 'PRE_JUDGMENT' | 'POST_JUDGMENT' | 'UNKNOWN'; status: 'READY_FOR_HUMAN_REVIEW' | 'REQUIRES_RECORD' | 'REQUIRES_AUTHORITY'; findings: DiscoveryAuditFinding[]; requestFindings: DiscoveryRequestFinding[]; warnings: string[]; humanReview: 'REQUIRED'; createdAt: string; }
export type JudgeEngineMode = 'TEXTUAL' | 'PROCEDURAL' | 'PROPORTIONALITY' | 'CASE_MANAGEMENT' | 'EVIDENCE' | 'APPELLATE_SAFE';
export interface JudgeEngineReport { judgeId: string; matterId?: string; issue: string; analyticalPosture: string; modes: Array<{ mode: JudgeEngineMode; likelyPath: 'LIKELY_GRANT' | 'LIKELY_PARTIAL_GRANT' | 'LIKELY_DENIAL' | 'RECORD_TOO_INCOMPLETE'; confidenceRange: [number, number]; basis: string[] }>; simulation: { iterations: 1000; outcomeIntervals: Array<{ outcome: string; mean: number; interval: [number, number] }>; disclaimer: 'MODEL-BASED — NOT EMPIRICAL JUDICIAL PROBABILITY'; }; strategies: Array<{ name: 'AGGRESSIVE' | 'BALANCED' | 'RISK_MINIMIZATION'; action: string; risk: 'HIGH' | 'MEDIUM' | 'LOW'; requiresHumanChoice: true }>; warnings: string[]; limitation: 'MODEL-BASED — NOT A GUARANTEE'; humanReview: 'REQUIRED'; createdAt: string; }
export interface ProceduralEvent { id: string; tenantId: string; matterId: string; eventType: string; eventDate: string; sourceId?: string; status: 'UNVERIFIED' | 'VERIFIED' | 'DISPUTED'; payload: Record<string, unknown>; createdAt: string; }
export type FilingGate = 'FACT_CHECK' | 'AUTHORITY_CHECK' | 'RED_TEAM' | 'BLUE_TEAM' | 'PROCEDURAL_CHECK' | 'EXHIBIT_CHECK' | 'RELIEF_CHECK' | 'HUMAN_REVIEW_REQUIRED';
export interface FilingArtifact { id: string; tenantId: string; matterId: string; kind: string; status: 'DRAFT' | FilingGate | 'READY_TO_FILE' | 'BLOCKED'; r2Key?: string; blockedReasons: string[]; gateEvidence: Partial<Record<FilingGate, string[]>>; createdAt: string; updatedAt: string; }
export interface AuthorityRecord { id: string; tenantId: string; judgeId: string; matterId?: string; name: string; citation: string; authorityType: 'RULE' | 'STATUTE' | 'CASE' | 'ADMINISTRATIVE_ORDER' | 'JUDGE_PROCEDURE' | 'SECONDARY'; court?: string; year?: number; proposition?: string; sourceId?: string; status: 'UNVERIFIED' | 'VERIFIED' | 'NEGATIVE' | 'CONFLICTING' | 'SUPERSEDED'; createdAt: string; verifiedAt?: string; }
export interface AuthorityEdge { id: string; tenantId: string; fromAuthorityId: string; toAuthorityId: string; relationship: 'SUPERSEDES' | 'LIMITS' | 'DISTINGUISHES' | 'NEGATIVE_TREATMENT' | 'CONFLICTS_WITH'; evidenceNote: string; sourceId?: string; status: 'UNVERIFIED' | 'VERIFIED' | 'DISPUTED'; createdAt: string; }

export type SearchMode = 'QUICK' | 'STANDARD' | 'DEEP' | 'LITIGATION' | 'APPELLATE' | 'GLOBAL' | 'CITATION_VERIFY' | 'ADVERSE_AUTHORITY' | 'DOCKET' | 'STATUTORY' | 'REGULATORY';
export type ProviderStatus = 'healthy' | 'degraded' | 'unavailable' | 'unknown';
export type ProviderLifecycle = 'DISCOVERED' | 'SECURITY_REVIEW' | 'TERMS_REVIEW' | 'SCHEMA_TEST' | 'DATA_QUALITY_TEST' | 'AUTHORITY_TEST' | 'APPROVED' | 'ACTIVE';

export interface ProviderCapabilities { search: boolean; caseLookup: boolean; docketLookup: boolean; citationLookup: boolean; documentDownload: boolean; bulkAccess: boolean; apiAvailable: boolean; scrapingPermitted: boolean; authRequired: boolean; paidAccess: boolean; robotsRestricted: boolean; }
export interface CourtJurisdictionCoverage { id: string; name: string; country: string; courtLevel?: string; sourceScope: 'official' | 'repository' | 'aggregator' | 'discovery'; }
export interface SearchContext { requestId: string; tenantId?: string; matterId?: string; signal?: AbortSignal; }
export interface LegalSearchQuery { text: string; jurisdiction?: string[]; country?: string[]; court?: string[]; courtLevel?: string[]; caseName?: string; docketNumber?: string; neutralCitation?: string; reporterCitation?: string; judge?: string[]; party?: string[]; statute?: string[]; regulation?: string[]; proceduralPosture?: string[]; legalIssue?: string[]; dateFrom?: string; dateTo?: string; bindingOnly?: boolean; publishedOnly?: boolean; includeDockets?: boolean; includeOpinions?: boolean; includeFilings?: boolean; semanticSearch?: boolean; citationSearch?: boolean; limit?: number; }
export interface ProviderSearchResult { provider: string; raw: RawProviderRecord; provenance: Provenance; }
export interface RawProviderRecord { id?: string; caseName?: string; court?: string; date?: string; docketNumber?: string; citation?: string; sourceUrl: string; snippet?: string; fullText?: string; metadata?: Record<string, unknown>; }
export interface CaseIdentifier { id?: string; docketNumber?: string; citation?: string; caseName?: string; }
export interface DocketIdentifier { id: string; }
export interface RawLegalDocument { record: RawProviderRecord; content?: string; provenance: Provenance; }
export interface RawDocket { id: string; provider: string; entries: Array<Record<string, unknown>>; provenance: Provenance; }
export interface CitationReference { citation: string; type: 'case' | 'statute' | 'regulation' | 'neutral' | 'international' | 'unknown'; verified: boolean; sourceUrl?: string; }
export interface SubsequentHistory { treatment: string; citingCaseId?: string; citation?: string; confidence: number; evidence: Provenance[]; }
export interface LegalDocument { id: string; kind: 'opinion' | 'filing' | 'order' | 'docket'; sourceUrl: string; contentHash?: string; r2Key?: string; }
export interface Provenance { provider: string; originalUrl: string; retrievedAt: string; contentHash?: string; documentId?: string; page?: number; paragraph?: number; }
export interface GLAWCase { id: string; source: { provider: string; sourceUrl: string; official: boolean; retrievedAt: string }; jurisdiction: { country: string; subdivision?: string; legalSystem?: string }; court: { id?: string; name: string; abbreviation?: string; level?: string }; identifiers: { docketNumber?: string; neutralCitation?: string; reporterCitations?: string[] }; parties: { plaintiffs?: string[]; defendants?: string[] }; judges?: string[]; dates: { decided?: string }; proceduralPosture?: string[]; issues?: string[]; holdings?: string[]; reasoning?: string[]; disposition?: string; casesCited?: CitationReference[]; subsequentHistory?: SubsequentHistory[]; authority: { binding?: boolean; persuasive?: boolean; authorityScore?: number; confidence?: number }; documents?: LegalDocument[]; rawProviderData?: unknown; }
export interface ProviderHealth { provider: string; status: ProviderStatus; latencyMs: number; lastSuccess?: string; errorRate: number; rateLimitRemaining?: number; }
export interface ProviderReview { lifecycle: ProviderLifecycle; termsReviewed: boolean; schemaValidated: boolean; authorityValidated: boolean; securityReviewed: boolean; approvedBy?: string; approvedAt?: string; notes?: string[]; }
export type ProviderReviewGate = 'termsReviewed' | 'schemaValidated' | 'authorityValidated' | 'securityReviewed';
export interface ProviderReviewRecord extends ProviderReview { providerId: string; updatedAt?: string; }
export interface CitationVerification { status: 'VERIFIED' | 'UNVERIFIED' | 'NOT_FOUND'; citation: string; caseId?: string; sourceUrl?: string; confidence: number; warnings: string[]; }
export interface IngestionMessage { kind: 'provider-result' | 'document'; provider: string; record: RawProviderRecord; requestId: string; tenantId?: string; }
export interface SourceAuthorityScore { officialSource: number; jurisdictionMatch: number; courtLevel: number; completeness: number; recency: number; citationReliability: number; documentIntegrity: number; subsequentHistoryConfidence: number; overall: number; }

export interface LegalSourceAdapter { id: string; jurisdiction: string[]; coverage: CourtJurisdictionCoverage[]; endpoint: string; capabilities: ProviderCapabilities; review: ProviderReview; searchCases(query: LegalSearchQuery, context: SearchContext): Promise<ProviderSearchResult[]>; getCase?(identifier: CaseIdentifier, context: SearchContext): Promise<RawLegalDocument | null>; getDocket?(identifier: DocketIdentifier, context: SearchContext): Promise<RawDocket | null>; healthCheck(): Promise<ProviderHealth>; normalize(input: RawProviderRecord): Promise<GLAWCase>; }
