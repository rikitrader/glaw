import type { RiskClass } from "../contracts/legal";

export type WorkflowScope = "department" | "matter" | "personal" | "court" | "client" | "firm";
export type AdapterProtocol = "INTERNAL" | "REST" | "GRAPHQL" | "MCP" | "WEBHOOK" | "X402";

export type DepartmentDefinition = {
  id: string;
  name: string;
  description: string;
  scopes: WorkflowScope[];
  defaultReviewRole: string;
  jurisdictionPacks: string[];
  practicePacks: string[];
};

export type PersonaDefinition = {
  id: string;
  name: string;
  title: string;
  departmentId: string;
  kind: "lawyer" | "agent" | "reviewer" | "operator";
  mission: string;
  skillIds: string[];
  allowedToolIds: string[];
  defaultRisk: RiskClass;
  requiresHumanReview: boolean;
  workflowIds: string[];
};

export type SkillDefinition = {
  id: string;
  name: string;
  version: string;
  departmentId: string;
  practiceArea: string;
  jurisdictions: string[];
  inputSchema: string;
  outputSchema: string;
  requiredEvidence: string[];
  validatorIds: string[];
  signed: boolean;
};

export type AdapterDefinition = {
  id: string;
  name: string;
  protocol: AdapterProtocol;
  provider: string;
  description: string;
  capabilities: string[];
  sideEffect: "NONE" | "REVERSIBLE" | "IRREVERSIBLE";
  supportsIdempotency: boolean;
  supportsLookup: boolean;
  requiresApproval: boolean;
  configured: boolean;
};

export type PaymentPolicy = {
  enabled: boolean;
  protocol: "X402";
  currency: string;
  maxPerRunUsd: number;
  maxPerAgentUsd: number;
  approvalRequiredAboveUsd: number;
  walletRef: string;
  settlementAdapterId: string;
  legalAuthorizationSeparate: true;
};

export type PackDefinition = { id: string; name: string; kind: "jurisdiction" | "practice" | "court"; description: string; version: string };

export type WorkflowBinding = {
  workflowId: string;
  scope: WorkflowScope;
  departmentId: string;
  personaIds: string[];
  skillIds: string[];
  adapterIds: string[];
  packIds: string[];
  payment?: PaymentPolicy;
};

export const DEPARTMENTS: DepartmentDefinition[] = [
  { id: "litigation", name: "Litigation", description: "Disputes, pleadings, discovery, motions, and trial preparation.", scopes: ["department", "matter", "personal", "court"], defaultReviewRole: "supervising-attorney", jurisdictionPacks: ["us-federal", "us-ny", "us-fl"], practicePacks: ["civil-litigation", "court-filing"] },
  { id: "corporate", name: "Corporate / M&A", description: "Entity, governance, diligence, transactions, and closing workflows.", scopes: ["department", "matter", "client", "firm"], defaultReviewRole: "deal-counsel", jurisdictionPacks: ["delaware", "us-federal"], practicePacks: ["ma", "corporate-governance"] },
  { id: "tax", name: "Tax / IRS", description: "Tax research, controversy, reporting, and audit support.", scopes: ["department", "matter", "personal", "client"], defaultReviewRole: "tax-attorney", jurisdictionPacks: ["us-federal"], practicePacks: ["tax-controversy", "tax-compliance"] },
  { id: "regulatory", name: "Regulatory / Compliance", description: "Regulatory obligations, investigations, licensing, and monitoring.", scopes: ["department", "matter", "client", "firm"], defaultReviewRole: "compliance-counsel", jurisdictionPacks: ["us-federal", "eu"], practicePacks: ["aml", "privacy"] },
  { id: "knowledge-operations", name: "Knowledge Operations", description: "Firm precedent, playbooks, retrieval quality, and source governance.", scopes: ["department", "firm"], defaultReviewRole: "knowledge-counsel", jurisdictionPacks: ["us-federal", "england-wales"], practicePacks: ["legal-research", "precedent-management"] }
];

