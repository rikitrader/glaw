CREATE TABLE IF NOT EXISTS pclc_fl_statutory_versions (
  version_id TEXT PRIMARY KEY,
  authority_id TEXT NOT NULL,
  citation TEXT NOT NULL,
  valid_from TEXT NOT NULL,
  valid_to TEXT,
  source_snapshot_id TEXT NOT NULL,
  operative_text TEXT NOT NULL,
  applicability_json TEXT NOT NULL,
  effective_date_verified INTEGER NOT NULL,
  applicability_verified INTEGER NOT NULL,
  verified INTEGER NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pclc_fl_opinion_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  source_url TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  content TEXT NOT NULL,
  official_source INTEGER NOT NULL,
  retrieved_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pclc_fl_dca_conflicts (
  conflict_id TEXT PRIMARY KEY,
  issue_code TEXT NOT NULL,
  cases_json TEXT NOT NULL,
  districts_json TEXT NOT NULL,
  holdings_json TEXT NOT NULL,
  status TEXT NOT NULL,
  human_review_required INTEGER NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pclc_fl_statutory_time ON pclc_fl_statutory_versions(authority_id, valid_from, valid_to, verified);
CREATE INDEX IF NOT EXISTS idx_pclc_fl_opinions_case ON pclc_fl_opinion_snapshots(case_id, official_source);
CREATE INDEX IF NOT EXISTS idx_pclc_fl_conflicts_issue ON pclc_fl_dca_conflicts(issue_code, status);
