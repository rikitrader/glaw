ALTER TABLE discovery_objects ADD COLUMN source_id TEXT;
CREATE INDEX IF NOT EXISTS idx_discovery_objects_source_scope ON discovery_objects(tenant_id, matter_id, source_id, status);