export const PACKS: PackDefinition[] = [
  { id: "us-federal", name: "US Federal", kind: "jurisdiction", description: "Federal authority hierarchy, citation, procedure, and deadlines.", version: "1.0.0" },
  { id: "us-ny", name: "New York", kind: "jurisdiction", description: "New York court and procedural rules.", version: "1.0.0" },
  { id: "us-fl", name: "Florida", kind: "jurisdiction", description: "Florida civil procedure and court rules.", version: "1.0.0" },
  { id: "delaware", name: "Delaware", kind: "jurisdiction", description: "Delaware corporate and Chancery materials.", version: "1.0.0" },
  { id: "england-wales", name: "England & Wales", kind: "jurisdiction", description: "England and Wales authority and practice configuration.", version: "1.0.0" },
  { id: "civil-litigation", name: "Civil Litigation", kind: "practice", description: "Issue, claim, defense, evidence, and adversarial review workflow.", version: "1.0.0" },
  { id: "court-filing", name: "Court Filing", kind: "court", description: "Prepare, approve, submit, receipt, and reconcile filings.", version: "1.0.0" },
  { id: "legal-research", name: "Legal Research", kind: "practice", description: "Primary-law research, contrary authority, and citation verification.", version: "1.0.0" },
  { id: "ma", name: "M&A", kind: "practice", description: "Diligence, issue tracking, drafting, and closing controls.", version: "1.0.0" },
  { id: "corporate-governance", name: "Corporate Governance", kind: "practice", description: "Board, shareholder, consent, and governance deliverables.", version: "1.0.0" },
  { id: "tax-controversy", name: "Tax Controversy", kind: "practice", description: "IRS audit, notice, response, and escalation workflow.", version: "1.0.0" },
  { id: "tax-compliance", name: "Tax Compliance", kind: "practice", description: "Deterministic filing and review workflow controls.", version: "1.0.0" },
  { id: "aml", name: "AML / KYC", kind: "practice", description: "Risk-based compliance and evidence review.", version: "1.0.0" },
  { id: "privacy", name: "Privacy", kind: "practice", description: "Privacy intake, data mapping, and incident controls.", version: "1.0.0" },
  { id: "precedent-management", name: "Precedent Management", kind: "practice", description: "Firm-approved precedent lifecycle and access controls.", version: "1.0.0" }
];

export const SKILLS: SkillDefinition[] = [
  { id: "legal-research", name: "Legal Research", version: "3.4.1", departmentId: "knowledge-operations", practiceArea: "research", jurisdictions: ["US-FEDERAL", "US-NY", "US-FL", "DELAWARE", "ENGLAND-WALES"], inputSchema: "ResearchRequest", outputSchema: "EvidencePacket[]", requiredEvidence: ["primary_law", "contrary_authority"], validatorIds: ["citation-validator", "authority-validator"], signed: true },
  { id: "motion-analysis", name: "Motion Analysis", version: "2.1.0", departmentId: "litigation", practiceArea: "litigation", jurisdictions: ["US-FEDERAL", "US-NY", "US-FL"], inputSchema: "MatterIssueSet", outputSchema: "LegalArgumentGraph", requiredEvidence: ["primary_law", "court_record"], validatorIds: ["citation-validator", "red-team"], signed: true },
  { id: "contract-review", name: "Contract Review", version: "4.0.0", departmentId: "corporate", practiceArea: "contracts", jurisdictions: ["US-FEDERAL", "DELAWARE", "ENGLAND-WALES"], inputSchema: "ContractDocument", outputSchema: "IssueLedger", requiredEvidence: ["contract_version", "playbook"], validatorIds: ["clause-validator", "human-review"], signed: true },
  { id: "docket-monitoring", name: "Docket Monitoring", version: "1.2.0", departmentId: "litigation", practiceArea: "courts", jurisdictions: ["US-FEDERAL", "US-NY", "US-FL"], inputSchema: "DocketWatch", outputSchema: "MatterEvent", requiredEvidence: ["court_record"], validatorIds: ["deadline-validator"], signed: true },
  { id: "citation-validation", name: "Citation Validation", version: "2.0.0", departmentId: "knowledge-operations", practiceArea: "governance", jurisdictions: ["US-FEDERAL", "US-NY", "US-FL", "DELAWARE", "ENGLAND-WALES"], inputSchema: "DraftWithClaims", outputSchema: "CitationReport", requiredEvidence: ["source_span", "document_hash"], validatorIds: ["authority-validator"], signed: true },
  { id: "human-review-packet", name: "Human Review Packet", version: "1.0.0", departmentId: "knowledge-operations", practiceArea: "governance", jurisdictions: ["GLOBAL"], inputSchema: "WorkflowResult", outputSchema: "ReviewPacket", requiredEvidence: ["evidence_ledger", "audit_trace"], validatorIds: ["policy-validator"], signed: true }
];

