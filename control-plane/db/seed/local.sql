INSERT OR IGNORE INTO organizations (id, name, status, created_at)
VALUES ('org-local', 'GLAW Local Test Organization', 'confirmed', '2026-08-23T00:00:00.000Z');

INSERT OR IGNORE INTO users (id, organization_id, email, role, status, created_at)
VALUES ('user-local-admin', 'org-local', 'local.admin@glaw.test', 'administrator', 'confirmed', '2026-08-23T00:00:00.000Z');

INSERT OR IGNORE INTO matters (id, organization_id, matter_number, name, department, status, risk, confidentiality, created_at, updated_at)
VALUES ('matter-local-001', 'org-local', 'GLAW-LOCAL-001', 'Local Control Plane Smoke Matter', 'Litigation', 'active', 'yellow', 'attorney-client', '2026-08-23T00:00:00.000Z', '2026-08-23T00:00:00.000Z');

INSERT OR IGNORE INTO workflows (id, organization_id, matter_id, name, version, status, definition_json, created_at)
VALUES ('workflow-local-intake', 'org-local', 'matter-local-001', 'Matter Intake Spine', '1.0.0', 'confirmed', '{"id":"matter-intake-spine","steps":["intake","strategy","structure","draft","adversarial","file","docket","retro"]}', '2026-08-23T00:00:00.000Z');

INSERT OR IGNORE INTO approvals (id, organization_id, matter_id, workflow_id, required_role, status, created_at)
VALUES ('approval-local-001', 'org-local', 'matter-local-001', 'workflow-local-intake', 'attorney', 'pending', '2026-08-23T00:00:00.000Z');

INSERT OR IGNORE INTO audit_events (id, organization_id, matter_id, actor_id, event_type, payload_json, created_at)
VALUES ('audit-local-001', 'org-local', 'matter-local-001', 'user-local-admin', 'local_seeded', '{"source":"control-plane/db/seed/local.sql"}', '2026-08-23T00:00:00.000Z');

INSERT OR IGNORE INTO authorization_tuples (id, tenant_id, subject_type, subject_id, relation, resource_type, resource_id, policy_version, created_at)
VALUES ('tuple-local-admin-matter', 'org-local', 'user', 'user-local-admin', 'admin', 'matter', 'matter-local-001', '1.0.0', '2026-08-23T00:00:00.000Z');

INSERT OR IGNORE INTO region_policies (tenant_id, home_region, allowed_regions_json, deployment_mode, fencing_epoch, updated_at)
VALUES ('org-local', 'local', '["local"]', 'single-tenant', 0, '2026-08-23T00:00:00.000Z');
