export type UnknownStatus = 'KNOWN' | 'UNKNOWN' | 'NOT_PROVIDED' | 'NOT_VERIFIED' | 'REQUIRES_SOURCE';
export type Confidence = 'HIGH' | 'MEDIUM' | 'LOW' | 'UNDETERMINED';
export type ClaimStage = 'INGESTION' | 'NORMALIZATION' | 'IDENTITY' | 'POLICY_LAW' | 'EVIDENCE_CAUSATION' | 'BUILDING_SCIENCE' | 'ESTIMATE_INVOICE' | 'RED_BLUE' | 'WHITE' | 'HUMAN_REVIEW' | 'REPORT';
export type IssueDisposition = 'SUPPORTED' | 'PARTIALLY_SUPPORTED' | 'UNSUPPORTED' | 'DUPLICATE' | 'MISSING' | 'PRICE_DISPUTE' | 'QUANTITY_DISPUTE' | 'COVERAGE_DISPUTE' | 'CAUSATION_DISPUTE' | 'LEGAL_DISPUTE' | 'DOCUMENTATION_DEFICIENT';

export interface Claim { claimId: string; carrier: string; insured: string; property: Property; lossDate: string; reportedDate: string; causeOfLoss: string; policyId: string; policyPeriod: string; jurisdiction?: string; parties: PersonOrOrganization[]; documents: DocumentRecord[]; timeline: ClaimTimelineEvent[]; status: UnknownStatus; }
export interface PersonOrOrganization { id: string; name: string; role: string; license?: string; status: UnknownStatus; }
export interface Property { propertyId: string; address: string; state: string; county?: string; propertyType?: string; rooms: Room[]; status: UnknownStatus; }
export interface Room { roomId: string; name: string; level?: string; dimensions?: string; components: BuildingComponent[]; }
export interface BuildingComponent { componentId: string; roomId: string; description: string; material?: string; classification?: string; condition?: string; }
export interface DocumentRecord { docId: string; filename: string; sha256: string; documentType: string; receivedDate?: string; creationDate?: string; author?: string; pageCount?: number; extractedText?: string; ocrConfidence?: number; relevance: string[]; sourceStatus: UnknownStatus; originalPath: string; }
export interface Policy { policyId: string; policyType: string; carrier: string; period: string; declarationsDocId: string; forms: PolicyForm[]; provisions: PolicyProvision[]; endorsements: Endorsement[]; status: UnknownStatus; }
export interface PolicyForm { formId: string; identifier: string; editionDate: string; docId: string; pageRefs: string[]; }
export interface Endorsement { endorsementId: string; identifier: string; editionDate: string; docId: string; modifies: string[]; pageRefs: string[]; }
export interface PolicyProvision { provisionId: string; kind: 'GRANT' | 'DEFINITION' | 'EXCLUSION' | 'EXCEPTION' | 'ENSUING_LOSS' | 'CONDITION' | 'LIMIT' | 'SUBLIMIT' | 'DEDUCTIBLE' | 'VALUATION' | 'APPRAISAL' | 'OTHER'; text: string; docId: string; page: string; modifiedBy?: string; }
export interface Evidence { evidenceId: string; docId?: string; type: string; proposition: string; locator?: string; sourceStatus: UnknownStatus; supports: string[]; contradicts: string[]; reliability: Confidence; }
export interface Cause { causeId: string; event: string; forceOrSource: string; mechanism: string; damageIds: string[]; alternatives: string[]; confidence: Confidence; evidenceRefs: string[]; }
export interface Damage { damageId: string; componentId: string; classification: string; causeIds: string[]; requiredOperations: string[]; confidence: Confidence; evidenceRefs: string[]; }
export interface Estimate { estimateId: string; source: string; priceList?: string; priceListDate?: string; lines: EstimateLineItem[]; totalRcv: number; totalAcv: number; }
export interface EstimateLineItem { lineId: string; estimateId: string; room: string; trade: string; category: string; selector: string; description: string; activity: string; quantity: number; unit: string; unitPrice: number; rcv: number; depreciation: number; acv: number; tax: number; op: number; location?: string; calculation?: string; evidenceRefs: string[]; policyRefs: string[]; legalRefs: string[]; dependencies: string[]; flags: string[]; confidence: Confidence; }
export interface Invoice { invoiceId: string; vendor: string; invoiceDate: string; serviceDate?: string; lines: InvoiceLine[]; total: number; balance: number; }
export interface InvoiceLine { lineId: string; description: string; quantity: number; rate: number; unit: string; total: number; equipmentId?: string; evidenceRefs: string[]; flags: string[]; }
export interface EquipmentRecord { equipmentId: string; type: string; placedAt?: string; removedAt?: string; quantity: number; room?: string; logEvidenceRefs: string[]; }
export interface MoistureReading { readingId: string; location: string; timestamp: string; value: number; unit: string; instrument?: string; evidenceRefs: string[]; }
export interface ClaimTimelineEvent { eventId: string; date: string; kind: string; description: string; evidenceRefs: string[]; }
export interface Argument { issueId: string; claimId: string; issueType: string; description: string; contractorPosition: string; carrierPosition: string; policyAuthority: string[]; legalAuthority: string[]; technicalAuthority: string[]; evidenceFor: string[]; evidenceAgainst: string[]; redTeam: TeamPosition; blueTeam: TeamPosition; whiteTeam?: WhiteFinding; financialImpact: FinancialImpact; confidence: ConfidenceProfile; missingInformation: string[]; humanReview: boolean; }
export interface TeamPosition { position: string; strongestAttack: string; survives: boolean | null; evidenceRefs: string[]; }
export interface WhiteFinding { finding: string; disposition: IssueDisposition; rationale: string; supportedEvidence: string[]; unresolvedFact?: string; additionalEvidenceNeeded: string[]; }
export interface FinancialImpact { claimedRcv?: number; supportedRcv?: number; disputedRcv?: number; depreciation?: number; acv?: number; deductible?: number; priorPayments?: number; remainingUndisputed?: number; remainingDisputed?: number; }
export interface ConfidenceProfile { fact: number; policy: number; legal: number; causation: number; scope: number; price: number; overall: Confidence; }
export interface ClaimDigitalTwin { claim: Claim; policy?: Policy; evidence: Evidence[]; causes: Cause[]; damages: Damage[]; estimates: Estimate[]; invoices: Invoice[]; equipment: EquipmentRecord[]; moisture: MoistureReading[]; arguments: Argument[]; status: UnknownStatus; }
