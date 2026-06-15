/**
 * Federal Pleading Engine - Type Definitions
 *
 * Defines all input/output schemas for the federal pleading engine.
 * These types ensure type-safe processing of case data through
 * element analysis, mapping, drafting, and risk scoring.
 */

// ============================================================================
// INPUT TYPES
// ============================================================================

/**
 * Court information for jurisdiction and venue analysis
 */
export interface CourtInfo {
  district: string;
  division: string;
  state: string;
}

/**
 * Party entity types
 */
export type EntityType =
  | 'individual'
  | 'corporation'
  | 'llc'
  | 'partnership'
  | 'municipality'
  | 'state_agency'
  | 'federal_agency'
  | 'unincorporated_association';

/**
 * Defendant types for immunity analysis
 */
export type DefendantType =
  | 'federal'
  | 'state'
  | 'local'
  | 'private'
  | 'officer';

/**
 * Capacity in which defendant is sued
 */
export type DefendantCapacity =
  | 'individual'
  | 'official'
  | 'both';

/**
 * Plaintiff party information
 */
export interface Plaintiff {
  name: string;
  citizenship: string;
  entity_type: EntityType;
  state_of_incorp?: string;
  ppb?: string;  // Principal place of business
  residence?: string;
}

/**
 * Defendant party information
 */
export interface Defendant {
  name: string;
  type: DefendantType;
  capacity: DefendantCapacity;
  citizenship: string;
  entity_type: EntityType;
  state_of_incorp?: string;
  ppb?: string;
  role_title?: string;
}

/**
 * Parties section of case input
 */
export interface Parties {
  plaintiffs: Plaintiff[];
  defendants: Defendant[];
}

/**
 * Individual fact entry with all relevant details
 */
export interface FactEntry {
  date: string;
  location: string;
  actors: string[];
  event: string;
  documents: string[];
  harm: string;
  damages_estimate: string;
  evidence: string[];
  witnesses: string[];
}

/**
 * Administrative exhaustion status
 */
export interface ExhaustionStatus {
  ftca_admin_claim_filed: boolean | 'unknown';
  eeoc_charge_filed: boolean | 'unknown';
  erisa_appeal_done: boolean | 'unknown';
  agency_final_action: boolean | 'unknown';
  plra_exhaustion_done: boolean | 'unknown';
  administrative_exhaustion_done: boolean | 'unknown';
  irs_claim_filed: boolean | 'unknown';
}

/**
 * Key dates for limitations analysis
 */
export interface KeyDates {
  injury_date: string;
  notice_date: string;
  denial_date: string;
}

/**
 * Limitations and timing information
 */
export interface LimitationsInfo {
  key_dates: KeyDates;
}

/**
 * Case goals for strategy analysis
 */
export interface CaseGoals {
  settlement_target: string;
  non_monetary_goals: string[];
}

/**
 * Types of relief that can be requested
 */
export type ReliefType =
  | 'money'
  | 'injunction'
  | 'declaratory'
  | 'fees'
  | 'costs'
  | 'other';

/**
 * Complete case input structure
 */
export interface CaseInput {
  court: CourtInfo;
  parties: Parties;
  facts: FactEntry[];
  claims_requested: string[];
  relief_requested: ReliefType[];
  exhaustion: ExhaustionStatus;
  limitations: LimitationsInfo;
  goals: CaseGoals;
}

// ============================================================================
// CLAIM LIBRARY TYPES
// ============================================================================

/**
 * Source type for the claim
 */
export type SourceType =
  | 'constitutional'
  | 'statute'
  | 'common_law'
  | 'regulatory';

/**
 * Types of exhaustion requirements
 */
export type ExhaustionType =
  | 'eeoc'
  | 'ftca_sf95'
  | 'erisa_internal'
  | 'apa_final_action'
  | 'state_tort_claim'
  | null;

/**
 * Immunity types that may apply
 */
export type ImmunityType =
  | 'qualified'
  | 'absolute_judicial'
  | 'absolute_prosecutorial'
  | 'absolute_legislative'
  | 'sovereign'
  | 'eleventh_amendment'
  | 'discretionary_function';

/**
 * Jurisdictional basis for the claim
 */
export type JurisdictionBasis =
  | 'federal_question'
  | 'diversity'
  | 'supplemental';

/**
 * Claim category groupings
 */
export type ClaimCategory =
  | 'constitutional_civil_rights'
  | 'bivens'
  | 'administrative'
  | 'employment'
  | 'tort_government'
  | 'financial_consumer'
  | 'commercial'
  | 'erisa'
  | 'tax';

/**
 * Metadata for a single claim type
 */
export interface ClaimMetadata {
  name: string;
  category: ClaimCategory;
  source: string;
  sourceType: SourceType;
  heightenedPleading: boolean;
  exhaustionRequired: boolean;
  exhaustionType: ExhaustionType;
  immunities: ImmunityType[];
  typicalDefenses: string[];
  jurisdiction: JurisdictionBasis;
  statuteOfLimitations: string;
  viabilityWarning?: string;  // For claims with modern limits (e.g., Bivens)
}

// ============================================================================
// ELEMENTS TYPES
// ============================================================================

/**
 * Single element of a cause of action
 */
export interface ClaimElement {
  number: number;
  name: string;
  mustAllege: string;
  typicalEvidence: string[];
  pitfalls: string;
}

/**
 * Precondition for filing the claim
 */
