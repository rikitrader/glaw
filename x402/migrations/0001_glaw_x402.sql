CREATE TABLE IF NOT EXISTS api_clients (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  key_hash TEXT NOT NULL UNIQUE,
  secret_hash TEXT NOT NULL,
  scopes TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  created_ms INTEGER NOT NULL,
  last_used_ms INTEGER
);

CREATE TABLE IF NOT EXISTS agent_catalog (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  domain TEXT NOT NULL,
  path TEXT,
  description TEXT,
  description_hash TEXT,
  active INTEGER NOT NULL DEFAULT 1,
  created_ms INTEGER NOT NULL,
  updated_ms INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS service_catalog (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT NOT NULL,
  default_unit TEXT NOT NULL,
  risk_tier TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  created_ms INTEGER NOT NULL,
  updated_ms INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS service_prices (
  id TEXT PRIMARY KEY,
  service_id TEXT NOT NULL,
  version INTEGER NOT NULL,
  base_usd INTEGER NOT NULL,
  minimum_usd INTEGER NOT NULL,
  list_usd INTEGER NOT NULL,
  unit_rates_json TEXT NOT NULL,
  created_ms INTEGER NOT NULL,
  UNIQUE(service_id, version)
);

CREATE TABLE IF NOT EXISTS charges (
  id TEXT PRIMARY KEY,
  client_id TEXT,
  quote_id TEXT NOT NULL,
  quote_json TEXT NOT NULL,
  service_id TEXT,
  agent_id TEXT,
  matter_id TEXT,
  memo TEXT,
  status TEXT NOT NULL,
  amount_usd INTEGER NOT NULL,
  amount_atomic TEXT NOT NULL,
  currency TEXT NOT NULL DEFAULT 'USDC',
  pay_url TEXT NOT NULL,
  idempotency_key TEXT,
  created_ms INTEGER NOT NULL,
  updated_ms INTEGER NOT NULL,
  UNIQUE(client_id, idempotency_key)
);

CREATE TABLE IF NOT EXISTS payments (
  id TEXT PRIMARY KEY,
  charge_id TEXT NOT NULL,
  status TEXT NOT NULL,
  scheme TEXT NOT NULL,
  network TEXT NOT NULL,
  chain_id INTEGER,
  asset TEXT NOT NULL,
  amount_atomic TEXT NOT NULL,
  amount_usd INTEGER NOT NULL,
  pay_to TEXT NOT NULL,
  payer TEXT,
  tx_hash TEXT,
  authorization_hash TEXT UNIQUE,
  payload_json TEXT,
  facilitator_response TEXT,
  invalid_reason TEXT,
  idempotency_key TEXT,
  created_ms INTEGER NOT NULL,
  verified_ms INTEGER,
  settled_ms INTEGER
);

CREATE INDEX IF NOT EXISTS idx_payments_charge ON payments(charge_id);
CREATE INDEX IF NOT EXISTS idx_charges_status ON charges(status);

CREATE TABLE IF NOT EXISTS agent_edges (
  a TEXT NOT NULL,
  b TEXT NOT NULL,
  reason TEXT NOT NULL,
  PRIMARY KEY (a, b)
);

CREATE TABLE IF NOT EXISTS agent_life (
  agent_id TEXT PRIMARY KEY,
  generation INTEGER NOT NULL DEFAULT 0,
  state TEXT NOT NULL DEFAULT 'dormant',
  energy REAL NOT NULL DEFAULT 0,
  paid_count INTEGER NOT NULL DEFAULT 0,
  live_neighbor_count INTEGER NOT NULL DEFAULT 0,
  last_paid_ms INTEGER,
  updated_ms INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_life_events (
  id TEXT PRIMARY KEY,
  agent_id TEXT NOT NULL,
  generation INTEGER NOT NULL,
  previous_state TEXT,
  next_state TEXT NOT NULL,
  reason TEXT NOT NULL,
  energy_delta REAL NOT NULL DEFAULT 0,
  created_ms INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_revenue_shares (
  id TEXT PRIMARY KEY,
  charge_id TEXT NOT NULL,
  agent_id TEXT NOT NULL,
  weight REAL NOT NULL,
  amount_usd INTEGER NOT NULL,
  created_ms INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS work_authorizations (
  id TEXT PRIMARY KEY,
  charge_id TEXT NOT NULL UNIQUE,
  client_id TEXT,
  authorized_agents_json TEXT NOT NULL,
  token_hash TEXT NOT NULL UNIQUE,
  expires_ms INTEGER NOT NULL,
  consumed_ms INTEGER,
  created_ms INTEGER NOT NULL
);
