-- Ada Context Core v0.2.0 — Phase 1 reliability foundation
-- Adapted for Neon + PGLite: no extensions, text ids (app supplies UUIDs).

CREATE TABLE IF NOT EXISTS scope_versions (
  scope_type text NOT NULL CHECK (scope_type IN ('global','project','site','task_type','agent','component')),
  scope_id text NOT NULL,
  version bigint NOT NULL DEFAULT 1,
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(scope_type, scope_id)
);

CREATE OR REPLACE FUNCTION ensure_scope_version(p_type text, p_id text) RETURNS bigint AS $$
DECLARE v bigint;
BEGIN
  INSERT INTO scope_versions(scope_type,scope_id,version) VALUES(p_type,p_id,1)
  ON CONFLICT(scope_type,scope_id) DO NOTHING;
  SELECT version INTO v FROM scope_versions WHERE scope_type=p_type AND scope_id=p_id;
  RETURN v;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION bump_scope_version(p_type text, p_id text) RETURNS bigint AS $$
DECLARE v bigint;
BEGIN
  INSERT INTO scope_versions(scope_type,scope_id,version) VALUES(p_type,p_id,2)
  ON CONFLICT(scope_type,scope_id) DO UPDATE SET version=scope_versions.version+1,updated_at=now()
  RETURNING version INTO v;
  RETURN v;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE IF NOT EXISTS memory_records (
  id text PRIMARY KEY,
  canonical_key text NOT NULL,
  record_type text NOT NULL CHECK (record_type IN (
    'GLOBAL_POLICY','PROJECT_POLICY','SITE_POLICY','USER_PREFERENCE','DECISION','FACT','PROCEDURE',
    'BLOCKER','EXAMPLE','RESEARCH_FINDING','EVIDENCE','HYPOTHESIS','HISTORICAL_EVENT','CORRECTION'
  )),
  scope_type text NOT NULL CHECK (scope_type IN ('global','project','site','task_type','agent')),
  scope_id text NOT NULL DEFAULT '*',
  priority smallint NOT NULL CHECK (priority BETWEEN 0 AND 5),
  authority text NOT NULL CHECK (authority IN (
    'user_explicit','verified_system','project_canonical','agent_verified','external_source','agent_inference'
  )),
  provenance text NOT NULL DEFAULT 'CONFIRMED' CHECK (provenance IN (
    'PROPOSED','OBSERVED','CONFIRMED','VERIFIED','TEMPORARY','SUPERSEDING_CANONICAL','DEPRECATED'
  )),
  status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','CANDIDATE','SUPERSEDED','DEPRECATED','ARCHIVED','REJECTED')),
  privacy_class text NOT NULL DEFAULT 'LOCAL_ONLY' CHECK (privacy_class IN ('LOCAL_ONLY','LOCAL_PREFERRED','EXTERNAL_OK')),
  title text NOT NULL,
  content text NOT NULL,
  summary text,
  source_type text,
  source_reference text,
  confidence numeric(4,3) CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
  valid_from timestamptz NOT NULL DEFAULT now(),
  valid_until timestamptz,
  last_verified_at timestamptz,
  supersedes_id text REFERENCES memory_records(id),
  superseded_by text REFERENCES memory_records(id),
  created_by text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  checksum text NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_active_memory_canonical_scope
ON memory_records(canonical_key,scope_type,scope_id)
WHERE status='ACTIVE';
CREATE INDEX IF NOT EXISTS idx_memory_bootstrap ON memory_records(scope_type,scope_id,status,priority,valid_from,valid_until);
CREATE INDEX IF NOT EXISTS idx_memory_updated ON memory_records(updated_at DESC);

CREATE TABLE IF NOT EXISTS memory_versions (
  id bigserial PRIMARY KEY,
  memory_id text NOT NULL REFERENCES memory_records(id) ON DELETE CASCADE,
  version_no integer NOT NULL,
  snapshot jsonb NOT NULL,
  changed_by text NOT NULL,
  change_reason text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(memory_id,version_no)
);

CREATE TABLE IF NOT EXISTS memory_links (
  source_id text NOT NULL REFERENCES memory_records(id) ON DELETE CASCADE,
  target_id text NOT NULL REFERENCES memory_records(id) ON DELETE CASCADE,
  relation text NOT NULL CHECK (relation IN ('SUPPORTS','CONTRADICTS','SUPERSEDES','DEPENDS_ON','EXAMPLE_OF','DERIVED_FROM','RELATED_TO')),
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(source_id,target_id,relation)
);

CREATE TABLE IF NOT EXISTS project_states (
  project_id text NOT NULL,
  lane text NOT NULL DEFAULT 'main',
  objective text,
  verified_status text,
  completed_work jsonb NOT NULL DEFAULT '[]'::jsonb,
  active_decisions jsonb NOT NULL DEFAULT '[]'::jsonb,
  blockers jsonb NOT NULL DEFAULT '[]'::jsonb,
  next_action text,
  active_artifacts jsonb NOT NULL DEFAULT '[]'::jsonb,
  pending_qa jsonb NOT NULL DEFAULT '[]'::jsonb,
  state_version bigint NOT NULL DEFAULT 1,
  updated_by text NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(project_id,lane)
);

CREATE TABLE IF NOT EXISTS policy_releases (
  component text NOT NULL,
  release text NOT NULL,
  content_hash text NOT NULL,
  status text NOT NULL CHECK(status IN ('ACTIVE','SUPERSEDED','CANDIDATE')),
  created_at timestamptz NOT NULL DEFAULT now(),
  activated_at timestamptz,
  PRIMARY KEY(component,release)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_active_policy_release ON policy_releases(component) WHERE status='ACTIVE';

CREATE TABLE IF NOT EXISTS agent_passports (
  id text PRIMARY KEY,
  agent_id text NOT NULL,
  task_type text NOT NULL DEFAULT '*',
  allowed_sites text[] NOT NULL DEFAULT ARRAY[]::text[],
  allowed_tools text[] NOT NULL DEFAULT ARRAY[]::text[],
  allowed_mutation_types text[] NOT NULL DEFAULT ARRAY[]::text[],
  max_batch_size integer NOT NULL DEFAULT 1 CHECK(max_batch_size BETWEEN 1 AND 1000),
  approval_classes text[] NOT NULL DEFAULT ARRAY['DELETE','BULK_WRITE','EXTERNAL_MESSAGE']::text[],
  valid_from timestamptz NOT NULL DEFAULT now(),
  valid_until timestamptz,
  enabled boolean NOT NULL DEFAULT true,
  version bigint NOT NULL DEFAULT 1,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_passport_agent_task ON agent_passports(agent_id,task_type);
CREATE INDEX IF NOT EXISTS idx_passport_agent ON agent_passports(agent_id,task_type,enabled);

CREATE TABLE IF NOT EXISTS tool_registry (
  tool_name text PRIMARY KEY,
  side_effect_class text NOT NULL CHECK(side_effect_class IN ('READ','WRITE','DELETE','EXTERNAL_MESSAGE','POLICY_CHANGE')),
  mutation_type text,
  requires_receipt boolean NOT NULL DEFAULT true,
  requires_snapshot boolean NOT NULL DEFAULT false,
  requires_live_verification boolean NOT NULL DEFAULT false,
  default_decision text NOT NULL DEFAULT 'DENY' CHECK(default_decision IN ('ALLOW','DENY','ESCALATE')),
  enabled boolean NOT NULL DEFAULT true,
  schema_hash text,
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS task_runs (
  id text PRIMARY KEY,
  parent_task_run_id text,
  idempotency_key text NOT NULL UNIQUE,
  task_type text NOT NULL,
  agent_id text NOT NULL,
  project_id text,
  site_id text,
  requested_action text NOT NULL,
  requested_payload_hash text,
  state text NOT NULL CHECK (state IN (
    'QUEUED','CLAIMED','BOOTSTRAPPING','SHADOW','RUNNING','WAITING_APPROVAL','RETRYABLE','FAILED','COMPLETED','ROLLED_BACK','BLOCKED_POLICY'
  )),
  context_receipt_id text,
  lease_owner text,
  lease_until timestamptz,
  attempts integer NOT NULL DEFAULT 0,
  max_attempts integer NOT NULL DEFAULT 3,
  retry_budget integer NOT NULL DEFAULT 3,
  created_at timestamptz NOT NULL DEFAULT now(),
  started_at timestamptz,
  finished_at timestamptz,
  last_error text
);
CREATE INDEX IF NOT EXISTS idx_task_queue ON task_runs(state,created_at);

CREATE TABLE IF NOT EXISTS context_receipts (
  id text PRIMARY KEY,
  agent_id text NOT NULL,
  task_run_id text,
  project_id text,
  site_id text,
  task_type text NOT NULL,
  project_lane text NOT NULL DEFAULT 'main',
  memory_ids text[] NOT NULL DEFAULT ARRAY[]::text[],
  project_state_version bigint,
  qalam_release text,
  qalam_hash text,
  passport_id text REFERENCES agent_passports(id),
  passport_version bigint,
  context_hash text NOT NULL,
  payload_hash text NOT NULL,
  signature_alg text NOT NULL DEFAULT 'HMAC-SHA256',
  key_id text NOT NULL,
  signature text NOT NULL,
  issued_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  revoked_at timestamptz
);

CREATE TABLE IF NOT EXISTS receipt_dependencies (
  receipt_id text NOT NULL REFERENCES context_receipts(id) ON DELETE CASCADE,
  scope_type text NOT NULL,
  scope_id text NOT NULL,
  version bigint NOT NULL,
  PRIMARY KEY(receipt_id,scope_type,scope_id)
);
CREATE INDEX IF NOT EXISTS idx_receipt_dependencies ON receipt_dependencies(scope_type,scope_id,version);

ALTER TABLE task_runs DROP CONSTRAINT IF EXISTS fk_task_parent;
ALTER TABLE task_runs ADD CONSTRAINT fk_task_parent FOREIGN KEY (parent_task_run_id) REFERENCES task_runs(id);
ALTER TABLE task_runs DROP CONSTRAINT IF EXISTS fk_task_context_receipt;
ALTER TABLE task_runs ADD CONSTRAINT fk_task_context_receipt FOREIGN KEY(context_receipt_id) REFERENCES context_receipts(id);

CREATE TABLE IF NOT EXISTS task_events (
  id bigserial PRIMARY KEY,
  task_run_id text NOT NULL REFERENCES task_runs(id) ON DELETE CASCADE,
  event_type text NOT NULL,
  actor text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS snapshots (
  id text PRIMARY KEY,
  task_run_id text REFERENCES task_runs(id),
  site_id text,
  resource_id text,
  storage_ref text NOT NULL,
  snapshot_hash text NOT NULL,
  created_by text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS approval_tickets (
  id text PRIMARY KEY,
  task_run_id text NOT NULL REFERENCES task_runs(id),
  tool_name text NOT NULL REFERENCES tool_registry(tool_name),
  site_id text,
  resource_id text,
  payload_hash text NOT NULL,
  snapshot_hash text,
  context_receipt_id text NOT NULL REFERENCES context_receipts(id),
  dependency_hash text NOT NULL,
  state text NOT NULL DEFAULT 'PENDING' CHECK(state IN ('PENDING','GRANTED','IN_FLIGHT','CONSUMED','DENIED','EXPIRED','REVOKED')),
  requested_by text NOT NULL,
  approved_by text,
  requested_at timestamptz NOT NULL DEFAULT now(),
  decided_at timestamptz,
  expires_at timestamptz NOT NULL,
  consumed_at timestamptz,
  one_time_token_hash text
);
CREATE INDEX IF NOT EXISTS idx_approval_pending ON approval_tickets(state,expires_at);

CREATE TABLE IF NOT EXISTS approval_events (
  id bigserial PRIMARY KEY,
  approval_ticket_id text NOT NULL REFERENCES approval_tickets(id) ON DELETE CASCADE,
  event_type text NOT NULL,
  actor text NOT NULL,
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS mutation_journal (
  id text PRIMARY KEY,
  task_run_id text NOT NULL REFERENCES task_runs(id),
  idempotency_key text NOT NULL UNIQUE,
  tool_name text NOT NULL,
  site_id text,
  resource_id text,
  payload_hash text NOT NULL,
  snapshot_id text REFERENCES snapshots(id),
  expected_postcondition jsonb NOT NULL DEFAULT '{}'::jsonb,
  status text NOT NULL CHECK(status IN ('INTENT_RECORDED','AUTHORIZED','EXECUTING','APPLIED','VERIFIED','FAILED','ROLLED_BACK')),
  external_result_hash text,
  last_error text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS external_inputs (
  id text PRIMARY KEY,
  source_uri text,
  source_kind text NOT NULL,
  trust_class text NOT NULL DEFAULT 'UNTRUSTED_EXTERNAL' CHECK(trust_class IN ('UNTRUSTED_EXTERNAL','USER_PROVIDED','VERIFIED_EXTERNAL')),
  content_hash text NOT NULL,
  content_text text,
  quarantine_status text NOT NULL DEFAULT 'QUARANTINED' CHECK(quarantine_status IN ('QUARANTINED','REVIEWED','REJECTED','PROMOTED_REFERENCE')),
  injection_flags jsonb NOT NULL DEFAULT '[]'::jsonb,
  ingested_by text NOT NULL,
  ingested_at timestamptz NOT NULL DEFAULT now(),
  reviewed_by text,
  reviewed_at timestamptz
);
CREATE INDEX IF NOT EXISTS idx_external_hash ON external_inputs(content_hash);

CREATE TABLE IF NOT EXISTS model_registry (
  model_key text PRIMARY KEY,
  provider_or_family text NOT NULL,
  model_revision text,
  official_model_card_uri text,
  model_card_hash text,
  license_uri text,
  license_hash text,
  status text NOT NULL DEFAULT 'UNVERIFIED_CANDIDATE' CHECK(status IN ('UNVERIFIED_CANDIDATE','BENCHMARKING','APPROVED','CURRENT_WORKER','REJECTED')),
  notes text
);

CREATE TABLE IF NOT EXISTS audit_events (
  id bigserial PRIMARY KEY,
  actor text NOT NULL,
  event_type text NOT NULL,
  task_run_id text,
  resource_type text,
  resource_id text,
  decision text,
  argument_hash text,
  result_status text,
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_events(created_at DESC);

CREATE TABLE IF NOT EXISTS backup_runs (
  id text PRIMARY KEY,
  started_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz,
  backup_kind text NOT NULL CHECK(backup_kind IN ('LOGICAL','WAL_ARCHIVE','RESTORE_DRILL')),
  destination_ref text,
  encrypted boolean NOT NULL DEFAULT true,
  checksum text,
  status text NOT NULL CHECK(status IN ('RUNNING','COMPLETED','FAILED')),
  notes text
);

CREATE TABLE IF NOT EXISTS mirror_events (
  id bigserial PRIMARY KEY,
  memory_id text REFERENCES memory_records(id),
  target text NOT NULL CHECK(target IN ('XMEMO','ENGRAM','OTHER')),
  status text NOT NULL CHECK(status IN ('PENDING','COMPLETED','FAILED','SKIPPED')),
  error text,
  created_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz
);

CREATE OR REPLACE FUNCTION memory_scope_bump() RETURNS trigger AS $$
DECLARE st text; sid text;
BEGIN
  st := COALESCE(NEW.scope_type, OLD.scope_type);
  sid := COALESCE(NEW.scope_id, OLD.scope_id);
  PERFORM bump_scope_version(st,sid);
  RETURN COALESCE(NEW,OLD);
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_memory_scope_bump ON memory_records;
CREATE TRIGGER trg_memory_scope_bump AFTER INSERT OR UPDATE OR DELETE ON memory_records
FOR EACH ROW EXECUTE FUNCTION memory_scope_bump();

CREATE OR REPLACE FUNCTION state_scope_bump() RETURNS trigger AS $$
DECLARE pid text;
BEGIN
  pid := COALESCE(NEW.project_id, OLD.project_id);
  PERFORM bump_scope_version('project',pid);
  RETURN COALESCE(NEW,OLD);
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_state_scope_bump ON project_states;
CREATE TRIGGER trg_state_scope_bump AFTER INSERT OR UPDATE OR DELETE ON project_states
FOR EACH ROW EXECUTE FUNCTION state_scope_bump();

CREATE OR REPLACE FUNCTION policy_scope_bump() RETURNS trigger AS $$
DECLARE comp text;
BEGIN
  comp := COALESCE(NEW.component,OLD.component);
  IF (TG_OP='DELETE') OR (NEW.status='ACTIVE') OR (OLD.status='ACTIVE') THEN
    PERFORM bump_scope_version('component',comp);
  END IF;
  RETURN COALESCE(NEW,OLD);
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_policy_scope_bump ON policy_releases;
CREATE TRIGGER trg_policy_scope_bump AFTER INSERT OR UPDATE OR DELETE ON policy_releases
FOR EACH ROW EXECUTE FUNCTION policy_scope_bump();

SELECT ensure_scope_version('global','*');