export const ADAPTERS: AdapterDefinition[] = [
  { id: "mcp-legal-research", name: "Legal Research MCP", protocol: "MCP", provider: "GLAW MCP", description: "Authorized search and source retrieval through the GLAW MCP boundary.", capabilities: ["research.search", "authority.read", "evidence.write"], sideEffect: "NONE", supportsIdempotency: true, supportsLookup: true, requiresApproval: false, configured: true },
  { id: "court-docket-api", name: "Court Docket API", protocol: "REST", provider: "Configured court provider", description: "Read docket state and reconcile filing receipts.", capabilities: ["court.search", "court.lookup", "court.file"], sideEffect: "IRREVERSIBLE", supportsIdempotency: true, supportsLookup: true, requiresApproval: true, configured: false },
  { id: "dms-api", name: "DMS Adapter", protocol: "REST", provider: "Customer DMS", description: "Scoped document read/write with version and hash preservation.", capabilities: ["document.read", "document.write"], sideEffect: "REVERSIBLE", supportsIdempotency: true, supportsLookup: true, requiresApproval: false, configured: false },
  { id: "email-api", name: "Email Adapter", protocol: "REST", provider: "Customer mail provider", description: "Draft and send messages only through approval-aware commands.", capabilities: ["email.draft", "email.send"], sideEffect: "IRREVERSIBLE", supportsIdempotency: true, supportsLookup: true, requiresApproval: true, configured: false },
  { id: "docusign-api", name: "DocuSign Adapter", protocol: "REST", provider: "DocuSign", description: "Prepare and reconcile signature envelopes.", capabilities: ["signature.request", "signature.lookup"], sideEffect: "IRREVERSIBLE", supportsIdempotency: true, supportsLookup: true, requiresApproval: true, configured: false },
  { id: "x402-settlement", name: "x402 Agent Settlement", protocol: "X402", provider: "Configured payment facilitator", description: "Metered agent/tool usage settlement. Payment never grants legal authority.", capabilities: ["usage.quote", "usage.authorize", "usage.settle"], sideEffect: "IRREVERSIBLE", supportsIdempotency: true, supportsLookup: true, requiresApproval: true, configured: false }
];

export const PERSONAS: PersonaDefinition[] = [
  { id: "matter-governor", name: "Matter Governor", title: "Workflow authority and risk router", departmentId: "knowledge-operations", kind: "agent", mission: "Resolve scope, conflict, policy, risk, and review requirements before execution.", skillIds: ["human-review-packet"], allowedToolIds: ["authority.read", "evidence.write"], defaultRisk: "HIGH", requiresHumanReview: true, workflowIds: ["litigation-analysis", "contract-review", "court-filing"] },
  { id: "research-counsel", name: "Research Counsel", title: "Primary-law research lawyer", departmentId: "litigation", kind: "lawyer", mission: "Build a cited, temporally correct, adversarially tested authority record.", skillIds: ["legal-research", "citation-validation"], allowedToolIds: ["research.search", "authority.read", "evidence.write"], defaultRisk: "HIGH", requiresHumanReview: true, workflowIds: ["litigation-analysis"] },
  { id: "drafting-counsel", name: "Drafting Counsel", title: "Legal drafting lawyer", departmentId: "corporate", kind: "lawyer", mission: "Turn approved facts and authority into reviewable legal work product.", skillIds: ["contract-review", "human-review-packet"], allowedToolIds: ["matter.read", "document.read", "document.write"], defaultRisk: "HIGH", requiresHumanReview: true, workflowIds: ["contract-review", "litigation-analysis"] },
  { id: "court-operations-agent", name: "Court Operations Agent", title: "Docket and filing operator", departmentId: "litigation", kind: "agent", mission: "Prepare court packets and reconcile authoritative docket state.", skillIds: ["docket-monitoring", "human-review-packet"], allowedToolIds: ["court.search", "court.lookup"], defaultRisk: "CRITICAL", requiresHumanReview: true, workflowIds: ["court-filing"] },
  { id: "opposition-counsel", name: "Opposition Counsel", title: "Independent red-team lawyer", departmentId: "litigation", kind: "reviewer", mission: "Attack unsupported claims, authority gaps, procedural defects, and privilege risks.", skillIds: ["legal-research", "motion-analysis"], allowedToolIds: ["research.search", "authority.read"], defaultRisk: "HIGH", requiresHumanReview: true, workflowIds: ["litigation-analysis", "contract-review"] }
];

