CREATE INDEX IF NOT EXISTS idx_judge_profile_reviews_identity_scope ON judge_profile_reviews(tenant_id, judge_id, decision, created_at);
