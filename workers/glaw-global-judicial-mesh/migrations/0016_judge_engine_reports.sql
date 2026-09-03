CREATE TABLE IF NOT EXISTS judge_engine_reports (id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, judge_id TEXT NOT NULL, matter_id TEXT, issue TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_judge_engine_reports_scope ON judge_engine_reports(tenant_id, judge_id, matter_id, created_at);
