CREATE TABLE IF NOT EXISTS ada_qalam_assets (
  component VARCHAR(64) NOT NULL,
  `release` VARCHAR(64) NOT NULL,
  path VARCHAR(512) NOT NULL,
  -- Collision-safe identity for paths up to 512 chars. Do not unique-index path(191).
  -- Writers must set path_hash = SHA2(path, 256) of the full path.
  path_hash CHAR(64) NOT NULL,
  content_hash CHAR(64) NOT NULL,
  status VARCHAR(32) NOT NULL,
  site_id VARCHAR(191) NULL,
  bytes INT NOT NULL,
  PRIMARY KEY (component, `release`, path_hash),
  KEY idx_ada_qalam_path_prefix (path(191))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_model_registry (
  model_key VARCHAR(128) NOT NULL,
  provider_or_family VARCHAR(128) NOT NULL,
  model_revision VARCHAR(191) NULL,
  official_model_card_uri TEXT NULL,
  model_card_hash CHAR(64) NULL,
  license_uri TEXT NULL,
  license_hash CHAR(64) NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'UNVERIFIED_CANDIDATE',
  context_length INT NULL,
  modalities JSON NULL,
  language_support JSON NULL,
  tool_call_support TINYINT(1) NULL,
  measured_memory_mb INT NULL,
  measured_latency_ms INT NULL,
  structured_output_failure_rate DECIMAL(6,5) NULL,
  tool_call_success_rate DECIMAL(6,5) NULL,
  fallback_model_key VARCHAR(128) NULL,
  notes TEXT NULL,
  PRIMARY KEY (model_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_eval_traces (
  id CHAR(36) NOT NULL,
  task_run_id CHAR(36) NULL,
  agent_id VARCHAR(128) NOT NULL,
  mode VARCHAR(32) NOT NULL,
  target_correctness TINYINT(1) NULL,
  canonical_correctness TINYINT(1) NULL,
  tool_choice VARCHAR(128) NULL,
  argument_ok TINYINT(1) NULL,
  qalam_compliance TINYINT(1) NULL,
  zwnj_fail TINYINT(1) NULL,
  authorization_decision VARCHAR(16) NULL,
  mutated TINYINT(1) NOT NULL DEFAULT 0,
  payload JSON NOT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_mirror_events (
  id BIGINT NOT NULL AUTO_INCREMENT,
  memory_id CHAR(36) NULL,
  target VARCHAR(32) NOT NULL,
  status VARCHAR(32) NOT NULL,
  error TEXT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  completed_at TIMESTAMP(6) NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_backup_runs (
  id CHAR(36) NOT NULL,
  started_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  completed_at TIMESTAMP(6) NULL,
  backup_kind VARCHAR(32) NOT NULL,
  destination_ref VARCHAR(512) NULL,
  encrypted TINYINT(1) NOT NULL DEFAULT 1,
  checksum CHAR(64) NULL,
  status VARCHAR(32) NOT NULL,
  notes TEXT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_audit_events (
  id BIGINT NOT NULL AUTO_INCREMENT,
  actor VARCHAR(128) NOT NULL,
  event_type VARCHAR(64) NOT NULL,
  decision VARCHAR(32) NULL,
  details JSON NOT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY idx_ada_audit_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
