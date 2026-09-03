CREATE TABLE IF NOT EXISTS pclc_source_documents (
  source_id TEXT PRIMARY KEY,
  jurisdiction TEXT NOT NULL,
  authority_type TEXT NOT NULL,
  title TEXT NOT NULL,
  official_url TEXT NOT NULL,
  retrieved_at TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pclc_source_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL REFERENCES pclc_source_documents(source_id),
  source_url TEXT NOT NULL,
  retrieved_at TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  raw_text_hash TEXT NOT NULL,
  parsed_text_hash TEXT,
  parser_version TEXT NOT NULL,
  verified INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pclc_research_queue (
  queue_id TEXT PRIMARY KEY,
  jurisdiction TEXT NOT NULL,
  issue_code TEXT NOT NULL,
  reason_code TEXT NOT NULL,
  priority INTEGER NOT NULL,
  status TEXT NOT NULL,
  missing_json TEXT NOT NULL,
  last_attempt_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pclc_conflicts (
  conflict_id TEXT PRIMARY KEY,
  jurisdiction TEXT NOT NULL,
  issue_code TEXT NOT NULL,
  authority_a TEXT NOT NULL,
  authority_b TEXT NOT NULL,
  conflict_type TEXT NOT NULL,
  resolution_json TEXT NOT NULL,
  human_review_required INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pclc_compiler_runs (
  run_id TEXT PRIMARY KEY,
  jurisdiction TEXT NOT NULL,
  issue_code TEXT NOT NULL,
  legal_date TEXT NOT NULL,
  system_date TEXT NOT NULL,
  source_snapshot_id TEXT,
  compiler_version TEXT NOT NULL,
  status TEXT NOT NULL,
  metrics_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pclc_human_reviews (
  review_id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES pclc_compiler_runs(run_id),
  reviewer_id TEXT NOT NULL,
  action TEXT NOT NULL,
  rationale TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pclc_sources_jurisdiction ON pclc_source_documents(jurisdiction, authority_type, status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_pclc_snapshot_hash ON pclc_source_snapshots(source_id, content_hash);
CREATE INDEX IF NOT EXISTS idx_pclc_research_queue ON pclc_research_queue(status, priority DESC, jurisdiction, issue_code);
CREATE INDEX IF NOT EXISTS idx_pclc_conflicts_issue ON pclc_conflicts(jurisdiction, issue_code, human_review_required);
CREATE INDEX IF NOT EXISTS idx_pclc_runs_dates ON pclc_compiler_runs(jurisdiction, issue_code, legal_date, system_date);
