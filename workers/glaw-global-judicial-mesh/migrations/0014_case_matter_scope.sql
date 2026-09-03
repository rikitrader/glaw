ALTER TABLE judge_case_observations ADD COLUMN matter_id TEXT;
CREATE INDEX IF NOT EXISTS idx_judge_case_matter_scope ON judge_case_observations(tenant_id, judge_id, matter_id, issue_class);
