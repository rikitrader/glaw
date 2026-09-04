CREATE TABLE IF NOT EXISTS pclc_policy_clause_fingerprints (
  fingerprint_id TEXT PRIMARY KEY,
  claim_id TEXT,
  policy_hash TEXT NOT NULL,
  form TEXT NOT NULL,
  edition TEXT NOT NULL,
  section TEXT NOT NULL,
  normalized_text TEXT NOT NULL,
  critical_phrases_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pclc_case_policy_matches (
  match_id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  claim_fingerprint_id TEXT NOT NULL REFERENCES pclc_policy_clause_fingerprints(fingerprint_id),
  case_fingerprint_id TEXT NOT NULL,
  match_type TEXT NOT NULL,
  material_differences_json TEXT NOT NULL,
  confidence INTEGER NOT NULL,
  human_review_required INTEGER NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pclc_case_holdings (
  holding_id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  case_name TEXT NOT NULL,
  citation TEXT NOT NULL,
  court TEXT NOT NULL,
  decision_date TEXT NOT NULL,
  holding TEXT NOT NULL,
  pinpoint_json TEXT NOT NULL,
  verification_status TEXT NOT NULL,
  source_url TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pclc_human_legal_reviews (
  review_id TEXT PRIMARY KEY,
  claim_id TEXT NOT NULL,
  jurisdiction TEXT NOT NULL,
  issue_code TEXT NOT NULL,
  question TEXT NOT NULL,
  scope TEXT NOT NULL,
  status TEXT NOT NULL,
  request_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pclc_human_legal_review_decisions (
  decision_id TEXT PRIMARY KEY,
  review_id TEXT NOT NULL REFERENCES pclc_human_legal_reviews(review_id),
  action TEXT NOT NULL,
  reviewer TEXT NOT NULL,
  reason TEXT NOT NULL,
  authority_relied_on_json TEXT NOT NULL,
  scope TEXT NOT NULL,
  decided_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pclc_case_holdings_citation ON pclc_case_holdings(citation, verification_status);
CREATE INDEX IF NOT EXISTS idx_pclc_policy_case_matches ON pclc_case_policy_matches(case_id, match_type, human_review_required);
CREATE INDEX IF NOT EXISTS idx_pclc_human_legal_reviews ON pclc_human_legal_reviews(jurisdiction, issue_code, status);