export const WORKFLOW_BINDINGS: WorkflowBinding[] = [
  { workflowId: "litigation-analysis", scope: "matter", departmentId: "litigation", personaIds: ["matter-governor", "research-counsel", "drafting-counsel", "opposition-counsel"], skillIds: ["legal-research", "motion-analysis", "citation-validation", "human-review-packet"], adapterIds: ["mcp-legal-research", "dms-api", "x402-settlement"], packIds: ["us-federal", "civil-litigation", "legal-research"], payment: { enabled: false, protocol: "X402", currency: "USD", maxPerRunUsd: 25, maxPerAgentUsd: 8, approvalRequiredAboveUsd: 5, walletRef: "tenant-configured", settlementAdapterId: "x402-settlement", legalAuthorizationSeparate: true } },
  { workflowId: "contract-review", scope: "client", departmentId: "corporate", personaIds: ["matter-governor", "drafting-counsel"], skillIds: ["contract-review", "citation-validation", "human-review-packet"], adapterIds: ["dms-api", "email-api", "x402-settlement"], packIds: ["delaware", "ma", "corporate-governance"], payment: { enabled: false, protocol: "X402", currency: "USD", maxPerRunUsd: 15, maxPerAgentUsd: 5, approvalRequiredAboveUsd: 5, walletRef: "tenant-configured", settlementAdapterId: "x402-settlement", legalAuthorizationSeparate: true } },
  { workflowId: "court-filing", scope: "court", departmentId: "litigation", personaIds: ["matter-governor", "court-operations-agent", "research-counsel"], skillIds: ["docket-monitoring", "citation-validation", "human-review-packet"], adapterIds: ["court-docket-api", "dms-api", "x402-settlement"], packIds: ["us-federal", "court-filing"], payment: { enabled: false, protocol: "X402", currency: "USD", maxPerRunUsd: 40, maxPerAgentUsd: 10, approvalRequiredAboveUsd: 1, walletRef: "tenant-configured", settlementAdapterId: "x402-settlement", legalAuthorizationSeparate: true } }
];

export function getGovernedCatalog() {
  return { departments: DEPARTMENTS, personas: PERSONAS, skills: SKILLS, adapters: ADAPTERS, packs: PACKS, workflows: WORKFLOW_BINDINGS, generatedAt: new Date().toISOString(), schemaVersion: "1.0.0" };
}

export function validateWorkflowBinding(binding: WorkflowBinding): string[] {
  const findings: string[] = [];
  const department = DEPARTMENTS.find((item) => item.id === binding.departmentId);
  if (!department) findings.push("department_not_found");
  if (!binding.personaIds.length) findings.push("persona_required");
  if (!binding.skillIds.length) findings.push("skill_required");
  for (const personaId of binding.personaIds) {
    const persona = PERSONAS.find((item) => item.id === personaId);
    if (!persona) findings.push(`persona_not_found:${personaId}`);
    else if (persona.departmentId !== binding.departmentId && persona.departmentId !== "knowledge-operations") findings.push(`persona_department_mismatch:${personaId}`);
  }
  for (const skillId of binding.skillIds) if (!SKILLS.some((item) => item.id === skillId)) findings.push(`skill_not_found:${skillId}`);
  for (const adapterId of binding.adapterIds) if (!ADAPTERS.some((item) => item.id === adapterId)) findings.push(`adapter_not_found:${adapterId}`);
  if (binding.scope === "court" && !binding.adapterIds.some((id) => id === "court-docket-api")) findings.push("court_adapter_required");
  if (binding.payment?.enabled && !binding.adapterIds.includes("x402-settlement")) findings.push("x402_adapter_required");
  if (binding.payment?.legalAuthorizationSeparate !== true) findings.push("payment_cannot_authorize_legal_action");
  if (!binding.personaIds.some((id) => PERSONAS.find((persona) => persona.id === id)?.requiresHumanReview)) findings.push("human_review_persona_required");
  return findings;
}
