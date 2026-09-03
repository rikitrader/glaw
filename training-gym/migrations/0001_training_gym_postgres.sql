-- PostgreSQL reference migration. Apply only through the repository's migration runner.
-- Large trajectory/state payloads belong in object storage; PostgreSQL stores metadata and hashes.
create table if not exists gym_organizations (
  id text primary key, name text not null, created_at timestamptz not null default now()
);
create table if not exists gym_versions (
  id text primary key, organization_id text not null references gym_organizations(id), name text not null,
  version text not null, manifest jsonb not null, created_at timestamptz not null default now(),
  unique (organization_id, name, version)
);
create table if not exists gym_tasks (
  id text primary key, organization_id text not null references gym_organizations(id), gym_version_id text not null references gym_versions(id),
  version text not null, definition jsonb not null, created_at timestamptz not null default now(),
  unique (organization_id, id, version)
);
create table if not exists gym_experiments (
  id text primary key, organization_id text not null references gym_organizations(id), config jsonb not null,
  status text not null, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists gym_episodes (
  id text primary key, organization_id text not null references gym_organizations(id), experiment_id text not null references gym_experiments(id),
  task_id text not null references gym_tasks(id), status text not null, seed bigint not null, version_pins jsonb not null,
  attempt integer not null default 0, idempotency_key text not null unique, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index if not exists gym_episodes_org_status_idx on gym_episodes (organization_id, status);
create index if not exists gym_episodes_experiment_idx on gym_episodes (experiment_id, created_at);
create table if not exists gym_episode_transitions (
  id bigserial primary key, episode_id text not null references gym_episodes(id), from_status text not null, to_status text not null,
  reason text, metadata jsonb, occurred_at timestamptz not null
);
create table if not exists gym_artifacts (
  id text primary key, organization_id text not null references gym_organizations(id), episode_id text references gym_episodes(id),
  object_key text not null, sha256 text not null, bytes bigint not null, content_type text, created_at timestamptz not null default now(), unique (organization_id, object_key)
);
create table if not exists gym_audit_events (
  id bigserial primary key, organization_id text not null references gym_organizations(id), actor_id text not null,
  event_type text not null, entity_id text, payload jsonb not null, occurred_at timestamptz not null default now()
);
create index if not exists gym_audit_org_time_idx on gym_audit_events (organization_id, occurred_at);
