import { n as TSS_SERVER_FUNCTION, t as createServerFn } from "./ssr.mjs";
import { createHash, createHmac, randomUUID, timingSafeEqual } from "node:crypto";
//#region node_modules/.nitro/vite/services/ssr/assets/server-DbWQZX6b.js
var createServerRpc = (serverFnMeta, splitImportFn) => {
	const url = "/_serverFn/" + serverFnMeta.id;
	return Object.assign(splitImportFn, {
		url,
		serverFnMeta,
		[TSS_SERVER_FUNCTION]: true
	});
};
var _0002_ada_context_core_default = "-- Ada Context Core v0.2.0 — Phase 1 reliability foundation\n-- Adapted for Neon + PGLite: no extensions, text ids (app supplies UUIDs).\n\nCREATE TABLE IF NOT EXISTS scope_versions (\n  scope_type text NOT NULL CHECK (scope_type IN ('global','project','site','task_type','agent','component')),\n  scope_id text NOT NULL,\n  version bigint NOT NULL DEFAULT 1,\n  updated_at timestamptz NOT NULL DEFAULT now(),\n  PRIMARY KEY(scope_type, scope_id)\n);\n\nCREATE OR REPLACE FUNCTION ensure_scope_version(p_type text, p_id text) RETURNS bigint AS $$\nDECLARE v bigint;\nBEGIN\n  INSERT INTO scope_versions(scope_type,scope_id,version) VALUES(p_type,p_id,1)\n  ON CONFLICT(scope_type,scope_id) DO NOTHING;\n  SELECT version INTO v FROM scope_versions WHERE scope_type=p_type AND scope_id=p_id;\n  RETURN v;\nEND;\n$$ LANGUAGE plpgsql;\n\nCREATE OR REPLACE FUNCTION bump_scope_version(p_type text, p_id text) RETURNS bigint AS $$\nDECLARE v bigint;\nBEGIN\n  INSERT INTO scope_versions(scope_type,scope_id,version) VALUES(p_type,p_id,2)\n  ON CONFLICT(scope_type,scope_id) DO UPDATE SET version=scope_versions.version+1,updated_at=now()\n  RETURNING version INTO v;\n  RETURN v;\nEND;\n$$ LANGUAGE plpgsql;\n\nCREATE TABLE IF NOT EXISTS memory_records (\n  id text PRIMARY KEY,\n  canonical_key text NOT NULL,\n  record_type text NOT NULL CHECK (record_type IN (\n    'GLOBAL_POLICY','PROJECT_POLICY','SITE_POLICY','USER_PREFERENCE','DECISION','FACT','PROCEDURE',\n    'BLOCKER','EXAMPLE','RESEARCH_FINDING','EVIDENCE','HYPOTHESIS','HISTORICAL_EVENT','CORRECTION'\n  )),\n  scope_type text NOT NULL CHECK (scope_type IN ('global','project','site','task_type','agent')),\n  scope_id text NOT NULL DEFAULT '*',\n  priority smallint NOT NULL CHECK (priority BETWEEN 0 AND 5),\n  authority text NOT NULL CHECK (authority IN (\n    'user_explicit','verified_system','project_canonical','agent_verified','external_source','agent_inference'\n  )),\n  provenance text NOT NULL DEFAULT 'CONFIRMED' CHECK (provenance IN (\n    'PROPOSED','OBSERVED','CONFIRMED','VERIFIED','TEMPORARY','SUPERSEDING_CANONICAL','DEPRECATED'\n  )),\n  status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','CANDIDATE','SUPERSEDED','DEPRECATED','ARCHIVED','REJECTED')),\n  privacy_class text NOT NULL DEFAULT 'LOCAL_ONLY' CHECK (privacy_class IN ('LOCAL_ONLY','LOCAL_PREFERRED','EXTERNAL_OK')),\n  title text NOT NULL,\n  content text NOT NULL,\n  summary text,\n  source_type text,\n  source_reference text,\n  confidence numeric(4,3) CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),\n  valid_from timestamptz NOT NULL DEFAULT now(),\n  valid_until timestamptz,\n  last_verified_at timestamptz,\n  supersedes_id text REFERENCES memory_records(id),\n  superseded_by text REFERENCES memory_records(id),\n  created_by text NOT NULL,\n  created_at timestamptz NOT NULL DEFAULT now(),\n  updated_at timestamptz NOT NULL DEFAULT now(),\n  checksum text NOT NULL\n);\n\nCREATE UNIQUE INDEX IF NOT EXISTS uq_active_memory_canonical_scope\nON memory_records(canonical_key,scope_type,scope_id)\nWHERE status='ACTIVE';\nCREATE INDEX IF NOT EXISTS idx_memory_bootstrap ON memory_records(scope_type,scope_id,status,priority,valid_from,valid_until);\nCREATE INDEX IF NOT EXISTS idx_memory_updated ON memory_records(updated_at DESC);\n\nCREATE TABLE IF NOT EXISTS memory_versions (\n  id bigserial PRIMARY KEY,\n  memory_id text NOT NULL REFERENCES memory_records(id) ON DELETE CASCADE,\n  version_no integer NOT NULL,\n  snapshot jsonb NOT NULL,\n  changed_by text NOT NULL,\n  change_reason text,\n  created_at timestamptz NOT NULL DEFAULT now(),\n  UNIQUE(memory_id,version_no)\n);\n\nCREATE TABLE IF NOT EXISTS memory_links (\n  source_id text NOT NULL REFERENCES memory_records(id) ON DELETE CASCADE,\n  target_id text NOT NULL REFERENCES memory_records(id) ON DELETE CASCADE,\n  relation text NOT NULL CHECK (relation IN ('SUPPORTS','CONTRADICTS','SUPERSEDES','DEPENDS_ON','EXAMPLE_OF','DERIVED_FROM','RELATED_TO')),\n  created_at timestamptz NOT NULL DEFAULT now(),\n  PRIMARY KEY(source_id,target_id,relation)\n);\n\nCREATE TABLE IF NOT EXISTS project_states (\n  project_id text NOT NULL,\n  lane text NOT NULL DEFAULT 'main',\n  objective text,\n  verified_status text,\n  completed_work jsonb NOT NULL DEFAULT '[]'::jsonb,\n  active_decisions jsonb NOT NULL DEFAULT '[]'::jsonb,\n  blockers jsonb NOT NULL DEFAULT '[]'::jsonb,\n  next_action text,\n  active_artifacts jsonb NOT NULL DEFAULT '[]'::jsonb,\n  pending_qa jsonb NOT NULL DEFAULT '[]'::jsonb,\n  state_version bigint NOT NULL DEFAULT 1,\n  updated_by text NOT NULL,\n  updated_at timestamptz NOT NULL DEFAULT now(),\n  PRIMARY KEY(project_id,lane)\n);\n\nCREATE TABLE IF NOT EXISTS policy_releases (\n  component text NOT NULL,\n  release text NOT NULL,\n  content_hash text NOT NULL,\n  status text NOT NULL CHECK(status IN ('ACTIVE','SUPERSEDED','CANDIDATE')),\n  created_at timestamptz NOT NULL DEFAULT now(),\n  activated_at timestamptz,\n  PRIMARY KEY(component,release)\n);\nCREATE UNIQUE INDEX IF NOT EXISTS uq_active_policy_release ON policy_releases(component) WHERE status='ACTIVE';\n\nCREATE TABLE IF NOT EXISTS agent_passports (\n  id text PRIMARY KEY,\n  agent_id text NOT NULL,\n  task_type text NOT NULL DEFAULT '*',\n  allowed_sites text[] NOT NULL DEFAULT ARRAY[]::text[],\n  allowed_tools text[] NOT NULL DEFAULT ARRAY[]::text[],\n  allowed_mutation_types text[] NOT NULL DEFAULT ARRAY[]::text[],\n  max_batch_size integer NOT NULL DEFAULT 1 CHECK(max_batch_size BETWEEN 1 AND 1000),\n  approval_classes text[] NOT NULL DEFAULT ARRAY['DELETE','BULK_WRITE','EXTERNAL_MESSAGE']::text[],\n  valid_from timestamptz NOT NULL DEFAULT now(),\n  valid_until timestamptz,\n  enabled boolean NOT NULL DEFAULT true,\n  version bigint NOT NULL DEFAULT 1,\n  created_at timestamptz NOT NULL DEFAULT now(),\n  updated_at timestamptz NOT NULL DEFAULT now()\n);\nCREATE UNIQUE INDEX IF NOT EXISTS uq_passport_agent_task ON agent_passports(agent_id,task_type);\nCREATE INDEX IF NOT EXISTS idx_passport_agent ON agent_passports(agent_id,task_type,enabled);\n\nCREATE TABLE IF NOT EXISTS tool_registry (\n  tool_name text PRIMARY KEY,\n  side_effect_class text NOT NULL CHECK(side_effect_class IN ('READ','WRITE','DELETE','EXTERNAL_MESSAGE','POLICY_CHANGE')),\n  mutation_type text,\n  requires_receipt boolean NOT NULL DEFAULT true,\n  requires_snapshot boolean NOT NULL DEFAULT false,\n  requires_live_verification boolean NOT NULL DEFAULT false,\n  default_decision text NOT NULL DEFAULT 'DENY' CHECK(default_decision IN ('ALLOW','DENY','ESCALATE')),\n  enabled boolean NOT NULL DEFAULT true,\n  schema_hash text,\n  updated_at timestamptz NOT NULL DEFAULT now()\n);\n\nCREATE TABLE IF NOT EXISTS task_runs (\n  id text PRIMARY KEY,\n  parent_task_run_id text,\n  idempotency_key text NOT NULL UNIQUE,\n  task_type text NOT NULL,\n  agent_id text NOT NULL,\n  project_id text,\n  site_id text,\n  requested_action text NOT NULL,\n  requested_payload_hash text,\n  state text NOT NULL CHECK (state IN (\n    'QUEUED','CLAIMED','BOOTSTRAPPING','SHADOW','RUNNING','WAITING_APPROVAL','RETRYABLE','FAILED','COMPLETED','ROLLED_BACK','BLOCKED_POLICY'\n  )),\n  context_receipt_id text,\n  lease_owner text,\n  lease_until timestamptz,\n  attempts integer NOT NULL DEFAULT 0,\n  max_attempts integer NOT NULL DEFAULT 3,\n  retry_budget integer NOT NULL DEFAULT 3,\n  created_at timestamptz NOT NULL DEFAULT now(),\n  started_at timestamptz,\n  finished_at timestamptz,\n  last_error text\n);\nCREATE INDEX IF NOT EXISTS idx_task_queue ON task_runs(state,created_at);\n\nCREATE TABLE IF NOT EXISTS context_receipts (\n  id text PRIMARY KEY,\n  agent_id text NOT NULL,\n  task_run_id text,\n  project_id text,\n  site_id text,\n  task_type text NOT NULL,\n  project_lane text NOT NULL DEFAULT 'main',\n  memory_ids text[] NOT NULL DEFAULT ARRAY[]::text[],\n  project_state_version bigint,\n  qalam_release text,\n  qalam_hash text,\n  passport_id text REFERENCES agent_passports(id),\n  passport_version bigint,\n  context_hash text NOT NULL,\n  payload_hash text NOT NULL,\n  signature_alg text NOT NULL DEFAULT 'HMAC-SHA256',\n  key_id text NOT NULL,\n  signature text NOT NULL,\n  issued_at timestamptz NOT NULL DEFAULT now(),\n  expires_at timestamptz NOT NULL,\n  revoked_at timestamptz\n);\n\nCREATE TABLE IF NOT EXISTS receipt_dependencies (\n  receipt_id text NOT NULL REFERENCES context_receipts(id) ON DELETE CASCADE,\n  scope_type text NOT NULL,\n  scope_id text NOT NULL,\n  version bigint NOT NULL,\n  PRIMARY KEY(receipt_id,scope_type,scope_id)\n);\nCREATE INDEX IF NOT EXISTS idx_receipt_dependencies ON receipt_dependencies(scope_type,scope_id,version);\n\nALTER TABLE task_runs DROP CONSTRAINT IF EXISTS fk_task_parent;\nALTER TABLE task_runs ADD CONSTRAINT fk_task_parent FOREIGN KEY (parent_task_run_id) REFERENCES task_runs(id);\nALTER TABLE task_runs DROP CONSTRAINT IF EXISTS fk_task_context_receipt;\nALTER TABLE task_runs ADD CONSTRAINT fk_task_context_receipt FOREIGN KEY(context_receipt_id) REFERENCES context_receipts(id);\n\nCREATE TABLE IF NOT EXISTS task_events (\n  id bigserial PRIMARY KEY,\n  task_run_id text NOT NULL REFERENCES task_runs(id) ON DELETE CASCADE,\n  event_type text NOT NULL,\n  actor text NOT NULL,\n  payload jsonb NOT NULL DEFAULT '{}'::jsonb,\n  created_at timestamptz NOT NULL DEFAULT now()\n);\n\nCREATE TABLE IF NOT EXISTS snapshots (\n  id text PRIMARY KEY,\n  task_run_id text REFERENCES task_runs(id),\n  site_id text,\n  resource_id text,\n  storage_ref text NOT NULL,\n  snapshot_hash text NOT NULL,\n  created_by text NOT NULL,\n  created_at timestamptz NOT NULL DEFAULT now()\n);\n\nCREATE TABLE IF NOT EXISTS approval_tickets (\n  id text PRIMARY KEY,\n  task_run_id text NOT NULL REFERENCES task_runs(id),\n  tool_name text NOT NULL REFERENCES tool_registry(tool_name),\n  site_id text,\n  resource_id text,\n  payload_hash text NOT NULL,\n  snapshot_hash text,\n  context_receipt_id text NOT NULL REFERENCES context_receipts(id),\n  dependency_hash text NOT NULL,\n  state text NOT NULL DEFAULT 'PENDING' CHECK(state IN ('PENDING','GRANTED','IN_FLIGHT','CONSUMED','DENIED','EXPIRED','REVOKED')),\n  requested_by text NOT NULL,\n  approved_by text,\n  requested_at timestamptz NOT NULL DEFAULT now(),\n  decided_at timestamptz,\n  expires_at timestamptz NOT NULL,\n  consumed_at timestamptz,\n  one_time_token_hash text\n);\nCREATE INDEX IF NOT EXISTS idx_approval_pending ON approval_tickets(state,expires_at);\n\nCREATE TABLE IF NOT EXISTS approval_events (\n  id bigserial PRIMARY KEY,\n  approval_ticket_id text NOT NULL REFERENCES approval_tickets(id) ON DELETE CASCADE,\n  event_type text NOT NULL,\n  actor text NOT NULL,\n  details jsonb NOT NULL DEFAULT '{}'::jsonb,\n  created_at timestamptz NOT NULL DEFAULT now()\n);\n\nCREATE TABLE IF NOT EXISTS mutation_journal (\n  id text PRIMARY KEY,\n  task_run_id text NOT NULL REFERENCES task_runs(id),\n  idempotency_key text NOT NULL UNIQUE,\n  tool_name text NOT NULL,\n  site_id text,\n  resource_id text,\n  payload_hash text NOT NULL,\n  snapshot_id text REFERENCES snapshots(id),\n  expected_postcondition jsonb NOT NULL DEFAULT '{}'::jsonb,\n  status text NOT NULL CHECK(status IN ('INTENT_RECORDED','AUTHORIZED','EXECUTING','APPLIED','VERIFIED','FAILED','ROLLED_BACK')),\n  external_result_hash text,\n  last_error text,\n  created_at timestamptz NOT NULL DEFAULT now(),\n  updated_at timestamptz NOT NULL DEFAULT now()\n);\n\nCREATE TABLE IF NOT EXISTS external_inputs (\n  id text PRIMARY KEY,\n  source_uri text,\n  source_kind text NOT NULL,\n  trust_class text NOT NULL DEFAULT 'UNTRUSTED_EXTERNAL' CHECK(trust_class IN ('UNTRUSTED_EXTERNAL','USER_PROVIDED','VERIFIED_EXTERNAL')),\n  content_hash text NOT NULL,\n  content_text text,\n  quarantine_status text NOT NULL DEFAULT 'QUARANTINED' CHECK(quarantine_status IN ('QUARANTINED','REVIEWED','REJECTED','PROMOTED_REFERENCE')),\n  injection_flags jsonb NOT NULL DEFAULT '[]'::jsonb,\n  ingested_by text NOT NULL,\n  ingested_at timestamptz NOT NULL DEFAULT now(),\n  reviewed_by text,\n  reviewed_at timestamptz\n);\nCREATE INDEX IF NOT EXISTS idx_external_hash ON external_inputs(content_hash);\n\nCREATE TABLE IF NOT EXISTS model_registry (\n  model_key text PRIMARY KEY,\n  provider_or_family text NOT NULL,\n  model_revision text,\n  official_model_card_uri text,\n  model_card_hash text,\n  license_uri text,\n  license_hash text,\n  status text NOT NULL DEFAULT 'UNVERIFIED_CANDIDATE' CHECK(status IN ('UNVERIFIED_CANDIDATE','BENCHMARKING','APPROVED','CURRENT_WORKER','REJECTED')),\n  notes text\n);\n\nCREATE TABLE IF NOT EXISTS audit_events (\n  id bigserial PRIMARY KEY,\n  actor text NOT NULL,\n  event_type text NOT NULL,\n  task_run_id text,\n  resource_type text,\n  resource_id text,\n  decision text,\n  argument_hash text,\n  result_status text,\n  details jsonb NOT NULL DEFAULT '{}'::jsonb,\n  created_at timestamptz NOT NULL DEFAULT now()\n);\nCREATE INDEX IF NOT EXISTS idx_audit_created ON audit_events(created_at DESC);\n\nCREATE TABLE IF NOT EXISTS backup_runs (\n  id text PRIMARY KEY,\n  started_at timestamptz NOT NULL DEFAULT now(),\n  completed_at timestamptz,\n  backup_kind text NOT NULL CHECK(backup_kind IN ('LOGICAL','WAL_ARCHIVE','RESTORE_DRILL')),\n  destination_ref text,\n  encrypted boolean NOT NULL DEFAULT true,\n  checksum text,\n  status text NOT NULL CHECK(status IN ('RUNNING','COMPLETED','FAILED')),\n  notes text\n);\n\nCREATE TABLE IF NOT EXISTS mirror_events (\n  id bigserial PRIMARY KEY,\n  memory_id text REFERENCES memory_records(id),\n  target text NOT NULL CHECK(target IN ('XMEMO','ENGRAM','OTHER')),\n  status text NOT NULL CHECK(status IN ('PENDING','COMPLETED','FAILED','SKIPPED')),\n  error text,\n  created_at timestamptz NOT NULL DEFAULT now(),\n  completed_at timestamptz\n);\n\nCREATE OR REPLACE FUNCTION memory_scope_bump() RETURNS trigger AS $$\nDECLARE st text; sid text;\nBEGIN\n  st := COALESCE(NEW.scope_type, OLD.scope_type);\n  sid := COALESCE(NEW.scope_id, OLD.scope_id);\n  PERFORM bump_scope_version(st,sid);\n  RETURN COALESCE(NEW,OLD);\nEND;\n$$ LANGUAGE plpgsql;\nDROP TRIGGER IF EXISTS trg_memory_scope_bump ON memory_records;\nCREATE TRIGGER trg_memory_scope_bump AFTER INSERT OR UPDATE OR DELETE ON memory_records\nFOR EACH ROW EXECUTE FUNCTION memory_scope_bump();\n\nCREATE OR REPLACE FUNCTION state_scope_bump() RETURNS trigger AS $$\nDECLARE pid text;\nBEGIN\n  pid := COALESCE(NEW.project_id, OLD.project_id);\n  PERFORM bump_scope_version('project',pid);\n  RETURN COALESCE(NEW,OLD);\nEND;\n$$ LANGUAGE plpgsql;\nDROP TRIGGER IF EXISTS trg_state_scope_bump ON project_states;\nCREATE TRIGGER trg_state_scope_bump AFTER INSERT OR UPDATE OR DELETE ON project_states\nFOR EACH ROW EXECUTE FUNCTION state_scope_bump();\n\nCREATE OR REPLACE FUNCTION policy_scope_bump() RETURNS trigger AS $$\nDECLARE comp text;\nBEGIN\n  comp := COALESCE(NEW.component,OLD.component);\n  IF (TG_OP='DELETE') OR (NEW.status='ACTIVE') OR (OLD.status='ACTIVE') THEN\n    PERFORM bump_scope_version('component',comp);\n  END IF;\n  RETURN COALESCE(NEW,OLD);\nEND;\n$$ LANGUAGE plpgsql;\nDROP TRIGGER IF EXISTS trg_policy_scope_bump ON policy_releases;\nCREATE TRIGGER trg_policy_scope_bump AFTER INSERT OR UPDATE OR DELETE ON policy_releases\nFOR EACH ROW EXECUTE FUNCTION policy_scope_bump();\n\nSELECT ensure_scope_version('global','*');\n";
/**
* Migration bookkeeping shared by the two appliers — `scripts/migrate.mjs`
* (deploy, `readdir`) and `src/lib/db.ts` (PGLite preview, `import.meta.glob`).
*
* Applied files are keyed by BASENAME, so the same file applies once no matter
* which directory it is globbed from. That is what makes the auth schema safe to
* copy from `migrations/auth/` into `migrations/` when an app turns sign-in on:
* a database that already has `0001_auth.sql` will not re-run it.
*
* Neither applier descends into subdirectories, so `migrations/auth/*.sql` is
* out of scope for both until it is copied up.
*/
/**
* The `_migrations` key for a migration path (or bare filename).
* @param {string} path
* @returns {string}
*/
function migrationName(path) {
	return path.split("/").pop() ?? path;
}
/**
* @param {string} path
* @returns {boolean}
*/
function isMigrationFile(path) {
	return path.endsWith(".sql");
}
/**
* Migrations in `paths` that are not yet in `applied`, in apply order.
* Non-`.sql` entries (a `readdir` also yields `migrations/auth/`) are dropped.
* @param {Iterable<string>} paths
* @param {Iterable<string>} applied
* @returns {Array<{ name: string, path: string }>}
*/
function pendingMigrations(paths, applied) {
	const done = new Set(applied);
	return [...paths].filter(isMigrationFile).map((path) => ({
		name: migrationName(path),
		path
	})).sort((a, b) => a.name.localeCompare(b.name)).filter(({ name }) => !done.has(name));
}
var rawDatabaseUrl = typeof process !== "undefined" ? process.env.DATABASE_URL : void 0;
var databaseUrl = rawDatabaseUrl && rawDatabaseUrl.trim() ? rawDatabaseUrl : void 0;
/**
* Active backend: real **Neon** when `DATABASE_URL` is set (deployed / configured
* sandbox), otherwise a local embedded **PGLite** (Postgres compiled to WASM) so
* the app has a working database even with nothing configured — the live preview
* included. Swap in Neon later by just setting `DATABASE_URL`; no code changes.
*/
var dbSource = databaseUrl ? "neon" : "pglite";
/**
* Init state lives on globalThis as promises: dev HMR creates new instances of
* this module, and two instances racing module-level state would open a second
* pool or run two concurrent PGLite migration passes (whose duplicate
* `_migrations` insert rejects — and would get memoized, poisoning every later
* `getSql()`). A failed init clears its slot so the next call retries.
*/
var globalRef = globalThis;
/**
* Result-type parity: Postgres sends every value as text plus a type OID — the
* JS value is the DRIVER's parsing choice, and pg and PGLite disagree (pg:
* int8 -> string, date -> local-midnight Date; PGLite: int8 -> BigInt, which
* JSON.stringify rejects, date -> UTC Date). Normalize both so preview and
* production return identical, JSON-safe shapes:
*   int8/bigint (incl. count(*)) -> number (past 2^53 loses precision — cast
*                                   `::text` if you ever need huge integers)
*   date                         -> 'YYYY-MM-DD' string
*   interval                     -> Postgres interval text
* numeric already comes back as a string on both (arbitrary precision).
*/
var OID_INT8 = 20;
var OID_DATE = 1082;
var OID_INTERVAL = 1186;
var identity = (v) => v;
/** Wrap a query runner in the tagged-template + `.query()` `Sql` surface. */
function toSql(run) {
	const sql = (async (strings, ...values) => {
		let text = strings[0];
		for (let i = 0; i < values.length; i += 1) text += `$${i + 1}${strings[i + 1]}`;
		return run(text, values);
	});
	sql.query = (text, params = []) => run(text, params);
	return sql;
}
function createNeonSql() {
	globalRef.__pgSqlPromise__ ??= (async () => {
		const { Pool, types } = await import("../_libs/pg.mjs").then((n) => n.t);
		types.setTypeParser(OID_INT8, Number);
		types.setTypeParser(OID_DATE, identity);
		types.setTypeParser(OID_INTERVAL, identity);
		const pool = new Pool({ connectionString: databaseUrl });
		return toSql(async (text, params) => {
			return (await pool.query(text, params)).rows;
		});
	})().catch((err) => {
		globalRef.__pgSqlPromise__ = void 0;
		throw err;
	});
	return globalRef.__pgSqlPromise__;
}
async function createPgliteSql() {
	globalRef.__pgliteInstance__ ??= (async () => {
		const { PGlite } = await import("../_libs/electric-sql__pglite.mjs").then((n) => n.t);
		const pg = new PGlite({ parsers: {
			[OID_INT8]: Number,
			[OID_DATE]: identity,
			[OID_INTERVAL]: identity
		} });
		await pg.waitReady;
		await pg.exec("create table if not exists _migrations (name text primary key, applied_at timestamptz not null default now())");
		return pg;
	})().catch((err) => {
		globalRef.__pgliteInstance__ = void 0;
		throw err;
	});
	const pg = await globalRef.__pgliteInstance__;
	const migrate = async () => {
		const migrations = /* #__PURE__ */ Object.assign({ "/migrations/0002_ada_context_core.sql": _0002_ada_context_core_default });
		const done = (await pg.query("select name from _migrations")).rows.map((r) => r.name);
		for (const { name, path } of pendingMigrations(Object.keys(migrations), done)) await pg.transaction(async (tx) => {
			await tx.exec(migrations[path]);
			await tx.query("insert into _migrations (name) values ($1)", [name]);
		});
	};
	const pass = (globalRef.__pgliteMigrateChain__ ?? Promise.resolve()).catch(() => void 0).then(migrate);
	globalRef.__pgliteMigrateChain__ = pass;
	await pass;
	return toSql(async (text, params) => {
		return (await pg.query(text, params)).rows;
	});
}
var sqlPromise = null;
async function createSql() {
	if (typeof window !== "undefined") throw new Error("@/lib/db is server-only — call getSql() from a createServerFn handler or a server route loader, never from client code.");
	return dbSource === "neon" ? createNeonSql() : createPgliteSql();
}
/**
* Get the shared, **server-only** SQL client. Neon when `DATABASE_URL` is set,
* otherwise the local PGLite fallback. Memoized — safe to call per request.
*
* Schema comes from `migrations/*.sql`, auto-applied before the first query on
* both backends — define tables there, never inline in server functions.
*/
function getSql() {
	sqlPromise ??= createSql().catch((err) => {
		sqlPromise = null;
		throw err;
	});
	return sqlPromise;
}
/**
* Finish DB bootstrap before the server handles traffic.
*
* - **PGLite** (preview / no `DATABASE_URL`): open the in-memory DB and apply
*   `migrations/*.sql`. Idempotent — concurrent callers share one promise.
* - **Neon**: no-op (pool is created lazily on first query).
*
* Vite `configureServer` awaits this at dev startup; production imports of this
* module kick it off immediately (see bottom of file).
*/
function ensureDbReady() {
	if (dbSource !== "pglite") return Promise.resolve();
	return getSql().then(() => void 0);
}
var globalBoot = globalThis;
if (typeof window === "undefined" && dbSource === "pglite") globalBoot.__pgBootstrapPromise__ ??= ensureDbReady().catch((err) => {
	globalBoot.__pgBootstrapPromise__ = void 0;
	console.error("[db] PGLite bootstrap failed:", err);
	throw err;
});
/** Preview-only HMAC. Production must set ADA_RECEIPT_HMAC_KEY (≥32 chars). Never write a .env. */
var PREVIEW_HMAC$1 = "ada-preview-hmac-key-not-for-production-use!";
var RECEIPT_KEY_ID = process.env.ADA_RECEIPT_KEY_ID ?? "internal-hmac";
var RECEIPT_TTL_SECONDS = Number(process.env.ADA_RECEIPT_TTL_SECONDS ?? "900");
function receiptHmacKey() {
	const env = process.env.ADA_RECEIPT_HMAC_KEY?.trim();
	return env && env.length >= 32 ? env : PREVIEW_HMAC$1;
}
function newId() {
	return randomUUID();
}
function canonicalJson(obj) {
	return JSON.stringify(sortValue(obj));
}
function sortValue(v) {
	if (v === null || typeof v !== "object") return v;
	if (Array.isArray(v)) return v.map(sortValue);
	const o = v;
	const out = {};
	for (const k of Object.keys(o).sort()) out[k] = sortValue(o[k]);
	return out;
}
function sha256Text(text) {
	return createHash("sha256").update(text).digest("hex");
}
function sha256Obj(obj) {
	return sha256Text(canonicalJson(obj));
}
function hmacSign(payload) {
	return createHmac("sha256", receiptHmacKey()).update(canonicalJson(payload)).digest("hex");
}
function hmacVerify(payload, signature) {
	const expected = Buffer.from(hmacSign(payload), "hex");
	const got = Buffer.from(signature, "hex");
	if (expected.length !== got.length) return false;
	return timingSafeEqual(expected, got);
}
function receiptTtlMs() {
	return RECEIPT_TTL_SECONDS * 1e3;
}
/** Floor to seconds so timestamptz round-trips through PGLite/Neon. */
function toIsoSeconds(v) {
	const d = v instanceof Date ? v : new Date(v);
	return (/* @__PURE__ */ new Date(Math.floor(d.getTime() / 1e3) * 1e3)).toISOString();
}
var MEMORIES = [
	{
		id: "aaaaaaaa-0001-4000-8000-000000000001",
		canonical_key: "writing.os.precedence",
		record_type: "GLOBAL_POLICY",
		scope_type: "global",
		scope_id: "*",
		priority: 0,
		authority: "user_explicit",
		title: "ترتیب تعارض نگارش",
		content: "ایمنی و حقیقت > دستور فعلی کاربر > نیاز حوزه > سیاست سایت > قرارداد ژانر > کتابچه نگارش ایرانی > سئو > تزئین. سبک حقیقت را باطل نمی کند. Teznevise ممنوعیت U+200C قاعده سایت است نه قاعده فارسی.",
		summary: "حقیقت بالاتر از سبک.",
		source_reference: "art-of-writing-bible v2.0"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-000000000002",
		canonical_key: "writing.think-in-persian",
		record_type: "PROCEDURE",
		scope_type: "global",
		scope_id: "*",
		priority: 0,
		authority: "user_explicit",
		title: "فکر به فارسی ایرانی",
		content: "قبل از نوشتن، استدلال را به فارسی ایرانی بسازید نه به انگلیسی و بعد ترجمه. ترتیب اطلاع فارسی: معلوم/دامنه سپس تازه سپس فعل. جمله را از معنا بازنویسی کنید نه از نحو مبدأ. اگر متن بوی ترجمه دارد، از نقطه شروع کنید نه از واژگان.",
		summary: "ترجمه فکر ممنوع.",
		source_reference: "art-of-writing-bible v2.0 §think"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-000000000003",
		canonical_key: "writing.iranian-not-dari",
		record_type: "GLOBAL_POLICY",
		scope_type: "global",
		scope_id: "*",
		priority: 0,
		authority: "user_explicit",
		title: "فارسی ایرانی نه دری افغانستان",
		content: "مخاطب ایران است. واژگان دری را قاطی نکنید: پوهنتون≠دانشگاه، شفاخانه≠بیمارستان، موتر≠خودرو/ماشین، دریور≠راننده، لیسه≠دبیرستان، محصل به جای دانشجو در نثر وب ایرانی. ی و ک فارسی (ی ک) نه ي ك عربی. copula پیش فرض است/هست نه می باشم. قاطی کردن گویش خواننده را از ادامه متن دلسرد می کند. این قاعده همه سطوح است نه فقط دانشگاهی.",
		summary: "یک زبان بازار: فارسی ایرانی.",
		source_reference: "iranian-dari.md"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-000000000004",
		canonical_key: "writing.registers.do-not-blend",
		record_type: "PROCEDURE",
		scope_type: "global",
		scope_id: "*",
		priority: 0,
		authority: "project_canonical",
		title: "رجیستر را قاطی نکنید",
		content: "مصنوع را نام ببرید سپس یک رجیستر. مجله+کافه، خدمت+می باشد، راهنما+سه سوت، پزشکی بیمار+چکیده علمی، لندینگ+راز طلایی: در یک بند ممنوع. FAQ می تواند چطور/فرقش چیه بپرسد؛ بدن صفحه دانشگاه نما impersonal می ماند. لندینگ کار را می گوید نه اکوسیستم را.",
		summary: "یک مصنوع، یک رجیستر.",
		source_reference: "slices A D E F + Bible"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-000000000005",
		canonical_key: "writing.anti-clone-anti-detector",
		record_type: "GLOBAL_POLICY",
		scope_type: "global",
		scope_id: "*",
		priority: 0,
		authority: "user_explicit",
		title: "تقلید صدا و حقه آشکارساز ممنوع",
		content: "قواعد را استخراج کنید. صدای آشوری، نجفی، صلح جو، سمیعی، بابایی، فتوحی، امانی، معصومی، نادری، سلطان زاده را شبیه سازی نکنید. ترکیدن مصنوعی، غلط عمدی، عامیانه استتار، چرخش مترادف برای آمار: ممنوع. تعمیر محتوا است نه استتار.",
		summary: "مکانیک بله؛ اثر انگشت نه.",
		source_reference: "Bible §15 + Slice E F24"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-000000000006",
		canonical_key: "writing.cut-list",
		record_type: "GLOBAL_POLICY",
		scope_type: "global",
		scope_id: "*",
		priority: 0,
		authority: "project_canonical",
		title: "برش پیش فرض",
		content: "در دنیای امروز؛ در این مقاله قصد داریم؛ همه چیز درباره؛ از صفر تا صد؛ با ما همراه باشید؛ می باشد/می گردد/می نماید مگر نقل آیین نامه؛ شکاف ساختگی این است که؛ نقش بازی کردن؛ پشته قدرتمند/جامع/یکپارچه؛ تضمینی؛ ظرفیت محدود؛ سه سوت؛ راز طلایی؛ ویراستاری فوری؛ انجام پایان نامه به عنوان پیشنهاد شبح نویسی؛ قلب تپنده؛ سخن آخر اجباری. ایجاز و سادگی بر زیبانویسی علمی مقدم است.",
		summary: "کالای نثر را ببرید.",
		source_reference: "A+D+E+Bible+medical"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-000000000007",
		canonical_key: "writing.academic.imrad",
		record_type: "PROCEDURE",
		scope_type: "task_type",
		scope_id: "academic_content",
		priority: 1,
		authority: "project_canonical",
		title: "نثر علمی پژوهشی",
		content: "پژوهش حاضر/نگارنده نه من. چکیده: هدف روش یافته نتیجه. روش: مجهول گذشته بدون عامل + منبع داده نمونه فن ابزار. یافته خاص گذشته، تعمیم حال. افعال گزارش: نشان می دهد تبیین می کند استدلال می کند. مورد بررسی قرار گرفت در این رجیستر بومی است؛ انباشته نکنید. Hedging برای استنتاج نه تعریف. تیتر گروه اسمی کوتاه.",
		summary: "Overlay دانشگاهی.",
		source_reference: "slice A + overlays.md"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-000000000008",
		canonical_key: "writing.editorial.craft",
		record_type: "PROCEDURE",
		scope_type: "task_type",
		scope_id: "editorial",
		priority: 1,
		authority: "project_canonical",
		title: "نثر ویرایشی",
		content: "زبان معیار هدف است. لایه ها: زبانی فنی استنادی پساویرایش. می باشد به است. ویرگول نهاد/گزاره نه. شکاف این است که گرته است. علمی=پیراستگی نه آراستگی. بی عیبی بی نقصی نیست. سنجه بابایی: کهن دستور گفتار نوشتار روز نه فهرست ۱۳۶۶ منجمد. منشیانه را ببرید. ویراستاری فوری ضدالگوست. صدای سمیعی/صلح جو را کلون نکنید.",
		summary: "Slice E.",
		source_reference: "research-slice-E"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-000000000009",
		canonical_key: "writing.telegram.reader-not-body",
		record_type: "PROCEDURE",
		scope_type: "task_type",
		scope_id: "web_content",
		priority: 1,
		authority: "project_canonical",
		title: "تلگرام منبع پرسش است نه بدن صفحه",
		content: "چیه/چطور/شما در FAQ مجاز. بدن صفحه را impersonal و SOV کنید. ایموجی ساختار تیتر نیست. هشتگ را به واژه تیتر تبدیل کنید. کانال معلم شتاب (سه سوت، ۳۰ ثانیه) و شبح نویسی و لایسنس غیرقانونی مدل نیستند. کانال حرفه ای محتاط (معصومی) را با ریتم فروش قاطی نکنید — آن قاطی نشانه مدل است. آینه بله/ایتا/اینستا یک صدایند.",
		summary: "Slice D.",
		source_reference: "research-slice-D"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-00000000000a",
		canonical_key: "writing.landing.product",
		record_type: "PROCEDURE",
		scope_type: "task_type",
		scope_id: "landing_product",
		priority: 1,
		authority: "project_canonical",
		title: "لندینگ و محصول",
		content: "کار کاربر در اولین صفحه. دکمه نام عمل است نه شروع کنید. خطای فرم فیلد را نام می برد. خالی و ۴۰۴ راه بعدی می دهند. بدون پاپ شمارش معکوس. تضمین نمره/نتیجه ممنوع. زبان بازار ایران: فارسی معیار خواندنی نه کانتنت و کپی رایتینگ به عنوان تیتر. ارزش غیرکالایی: محدوده حد فرایند شاهد. طول کلمه حکمرانی نیست.",
		summary: "محصول + خدمت.",
		source_reference: "helpfulness + Bible service"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-00000000000b",
		canonical_key: "writing.medical.patient",
		record_type: "PROCEDURE",
		scope_type: "task_type",
		scope_id: "medical_clinic",
		priority: 1,
		authority: "project_canonical",
		title: "صفحه بیمار ایرانی",
		content: "ایمنی پزشکی بالاتر از لحن و سئو. بدون تضمین بدون عارضه بدون بهترین جراح. جغرافیا ایرانی (۱۱۵ نه ۹۱۱). کالک Mayo را اسکلت نکنید. زیباجو پیش فرض نیست. می باشد در صفحه بیمار نه. ادعا را طبقه بندی کنید: ثابت، وابسته به فرد، سیاست کلینیک.",
		summary: "پزشکی جدا از پایان نامه.",
		source_reference: "persian-medical-human-writing"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-00000000000c",
		canonical_key: "writing.teznevise.zwnj",
		record_type: "SITE_POLICY",
		scope_type: "site",
		scope_id: "teznevise.ir",
		priority: 0,
		authority: "project_canonical",
		title: "Teznevise بدون ZWNJ",
		content: "در محتوای منتشرشده teznevise.ir نویسه U+200C ممنوع است. فاصله معمولی یا اتصال کامل. این قاعده خانه است. فارسی معیار دانشگاهی غالبا نیم فاصله دارد؛ آن واقعیت زبان است نه مجوز نقض سیاست سایت.",
		summary: "خانه ≠ زبان.",
		source_reference: "Teznevise site policy"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-00000000000d",
		canonical_key: "ada.memory.contract",
		record_type: "PROCEDURE",
		scope_type: "global",
		scope_id: "*",
		priority: 0,
		authority: "verified_system",
		title: "قرارداد حافظه Ada",
		content: "هیچ کار پیامدی بدون رسید زمینه که حافظه اجباری P0/P1 همان دامنه را ثابت کند آغاز نمی شود. بازیابی معنایی جایگزین لایه قطعی نیست. متن اسکرپ خودکار سیاست نمی شود. XMemo/Engram آینه اند نه حقیقت.",
		summary: "قطعیت قبل از شباهت.",
		source_reference: "Ada MEMORY-CONTRACT v0.2.0"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-00000000000e",
		canonical_key: "ada.execution.contract",
		record_type: "PROCEDURE",
		scope_type: "global",
		scope_id: "*",
		priority: 0,
		authority: "verified_system",
		title: "قرارداد اجرا",
		content: "مدل پیشنهاد می دهد؛ کد تصمیم می گیرد. جهش: رسید تازه، گذرنامه، ابزار مجاز، ژورنال با کلید تکرارناپذیر، در صورت نیاز بلیت تصویب با هش بار و اسنپ شات. ادعای مدل که منتشر شد شاهد نیست.",
		summary: "اجازه جدا از پیشنهاد.",
		source_reference: "Ada EXECUTION-CONTRACT v0.2.0"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-00000000000f",
		canonical_key: "ada.external.quarantine",
		record_type: "GLOBAL_POLICY",
		scope_type: "global",
		scope_id: "*",
		priority: 0,
		authority: "verified_system",
		title: "قرنطینه ورودی بیرونی",
		content: "متن اسکرپ و خبر صنعت UNTRUSTED_EXTERNAL است. قرنطینه تا بازبینی. حق ارتقای خودکار به سیاست کاننیکال ندارد. تیتر سئو وارد دستور نگارش تولید نمی شود.",
		summary: "اسکرپ ≠ قانون.",
		source_reference: "Ada v0.2.0"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-000000000010",
		canonical_key: "writing.ux.microcopy",
		record_type: "PROCEDURE",
		scope_type: "task_type",
		scope_id: "ux_microcopy",
		priority: 1,
		authority: "project_canonical",
		title: "ریزمتن رابط",
		content: "دکمه نام عمل است. خطا فیلد را نام می برد نه مقدار نامعتبر. خالی و ۴۰۴ راه بعدی دارند. بدون کاربران عزیز و ایموجی ساختار. نام نرم افزار لاتین. متن کارمند عملیاتی است نه شناسه داخلی.",
		summary: "ریزمتن بالغ.",
		source_reference: "landing-product-ux.md"
	},
	{
		id: "aaaaaaaa-0001-4000-8000-000000000011",
		canonical_key: "writing.student.faq",
		record_type: "PROCEDURE",
		scope_type: "task_type",
		scope_id: "student_faq",
		priority: 1,
		authority: "project_canonical",
		title: "پرسش متداول دانشجو",
		content: "چطور و فرقش چیه و شما در FAQ مجاز است. بدن مقاله دانشگاه نما با چیه نوشته نمی شود. پرسش دانشجو را به حرکت علمی برگردانید: فرمت به شیوه‌نامه، درصد همانندی به استناد، ایده به بیان مسئله. سه سوت و شبح نویسی مدل نیستند.",
		summary: "FAQ ≠ بدن صفحه.",
		source_reference: "research-slice-D"
	}
];
async function ensureAdaSeed(sql) {
	await sql.query(`SELECT ensure_scope_version($1,$2)`, ["global", "*"]);
	await sql.query(`SELECT ensure_scope_version($1,$2)`, ["project", "qalam"]);
	await sql.query(`SELECT ensure_scope_version($1,$2)`, ["site", "teznevise.ir"]);
	await sql.query(`SELECT ensure_scope_version($1,$2)`, ["component", "qalam"]);
	await sql.query(`SELECT ensure_scope_version($1,$2)`, ["task_type", "web_content"]);
	await sql.query(`SELECT ensure_scope_version($1,$2)`, ["task_type", "landing_product"]);
	await sql.query(`SELECT ensure_scope_version($1,$2)`, ["task_type", "ux_microcopy"]);
	await sql.query(`SELECT ensure_scope_version($1,$2)`, ["task_type", "student_faq"]);
	const have = await sql.query(`SELECT canonical_key FROM memory_records`);
	const haveKeys = new Set(have.map((r) => r.canonical_key));
	for (const m of MEMORIES) {
		if (haveKeys.has(m.canonical_key)) continue;
		const checksum = sha256Text(m.content);
		await sql.query(`INSERT INTO memory_records(
        id,canonical_key,record_type,scope_type,scope_id,priority,authority,provenance,status,
        privacy_class,title,content,summary,source_type,source_reference,created_by,checksum,confidence
      ) VALUES ($1,$2,$3,$4,$5,$6,$7,'CONFIRMED','ACTIVE','LOCAL_ONLY',$8,$9,$10,'seed',$11,'qalam-factory',$12,0.950)
      ON CONFLICT (id) DO NOTHING`, [
			m.id,
			m.canonical_key,
			m.record_type,
			m.scope_type,
			m.scope_id,
			m.priority,
			m.authority,
			m.title,
			m.content,
			m.summary,
			m.source_reference,
			checksum
		]);
	}
	await sql.query(`INSERT INTO tool_registry(tool_name,side_effect_class,mutation_type,requires_receipt,requires_snapshot,requires_live_verification,default_decision)
     VALUES
     ('wp_read','READ',NULL,false,false,false,'ALLOW'),
     ('wp_update_metadata','WRITE','METADATA_UPDATE',true,true,true,'ALLOW'),
     ('wp_publish','WRITE','PUBLISH',true,true,true,'ESCALATE'),
     ('wp_delete','DELETE','DELETE',true,true,true,'ESCALATE'),
     ('ada_memory_read','READ',NULL,false,false,false,'ALLOW'),
     ('ada_memory_upsert','WRITE','POLICY_CHANGE',true,false,false,'ESCALATE')
     ON CONFLICT (tool_name) DO NOTHING`);
	await sql.query(`INSERT INTO agent_passports(id,agent_id,task_type,allowed_sites,allowed_tools,allowed_mutation_types,max_batch_size,approval_classes)
     VALUES
     ('bbbbbbbb-0001-4000-8000-000000000001','qalam-desk','*',ARRAY['teznevise.ir']::text[],ARRAY['ada_memory_read','wp_read']::text[],ARRAY[]::text[],1,ARRAY['DELETE','WRITE','EXTERNAL_MESSAGE']::text[]),
     ('bbbbbbbb-0001-4000-8000-000000000002','mistral-shadow','academic_content',ARRAY['teznevise.ir']::text[],ARRAY['wp_read']::text[],ARRAY[]::text[],1,ARRAY['DELETE','WRITE','EXTERNAL_MESSAGE']::text[])
     ON CONFLICT (id) DO NOTHING`);
	await sql.query(`INSERT INTO policy_releases(component,release,content_hash,status,activated_at)
     VALUES ('qalam','2.0.0',$1,'ACTIVE',now())
     ON CONFLICT (component,release) DO NOTHING`, [sha256Text("art-of-writing-bible-2.0.0")]);
	await sql.query(`INSERT INTO project_states(project_id,lane,objective,verified_status,completed_work,active_decisions,blockers,next_action,active_artifacts,pending_qa,updated_by)
     VALUES (
       'qalam','main',
       'سامانه نگارش ایرانی + پی پی0 حافظه Ada',
       'operating',
       $1::jsonb,$2::jsonb,$3::jsonb,
       'عامل قبل از نگارش bootstrap کند',
       $4::jsonb,$5::jsonb,
       'qalam-factory'
     )
     ON CONFLICT (project_id,lane) DO NOTHING`, [
		JSON.stringify(["bible-2.0", "ada-schema-0.2"]),
		JSON.stringify([
			"iranian-not-dari",
			"registers-not-blended",
			"no-voice-clone"
		]),
		JSON.stringify([
			"TheSEOCommunity-inaccessible",
			"named-reviewers-unassigned",
			"slices-B-C-G-not-in-pack"
		]),
		JSON.stringify([
			"/desk",
			"/ada",
			"/factory/os"
		]),
		JSON.stringify(["live-teznevise-not-published"])
	]);
}
var PREVIEW_HMAC = "ada-preview-hmac-key-not-for-production-use!";
async function db() {
	const sql = await getSql();
	await ensureAdaSeed(sql);
	return sql;
}
function wantedScopes(req) {
	const scopes = [["global", "*"]];
	if (req.project_id) scopes.push(["project", req.project_id]);
	if (req.site_id) scopes.push(["site", req.site_id]);
	scopes.push(["task_type", req.task_type]);
	scopes.push(["agent", req.agent_id]);
	scopes.push(["component", "qalam"]);
	return scopes;
}
async function ensureDeps(sql, scopes) {
	const deps = [];
	for (const [st, sid] of scopes) {
		const rows = await sql.query(`SELECT ensure_scope_version($1,$2) AS version`, [st, sid]);
		deps.push({
			scope_type: st,
			scope_id: sid,
			version: Number(rows[0]?.version ?? 1)
		});
	}
	return deps;
}
function asStringArray(v) {
	if (Array.isArray(v)) return v.map((x) => String(x));
	if (typeof v === "string") try {
		const parsed = JSON.parse(v);
		if (Array.isArray(parsed)) return parsed.map((x) => String(x));
	} catch {
		return v ? [v] : [];
	}
	return [];
}
function mapMemory(r) {
	return {
		id: String(r.id),
		canonical_key: String(r.canonical_key),
		record_type: String(r.record_type),
		scope_type: String(r.scope_type),
		scope_id: String(r.scope_id),
		priority: Number(r.priority),
		authority: String(r.authority),
		provenance: String(r.provenance),
		privacy_class: String(r.privacy_class),
		title: String(r.title),
		content: String(r.content),
		summary: r.summary == null ? null : String(r.summary),
		checksum: String(r.checksum)
	};
}
var adaBootstrap_createServerFn_handler = createServerRpc({
	id: "e2783f68d3a24b8b11a24743b9a49d642c877b4997f44988a816b0bedcd90b66",
	name: "adaBootstrap",
	filename: "src/lib/ada/server.ts"
}, (opts) => adaBootstrap.__executeServer(opts));
var adaBootstrap = createServerFn({ method: "POST" }).validator((d) => d).handler(adaBootstrap_createServerFn_handler, async ({ data }) => {
	const sql = await db();
	const lane = data.project_lane || "main";
	const scopes = wantedScopes(data);
	const deps = await ensureDeps(sql, scopes);
	const clauses = [];
	const args = [];
	let i = 1;
	for (const [st, sid] of scopes) {
		if (st === "component") continue;
		clauses.push(`(scope_type=$${i} AND scope_id=$${i + 1})`);
		args.push(st, sid);
		i += 2;
	}
	const memories = (await sql.query(`SELECT id,canonical_key,record_type,scope_type,scope_id,priority,authority,provenance,
                privacy_class,title,content,summary,checksum
         FROM memory_records
         WHERE status='ACTIVE' AND priority<=1 AND (${clauses.join(" OR ")})
           AND valid_from<=now() AND (valid_until IS NULL OR valid_until>now())
         ORDER BY priority ASC,
           CASE authority WHEN 'user_explicit' THEN 0 WHEN 'verified_system' THEN 1
             WHEN 'project_canonical' THEN 2 WHEN 'agent_verified' THEN 3 ELSE 9 END,
           updated_at DESC`, args)).map(mapMemory);
	let state = null;
	let stateVersion = null;
	if (data.project_id) {
		const s = (await sql.query(`SELECT * FROM project_states WHERE project_id=$1 AND lane=$2`, [data.project_id, lane]))[0];
		if (s) {
			stateVersion = Number(s.state_version);
			state = {
				project_id: String(s.project_id),
				lane: String(s.lane),
				objective: s.objective == null ? null : String(s.objective),
				verified_status: s.verified_status == null ? null : String(s.verified_status),
				completed_work: asStringArray(s.completed_work),
				active_decisions: asStringArray(s.active_decisions),
				blockers: asStringArray(s.blockers),
				next_action: s.next_action == null ? null : String(s.next_action),
				active_artifacts: asStringArray(s.active_artifacts),
				pending_qa: asStringArray(s.pending_qa),
				state_version: stateVersion,
				updated_by: String(s.updated_by)
			};
		}
	}
	const q = (await sql.query(`SELECT release, content_hash FROM policy_releases WHERE component='qalam' AND status='ACTIVE' LIMIT 1`))[0];
	const passportRow = (await sql.query(`SELECT * FROM agent_passports
         WHERE agent_id=$1 AND enabled=true AND task_type IN ($2,'*')
           AND valid_from<=now() AND (valid_until IS NULL OR valid_until>now())
         ORDER BY CASE WHEN task_type=$2 THEN 0 ELSE 1 END, updated_at DESC LIMIT 1`, [data.agent_id, data.task_type]))[0];
	const passport = passportRow ? {
		id: String(passportRow.id),
		agent_id: String(passportRow.agent_id),
		task_type: String(passportRow.task_type),
		allowed_sites: passportRow.allowed_sites ?? [],
		allowed_tools: passportRow.allowed_tools ?? [],
		allowed_mutation_types: passportRow.allowed_mutation_types ?? [],
		max_batch_size: Number(passportRow.max_batch_size),
		approval_classes: passportRow.approval_classes ?? [],
		version: Number(passportRow.version)
	} : null;
	const memoryIds = memories.map((m) => m.id);
	const contextHash = sha256Obj({
		agent_id: data.agent_id,
		task_type: data.task_type,
		project_id: data.project_id ?? null,
		site_id: data.site_id ?? null,
		project_lane: lane,
		dependencies: deps,
		memory_ids: memoryIds,
		memory_checksums: memories.map((m) => m.checksum),
		project_state_version: stateVersion,
		qalam_release: q?.release ?? null,
		qalam_hash: q?.content_hash ?? null,
		passport_id: passport?.id ?? null,
		passport_version: passport?.version ?? null
	});
	const rid = newId();
	const expiresIso = toIsoSeconds(/* @__PURE__ */ new Date(Math.floor(((/* @__PURE__ */ new Date()).getTime() + receiptTtlMs()) / 1e3) * 1e3));
	const signature = hmacSign({
		receipt_id: rid,
		agent_id: data.agent_id,
		task_type: data.task_type,
		project_id: data.project_id ?? null,
		site_id: data.site_id ?? null,
		project_lane: lane,
		context_hash: contextHash,
		payload_hash: contextHash,
		expires_at: expiresIso,
		key_id: RECEIPT_KEY_ID,
		signature_alg: "HMAC-SHA256"
	});
	await sql.query(`INSERT INTO context_receipts(
        id,agent_id,project_id,site_id,task_type,project_lane,memory_ids,
        project_state_version,qalam_release,qalam_hash,passport_id,passport_version,
        context_hash,payload_hash,signature_alg,key_id,signature,expires_at)
       VALUES ($1,$2,$3,$4,$5,$6,$7::text[],$8,$9,$10,$11,$12,$13,$14,'HMAC-SHA256',$15,$16,$17)`, [
		rid,
		data.agent_id,
		data.project_id ?? null,
		data.site_id ?? null,
		data.task_type,
		lane,
		memoryIds,
		stateVersion,
		q?.release ?? null,
		q?.content_hash ?? null,
		passport?.id ?? null,
		passport?.version ?? null,
		contextHash,
		contextHash,
		RECEIPT_KEY_ID,
		signature,
		expiresIso
	]);
	for (const d of deps) await sql.query(`INSERT INTO receipt_dependencies(receipt_id,scope_type,scope_id,version) VALUES ($1,$2,$3,$4)`, [
		rid,
		d.scope_type,
		d.scope_id,
		d.version
	]);
	await sql.query(`INSERT INTO audit_events(actor,event_type,resource_type,resource_id,decision,result_status,details)
       VALUES ('qalam-factory','bootstrap','context_receipt',$1,'ALLOW','ok',$2::jsonb)`, [rid, JSON.stringify({
		agent_id: data.agent_id,
		task_type: data.task_type,
		n_memory: memories.length
	})]);
	return {
		receipt_id: rid,
		context_hash: contextHash,
		expires_at: expiresIso,
		dependencies: deps,
		mandatory_memory: memories,
		project_state: state,
		qalam_release: q?.release ?? null,
		passport,
		preview_hmac: receiptHmacKey() === PREVIEW_HMAC
	};
});
var adaValidateReceipt_createServerFn_handler = createServerRpc({
	id: "83b2377a2aa25180609c41a04b4203afc5b683e0fe22459c200d6b3181941e97",
	name: "adaValidateReceipt",
	filename: "src/lib/ada/server.ts"
}, (opts) => adaValidateReceipt.__executeServer(opts));
var adaValidateReceipt = createServerFn({ method: "POST" }).validator((d) => d).handler(adaValidateReceipt_createServerFn_handler, async ({ data }) => {
	const sql = await db();
	const rec = (await sql.query(`SELECT * FROM context_receipts WHERE id=$1`, [data.receipt_id]))[0];
	if (!rec) return {
		valid: false,
		reason: "receipt_not_found",
		dependencies: []
	};
	if (rec.revoked_at) return {
		valid: false,
		reason: "revoked",
		dependencies: []
	};
	if (new Date(String(rec.expires_at)).getTime() <= Date.now()) return {
		valid: false,
		reason: "expired",
		dependencies: []
	};
	const deps = await sql.query(`SELECT scope_type, scope_id, version::int AS version FROM receipt_dependencies WHERE receipt_id=$1 ORDER BY scope_type,scope_id`, [data.receipt_id]);
	for (const d of deps) {
		const cur = (await sql.query(`SELECT version FROM scope_versions WHERE scope_type=$1 AND scope_id=$2`, [d.scope_type, d.scope_id]))[0];
		if (!cur || Number(cur.version) !== Number(d.version)) return {
			valid: false,
			reason: `stale_context:${d.scope_type}:${d.scope_id}`,
			dependencies: deps
		};
	}
	const payload = {
		receipt_id: String(rec.id),
		agent_id: String(rec.agent_id),
		task_type: String(rec.task_type),
		project_id: rec.project_id == null ? null : String(rec.project_id),
		site_id: rec.site_id == null ? null : String(rec.site_id),
		project_lane: String(rec.project_lane),
		context_hash: String(rec.context_hash),
		payload_hash: String(rec.payload_hash),
		expires_at: toIsoSeconds(rec.expires_at),
		key_id: String(rec.key_id),
		signature_alg: String(rec.signature_alg)
	};
	if (String(rec.signature_alg) !== "HMAC-SHA256" || !hmacVerify(payload, String(rec.signature))) return {
		valid: false,
		reason: "bad_signature",
		dependencies: deps
	};
	return {
		valid: true,
		reason: "ok",
		dependencies: deps
	};
});
var adaListMemory_createServerFn_handler = createServerRpc({
	id: "bd181e364d476b0f4d1795e829dc2e3b5c4beb7d503538562c3b037e66dec2d6",
	name: "adaListMemory",
	filename: "src/lib/ada/server.ts"
}, (opts) => adaListMemory.__executeServer(opts));
var adaListMemory = createServerFn({ method: "POST" }).handler(adaListMemory_createServerFn_handler, async () => {
	const sql = await db();
	const memories = (await sql.query(`SELECT id,canonical_key,record_type,scope_type,scope_id,priority,authority,provenance,
              privacy_class,title,content,summary,checksum
       FROM memory_records WHERE status='ACTIVE' ORDER BY priority ASC, canonical_key`)).map(mapMemory);
	const tools = await sql.query(`SELECT tool_name, side_effect_class, mutation_type, requires_receipt, requires_snapshot, default_decision, enabled FROM tool_registry ORDER BY tool_name`);
	const passports = await sql.query(`SELECT id,agent_id,task_type,allowed_sites,allowed_tools,allowed_mutation_types,max_batch_size,approval_classes,version FROM agent_passports WHERE enabled=true`);
	const state = (await sql.query(`SELECT * FROM project_states WHERE project_id='qalam' AND lane='main'`))[0];
	const policy = (await sql.query(`SELECT release, content_hash FROM policy_releases WHERE component='qalam' AND status='ACTIVE' LIMIT 1`))[0];
	return {
		memories,
		tools,
		passports: passports.map((p) => ({
			id: String(p.id),
			agent_id: String(p.agent_id),
			task_type: String(p.task_type),
			allowed_sites: p.allowed_sites ?? [],
			allowed_tools: p.allowed_tools ?? [],
			allowed_mutation_types: p.allowed_mutation_types ?? [],
			max_batch_size: Number(p.max_batch_size),
			approval_classes: p.approval_classes ?? [],
			version: Number(p.version)
		})),
		state: state ? {
			project_id: String(state.project_id),
			lane: String(state.lane),
			objective: state.objective == null ? null : String(state.objective),
			verified_status: state.verified_status == null ? null : String(state.verified_status),
			completed_work: asStringArray(state.completed_work),
			active_decisions: asStringArray(state.active_decisions),
			blockers: asStringArray(state.blockers),
			next_action: state.next_action == null ? null : String(state.next_action),
			active_artifacts: asStringArray(state.active_artifacts),
			pending_qa: asStringArray(state.pending_qa),
			state_version: Number(state.state_version),
			updated_by: String(state.updated_by)
		} : null,
		qalam_release: policy?.release ?? null,
		preview_hmac: receiptHmacKey() === PREVIEW_HMAC
	};
});
var adaAuthorize_createServerFn_handler = createServerRpc({
	id: "757f7404502eeea822ff82d4285fe5a444e219a785f4dbedb372674a0bd43123",
	name: "adaAuthorize",
	filename: "src/lib/ada/server.ts"
}, (opts) => adaAuthorize.__executeServer(opts));
var adaAuthorize = createServerFn({ method: "POST" }).validator((d) => d).handler(adaAuthorize_createServerFn_handler, async ({ data }) => {
	const sql = await db();
	const tool = (await sql.query(`SELECT tool_name, side_effect_class, mutation_type, requires_receipt, requires_snapshot, default_decision, enabled FROM tool_registry WHERE tool_name=$1 AND enabled=true`, [data.tool_name]))[0];
	if (!tool) return {
		decision: "DENY",
		reason: "unknown_or_disabled_tool"
	};
	const pp = (await sql.query(`SELECT * FROM agent_passports WHERE agent_id=$1 AND enabled=true AND task_type IN ($2,'*')
         AND valid_from<=now() AND (valid_until IS NULL OR valid_until>now())
         ORDER BY CASE WHEN task_type=$2 THEN 0 ELSE 1 END, updated_at DESC LIMIT 1`, [data.agent_id, data.task_type]))[0];
	if (!pp) return {
		decision: "DENY",
		reason: "missing_passport"
	};
	if (!(pp.allowed_tools ?? []).includes(data.tool_name)) return {
		decision: "DENY",
		reason: "tool_not_in_passport"
	};
	const allowedSites = pp.allowed_sites ?? [];
	if (data.site_id && allowedSites.length && !allowedSites.includes(data.site_id)) return {
		decision: "DENY",
		reason: "site_not_in_passport"
	};
	if (tool.requires_receipt) {
		if (!data.receipt_id) return {
			decision: "DENY",
			reason: "missing_context_receipt"
		};
		const rec = (await sql.query(`SELECT * FROM context_receipts WHERE id=$1`, [data.receipt_id]))[0];
		if (!rec) return {
			decision: "DENY",
			reason: "receipt_not_found"
		};
		if (rec.revoked_at) return {
			decision: "DENY",
			reason: "revoked"
		};
		if (new Date(String(rec.expires_at)).getTime() <= Date.now()) return {
			decision: "DENY",
			reason: "expired"
		};
	}
	if ([
		"WRITE",
		"DELETE",
		"EXTERNAL_MESSAGE",
		"POLICY_CHANGE"
	].includes(tool.side_effect_class)) {
		const allowedMut = pp.allowed_mutation_types ?? [];
		if (tool.mutation_type && allowedMut.length && !allowedMut.includes(tool.mutation_type)) return {
			decision: "DENY",
			reason: "mutation_type_not_in_passport"
		};
		if (tool.default_decision === "ESCALATE") return {
			decision: "ESCALATE",
			reason: "tool_requires_approval"
		};
	}
	return {
		decision: tool.default_decision === "DENY" ? "DENY" : "ALLOW",
		reason: "ok"
	};
});
var adaQuarantine_createServerFn_handler = createServerRpc({
	id: "f2f2bad8ddec0d3d59607398bf0c38878b16e6c9cb2aef0234e36cc1d77bdd54",
	name: "adaQuarantine",
	filename: "src/lib/ada/server.ts"
}, (opts) => adaQuarantine.__executeServer(opts));
var adaQuarantine = createServerFn({ method: "POST" }).validator((d) => d).handler(adaQuarantine_createServerFn_handler, async ({ data }) => {
	const sql = await db();
	const id = newId();
	const hash = sha256Text(data.content_text);
	await sql.query(`INSERT INTO external_inputs(id,source_uri,source_kind,trust_class,content_hash,content_text,quarantine_status,ingested_by)
       VALUES ($1,$2,$3,'UNTRUSTED_EXTERNAL',$4,$5,'QUARANTINED','qalam-factory')`, [
		id,
		data.source_uri ?? null,
		data.source_kind,
		hash,
		data.content_text.slice(0, 4e3)
	]);
	return {
		id,
		quarantine_status: "QUARANTINED",
		promoted: false
	};
});
//#endregion
export { adaAuthorize_createServerFn_handler, adaBootstrap_createServerFn_handler, adaListMemory_createServerFn_handler, adaQuarantine_createServerFn_handler, adaValidateReceipt_createServerFn_handler };
