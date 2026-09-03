ALTER TABLE authority_records ADD COLUMN judge_id TEXT NOT NULL DEFAULT 'legacy';
CREATE INDEX IF NOT EXISTS idx_authority_records_judge_scope ON authority_records(tenant_id, judge_id, status);
