ALTER TABLE judge_profile_reviews ADD COLUMN tenant_id TEXT NOT NULL DEFAULT 'legacy';
CREATE INDEX IF NOT EXISTS idx_judge_profile_reviews_tenant ON judge_profile_reviews(tenant_id, judge_id, created_at);
