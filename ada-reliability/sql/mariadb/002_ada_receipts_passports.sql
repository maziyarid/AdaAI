CREATE TABLE IF NOT EXISTS ada_policy_releases (
  component VARCHAR(64) NOT NULL,
  release VARCHAR(64) NOT NULL,
  content_hash CHAR(64) NOT NULL,
  status VARCHAR(32) NOT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  activated_at TIMESTAMP(6) NULL,
  PRIMARY KEY (component, release)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_agent_passports (
  id CHAR(36) NOT NULL,
  agent_id VARCHAR(128) NOT NULL,
  task_type VARCHAR(64) NOT NULL DEFAULT '*',
  allowed_sites JSON NOT NULL,
  allowed_tools JSON NOT NULL,
  allowed_page_roles JSON NOT NULL,
  allowed_mutation_types JSON NOT NULL,
  max_batch_size INT NOT NULL DEFAULT 1,
  max_retries INT NOT NULL DEFAULT 3,
  allowed_hours VARCHAR(64) NULL,
  external_communication TINYINT(1) NOT NULL DEFAULT 0,
  deletion_permission TINYINT(1) NOT NULL DEFAULT 0,
  policy_change_permission TINYINT(1) NOT NULL DEFAULT 0,
  approval_mandatory TINYINT(1) NOT NULL DEFAULT 0,
  approval_classes JSON NOT NULL,
  enabled TINYINT(1) NOT NULL DEFAULT 1,
  version BIGINT NOT NULL DEFAULT 1,
  valid_from TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  valid_until TIMESTAMP(6) NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY idx_ada_passport_agent (agent_id, task_type, enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_tool_registry (
  tool_name VARCHAR(128) NOT NULL,
  side_effect_class VARCHAR(32) NOT NULL,
  mutation_type VARCHAR(64) NULL,
  requires_receipt TINYINT(1) NOT NULL DEFAULT 1,
  requires_snapshot TINYINT(1) NOT NULL DEFAULT 0,
  requires_live_verification TINYINT(1) NOT NULL DEFAULT 0,
  default_decision VARCHAR(16) NOT NULL DEFAULT 'DENY',
  enabled TINYINT(1) NOT NULL DEFAULT 1,
  schema_hash CHAR(64) NULL,
  updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (tool_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_context_receipts (
  id CHAR(36) NOT NULL,
  agent_id VARCHAR(128) NOT NULL,
  task_run_id CHAR(36) NULL,
  project_id VARCHAR(191) NULL,
  site_id VARCHAR(191) NULL,
  task_type VARCHAR(64) NOT NULL,
  memory_ids JSON NOT NULL,
  qalam_release VARCHAR(64) NULL,
  qalam_hash CHAR(64) NULL,
  passport_id CHAR(36) NULL,
  context_hash CHAR(64) NOT NULL,
  payload_hash CHAR(64) NOT NULL,
  allowed_mutation_classes JSON NOT NULL,
  signature_alg VARCHAR(32) NOT NULL DEFAULT 'HMAC-SHA256',
  key_id VARCHAR(64) NOT NULL,
  signature VARCHAR(256) NOT NULL,
  issued_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  expires_at TIMESTAMP(6) NOT NULL,
  revoked_at TIMESTAMP(6) NULL,
  PRIMARY KEY (id),
  KEY idx_ada_receipt_task (task_run_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ada_receipt_dependencies (
  receipt_id CHAR(36) NOT NULL,
  scope_type VARCHAR(32) NOT NULL,
  scope_id VARCHAR(191) NOT NULL,
  version BIGINT NOT NULL,
  release_label VARCHAR(64) NULL,
  PRIMARY KEY (receipt_id, scope_type, scope_id),
  KEY idx_ada_dep_scope (scope_type, scope_id, version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
