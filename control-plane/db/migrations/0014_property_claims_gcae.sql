CREATE TABLE IF NOT EXISTS property_claims (
  claim_id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  matter_id TEXT,
  policy_id TEXT,
  jurisdiction TEXT,
  stage TEXT NOT NULL,
  status TEXT NOT NULL,
  source_manifest_sha256 TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS property_claim_documents (
  doc_id TEXT PRIMARY KEY,
  claim_id TEXT NOT NULL REFERENCES property_claims(claim_id),
  filename TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  document_type TEXT NOT NULL,
  original_path TEXT NOT NULL,
  source_status TEXT NOT NULL,
  metadata_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_property_claim_document_hash
  ON property_claim_documents(claim_id, sha256);

CREATE TABLE IF NOT EXISTS property_claim_findings (
  finding_id TEXT PRIMARY KEY,
  claim_id TEXT NOT NULL REFERENCES property_claims(claim_id),
  issue_type TEXT NOT NULL,
  disposition TEXT NOT NULL,
  evidence_json TEXT NOT NULL,
  policy_json TEXT NOT NULL,
  authority_json TEXT NOT NULL,
  red_json TEXT NOT NULL,
  blue_json TEXT NOT NULL,
  white_json TEXT NOT NULL,
  confidence_json TEXT NOT NULL,
  human_review_required INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_property_claim_documents_claim
  ON property_claim_documents(claim_id, created_at);
CREATE INDEX IF NOT EXISTS idx_property_claim_findings_claim
  ON property_claim_findings(claim_id, created_at);