export interface ClaimPrecondition {
  type: 'exhaustion' | 'standing' | 'timing' | 'procedural';
  requirement: string;
  satisfied?: boolean | 'unknown';
  notes?: string;
}

// ============================================================================
// MAPPING TYPES
// ============================================================================

/**
 * Result of mapping a fact to an element
 */
export interface FactElementMapping {
  elementNumber: number;
  elementName: string;
  factIndices: number[];
  coverage: 'full' | 'partial' | 'none';
  supportingFacts: string[];
  gaps: string[];
}

/**
 * Overall mapping result for a claim
 */
export interface ClaimMappingResult {
  claimKey: string;
  claimName: string;
  elements: FactElementMapping[];
  overallCoverage: number;  // 0-100%
  factGaps: FactGap[];
  preconditions: ClaimPrecondition[];
}

/**
 * Identified gap in fact coverage
 */
export interface FactGap {
  elementNumber: number;
  elementName: string;
  missingInfo: string;
  priority: 'critical' | 'important' | 'helpful';
  suggestedSources: string[];
}

// ============================================================================
// DRAFTING TYPES
// ============================================================================

/**
 * Row in the elements table output
 */
export interface ElementsTableRow {
  number: number;
  element: string;
  mustAllege: string;
  typicalEvidence: string;
  pitfalls: string;
}

/**
 * Pleading checklist entry
 */
export interface PleadingChecklistEntry {
  elementNumber: number;
  elementName: string;
  facts: string[];
  status: 'satisfied' | 'partial' | 'missing';
  notes: string;
}

/**
 * Draft count/cause of action
 */
export interface DraftCount {
  countNumber: number;
  title: string;
  statutoryCitation: string;
  incorporationParagraph: string;
  allegations: DraftAllegation[];
  damagesParagraph: string;
}

/**
 * Individual allegation in a count
 */
export interface DraftAllegation {
  paragraphNumber: number;
  text: string;
  elementAddressed: number;
  plausibilityScore: number;  // 0-100
  rule9bCompliant?: boolean;
}

/**
 * Complete draft output for a claim
 */
export interface ClaimDraftOutput {
  claimKey: string;
  elementsTable: ElementsTableRow[];
  preconditions: ClaimPrecondition[];
  defenses: DefenseWarning[];
  pleadingChecklist: PleadingChecklistEntry[];
  draftCount: DraftCount;
  factGaps: FactGap[];
  mtdRisk: MTDRiskScore;
}

// ============================================================================
// RISK SCORING TYPES
// ============================================================================

/**
 * Individual risk factor
 */
export interface RiskFactor {
  category: RiskCategory;
  score: number;  // 0-100
  weight: number; // Weight in overall score
  issue: string;
  fix: string;
}

/**
 * Risk categories for MTD analysis
 */
export type RiskCategory =
  | 'standing'
  | 'immunity'
  | 'exhaustion'
  | 'sol'
  | 'rule_9b'
  | 'monell'
  | 'causation'
  | 'damages'
  | 'plausibility';

/**
 * Complete MTD risk score
 */
export interface MTDRiskScore {
  overallScore: number;  // 0-100 (higher = more risk)
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  factors: RiskFactor[];
  topVulnerabilities: string[];
  prioritizedFixes: string[];
}

/**
 * Defense/immunity warning
 */
export interface DefenseWarning {
  type: string;
  likelihood: 'high' | 'medium' | 'low';
  description: string;
  counterArguments: string[];
}

// ============================================================================
// JURISDICTION TYPES
// ============================================================================

/**
 * Jurisdiction analysis result
 */
export interface JurisdictionAnalysis {
  subjectMatter: {
    basis: JurisdictionBasis;
    satisfied: boolean;
    analysis: string;
    citations: string[];
  };
  personalJurisdiction: {
    satisfied: boolean;
    basis: 'general' | 'specific' | 'consent';
    analysis: string;
  };
  venue: {
    proper: boolean;
    basis: string;
    analysis: string;
  };
  standing: {
    injuryInFact: boolean;
    causation: boolean;
    redressability: boolean;
    analysis: string;
  };
}

// ============================================================================
// COMPLAINT SKELETON TYPES
// ============================================================================

/**
 * Complete complaint structure
 */
export interface ComplaintSkeleton {
  caption: string;
  partiesSection: string;
  jurisdictionSection: string;
  venueSection: string;
  generalAllegations: string[];
  counts: DraftCount[];
  prayerForRelief: string;
  juryDemand: boolean;
  certificateOfService: string;
  verification?: string;
}

// ============================================================================
// OUTPUT TYPES
// ============================================================================

/**
 * Complete engine output
 */
export interface PleadingEngineOutput {
  caseInput: CaseInput;
  jurisdictionAnalysis: JurisdictionAnalysis;
  claimOutputs: ClaimDraftOutput[];
  complaintSkeleton: ComplaintSkeleton;
  consolidatedFactGaps: FactGap[];
  recommendations: string[];
  generatedAt: string;
}

/**
 * Validation error
 */
export interface ValidationError {
  field: string;
  message: string;
  severity: 'error' | 'warning';
}

/**
 * Validation result
 */
export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Claim suggestion when auto_suggest is requested
 */
export interface ClaimSuggestion {
  claimKey: string;
  claimName: string;
  matchScore: number;  // 0-100
  reasons: string[];
  showstoppers: string[];
  missingCriticalFacts: string[];
}
