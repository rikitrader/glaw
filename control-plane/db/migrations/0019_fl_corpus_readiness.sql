CREATE TABLE IF NOT EXISTS pclc_fl_corpus_readiness (
  readiness_id TEXT PRIMARY KEY,
  jurisdiction TEXT NOT NULL DEFAULT 'FL',
  issue_code TEXT NOT NULL,
  historical_statutes_verified INTEGER NOT NULL DEFAULT 0,
  judicial_opinions_verified INTEGER NOT NULL DEFAULT 0,
  actual_policy_verified INTEGER NOT NULL DEFAULT 0,
  provenance_complete INTEGER NOT NULL DEFAULT 0,
  human_review_complete INTEGER NOT NULL DEFAULT 0,
  critical_conflicts INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL,
  ruleset_version TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_pclc_fl_corpus_readiness_issue ON pclc_fl_corpus_readiness(jurisdiction, issue_code);
