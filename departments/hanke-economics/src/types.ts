export type EvidenceLabel =
  | 'HANKE-DIRECT' | 'HANKE-FRAMEWORK' | 'SYSTEM-INFERENCE'
  | 'SYSTEM-CALCULATION' | 'HISTORICAL-EVIDENCE' | 'EXTERNAL-VIEW'
  | 'RED-TEAM-CHALLENGE' | 'BLUE-TEAM-RESPONSE' | 'UNRESOLVED';

export type Confidence = 'VERY HIGH' | 'HIGH' | 'MODERATE' | 'LOW' | 'VERY LOW';
export type SourceStatus = 'KNOWN' | 'FOUND' | 'INGESTED' | 'INDEXED' | 'VERIFIED' | 'MISSING' | 'RESTRICTED';

export interface SourceRecord {
  document_id: string;
  author: string;
  coauthors: string[];
  title: string;
  publication?: string;
  publisher?: string;
  publication_date?: string;
  year?: number;
  source_url?: string;
  document_type: string;
  country: string[];
  topic: string[];
  economic_regime: string[];
  policy_position: string[];
  methodology: string[];
  dataset: string[];
  formula: string[];
  historical_case: string[];
  page?: number;
  section?: string;
  citation_anchor?: string;
  primary_source: boolean;
  authority_level: 1 | 2 | 3 | 4 | 5 | 6 | 7;
  confidence: number;
  status: SourceStatus;
}

export interface Observation {
  series_id: string;
  observation_date: string;
  release_date?: string;
  revision_date?: string;
  source_document_id: string;
  value: number;
  unit: string;
  vintage?: string;
}

export interface CalculationResult {
  formula: string;
  inputs: Record<string, number | string | number[]>;
  result: number;
  unit: string;
  date?: string;
  source_data: string[];
  assumptions: string[];
  verification: 'PASS' | 'REVIEW' | 'FAIL';
}

export interface Claim {
  claim_id: string;
  text: string;
  label: EvidenceLabel;
  source_ids: string[];
  data_ids: string[];
  calculation_ids: string[];
  assumptions: string[];
  counterarguments: string[];
  confidence: Confidence;
  status: 'SUPPORTED' | 'CONDITIONAL' | 'UNRESOLVED' | 'BLOCKED';
}

export interface PolicyOption {
  option_id: string;
  name: string;
  inflation_stability: number;
  banking_stability: number;
  fiscal_discipline: number;
  credit_availability: number;
  implementation_difficulty: number;
  reserve_requirement: number;
  political_feasibility: number;
  institutional_requirements: number;
  transition_risk: number;
  long_term_credibility: number;
}

export interface AuditFinding {
  finding_id: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  category: 'DATA' | 'MATH' | 'CITATION' | 'CAUSALITY' | 'INSTITUTIONAL' | 'POLITICAL';
  text: string;
  evidence_ids: string[];
  owner?: string;
  status: 'OPEN' | 'PARTIALLY_RESOLVED' | 'RESOLVED' | 'CARRIED';
}
