CREATE TABLE IF NOT EXISTS pclc_authorities (
  authority_id TEXT PRIMARY KEY,
  jurisdiction TEXT NOT NULL,
  authority_type TEXT NOT NULL,
  citation TEXT NOT NULL,
  official_source_url TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  verification_status TEXT NOT NULL,
  valid_from TEXT,
  valid_to TEXT,
  system_from TEXT NOT NULL,
  system_to TEXT,
  metadata_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pclc_propositions (
  proposition_id TEXT PRIMARY KEY,
  authority_id TEXT NOT NULL REFERENCES pclc_authorities(authority_id),
  jurisdiction TEXT NOT NULL,
  issue_code TEXT NOT NULL,
  rule_text TEXT NOT NULL,
  temporal_json TEXT NOT NULL,
  verification_status TEXT NOT NULL,
  confidence INTEGER NOT NULL CHECK (confidence BETWEEN 0 AND 100),
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pclc_rules (
  rule_id TEXT PRIMARY KEY,
  jurisdiction TEXT NOT NULL,
  issue_code TEXT NOT NULL,
  validity_from TEXT NOT NULL,
  validity_to TEXT,
  system_from TEXT NOT NULL,
  system_to TEXT,
  status TEXT NOT NULL,
  authority_refs_json TEXT NOT NULL,
  rule_json TEXT NOT NULL,
  compiler_version TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pclc_authorities_jurisdiction_type ON pclc_authorities(jurisdiction, authority_type);
CREATE INDEX IF NOT EXISTS idx_pclc_authorities_valid_time ON pclc_authorities(jurisdiction, valid_from, valid_to);
CREATE INDEX IF NOT EXISTS idx_pclc_propositions_issue ON pclc_propositions(jurisdiction, issue_code, verification_status);
CREATE INDEX IF NOT EXISTS idx_pclc_rules_issue_validity ON pclc_rules(jurisdiction, issue_code, validity_from, validity_to, status);
