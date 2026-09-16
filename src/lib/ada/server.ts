import { createServerFn } from "@tanstack/react-start";
import { getSql, type Sql } from "@/lib/db";
import {
  hmacSign,
  hmacVerify,
  newId,
  receiptHmacKey,
  RECEIPT_KEY_ID,
  receiptTtlMs,
  sha256Obj,
  sha256Text,
  toIsoSeconds,
} from "./crypto";
import { ensureAdaSeed } from "./seed";
import type { AdaMemory, AdaPassport, AdaReceipt, AdaScope, AdaState, AdaTool } from "./types";

const PREVIEW_HMAC = "ada-preview-hmac-key-not-for-production-use!";

async function db(): Promise<Sql> {
  const sql = await getSql();
  await ensureAdaSeed(sql);
  return sql;
}

type BootstrapIn = {
  agent_id: string;
  task_type: string;
  project_id?: string;
  project_lane?: string;
  site_id?: string;
};

function wantedScopes(req: BootstrapIn): Array<[string, string]> {
  const scopes: Array<[string, string]> = [["global", "*"]];
  if (req.project_id) scopes.push(["project", req.project_id]);
  if (req.site_id) scopes.push(["site", req.site_id]);
  scopes.push(["task_type", req.task_type]);
  scopes.push(["agent", req.agent_id]);
  scopes.push(["component", "qalam"]);
  return scopes;
}

async function ensureDeps(sql: Sql, scopes: Array<[string, string]>): Promise<AdaScope[]> {
  const deps: AdaScope[] = [];
  for (const [st, sid] of scopes) {
    const rows = await sql.query<{ version: number }>(`SELECT ensure_scope_version($1,$2) AS version`, [st, sid]);
    deps.push({ scope_type: st, scope_id: sid, version: Number(rows[0]?.version ?? 1) });
  }
  return deps;
}

function asStringArray(v: unknown): string[] {
  if (Array.isArray(v)) return v.map((x) => String(x));
  if (typeof v === "string") {
    try {
      const parsed = JSON.parse(v) as unknown;
      if (Array.isArray(parsed)) return parsed.map((x) => String(x));
    } catch {
      return v ? [v] : [];
    }
  }
  return [];
}

function mapMemory(r: Record<string, unknown>): AdaMemory {
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
    checksum: String(r.checksum),
  };
}

export const adaBootstrap = createServerFn({ method: "POST" })
  .validator((d: BootstrapIn) => d)
  .handler(async ({ data }): Promise<AdaReceipt> => {
    const sql = await db();
    const lane = data.project_lane || "main";
    const scopes = wantedScopes(data);
    const deps = await ensureDeps(sql, scopes);

    const clauses: string[] = [];
    const args: unknown[] = [];
    let i = 1;
    for (const [st, sid] of scopes) {
      if (st === "component") continue;
      clauses.push(`(scope_type=$${i} AND scope_id=$${i + 1})`);
      args.push(st, sid);
      i += 2;
    }

    const memories = (
      await sql.query<Record<string, unknown>>(
        `SELECT id,canonical_key,record_type,scope_type,scope_id,priority,authority,provenance,
                privacy_class,title,content,summary,checksum
         FROM memory_records
         WHERE status='ACTIVE' AND priority<=1 AND (${clauses.join(" OR ")})
           AND valid_from<=now() AND (valid_until IS NULL OR valid_until>now())
         ORDER BY priority ASC,
           CASE authority WHEN 'user_explicit' THEN 0 WHEN 'verified_system' THEN 1
             WHEN 'project_canonical' THEN 2 WHEN 'agent_verified' THEN 3 ELSE 9 END,
           updated_at DESC`,
        args,
      )
    ).map(mapMemory);

    let state: AdaState | null = null;
    let stateVersion: number | null = null;
    if (data.project_id) {
      const rows = await sql.query<Record<string, unknown>>(
        `SELECT * FROM project_states WHERE project_id=$1 AND lane=$2`,
        [data.project_id, lane],
      );
      const s = rows[0];
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
          updated_by: String(s.updated_by),
        };
      }
    }

    const q = (
      await sql.query<{ release: string; content_hash: string }>(
        `SELECT release, content_hash FROM policy_releases WHERE component='qalam' AND status='ACTIVE' LIMIT 1`,
      )
    )[0];

    const passportRow = (
      await sql.query<Record<string, unknown>>(
        `SELECT * FROM agent_passports
         WHERE agent_id=$1 AND enabled=true AND task_type IN ($2,'*')
           AND valid_from<=now() AND (valid_until IS NULL OR valid_until>now())
         ORDER BY CASE WHEN task_type=$2 THEN 0 ELSE 1 END, updated_at DESC LIMIT 1`,
        [data.agent_id, data.task_type],
      )
    )[0];

    const passport: AdaPassport | null = passportRow
      ? {
          id: String(passportRow.id),
          agent_id: String(passportRow.agent_id),
          task_type: String(passportRow.task_type),
          allowed_sites: (passportRow.allowed_sites as string[]) ?? [],
          allowed_tools: (passportRow.allowed_tools as string[]) ?? [],
          allowed_mutation_types: (passportRow.allowed_mutation_types as string[]) ?? [],
          max_batch_size: Number(passportRow.max_batch_size),
          approval_classes: (passportRow.approval_classes as string[]) ?? [],
          version: Number(passportRow.version),
        }
      : null;

    const memoryIds = memories.map((m) => m.id);
    const canonical = {
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
      passport_version: passport?.version ?? null,
    };
    const contextHash = sha256Obj(canonical);
    const rid = newId();
    const issued = new Date();
    const expires = new Date(Math.floor((issued.getTime() + receiptTtlMs()) / 1000) * 1000);
    const expiresIso = toIsoSeconds(expires);
    const payload = {
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
      signature_alg: "HMAC-SHA256",
    };
    const signature = hmacSign(payload);

    await sql.query(
      `INSERT INTO context_receipts(
        id,agent_id,project_id,site_id,task_type,project_lane,memory_ids,
        project_state_version,qalam_release,qalam_hash,passport_id,passport_version,
        context_hash,payload_hash,signature_alg,key_id,signature,expires_at)
       VALUES ($1,$2,$3,$4,$5,$6,$7::text[],$8,$9,$10,$11,$12,$13,$14,'HMAC-SHA256',$15,$16,$17)`,
      [
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
        expiresIso,
      ],
    );
    for (const d of deps) {
      await sql.query(
        `INSERT INTO receipt_dependencies(receipt_id,scope_type,scope_id,version) VALUES ($1,$2,$3,$4)`,
        [rid, d.scope_type, d.scope_id, d.version],
      );
    }
    await sql.query(
      `INSERT INTO audit_events(actor,event_type,resource_type,resource_id,decision,result_status,details)
       VALUES ('qalam-factory','bootstrap','context_receipt',$1,'ALLOW','ok',$2::jsonb)`,
      [rid, JSON.stringify({ agent_id: data.agent_id, task_type: data.task_type, n_memory: memories.length })],
    );

    return {
      receipt_id: rid,
      context_hash: contextHash,
      expires_at: expiresIso,
      dependencies: deps,
      mandatory_memory: memories,
      project_state: state,
      qalam_release: q?.release ?? null,
      passport,
      preview_hmac: receiptHmacKey() === PREVIEW_HMAC,
    };
  });

export const adaValidateReceipt = createServerFn({ method: "POST" })
  .validator((d: { receipt_id: string }) => d)
  .handler(async ({ data }) => {
    const sql = await db();
    const rec = (
      await sql.query<Record<string, unknown>>(`SELECT * FROM context_receipts WHERE id=$1`, [data.receipt_id])
    )[0];
    if (!rec) return { valid: false, reason: "receipt_not_found", dependencies: [] as AdaScope[] };
    if (rec.revoked_at) return { valid: false, reason: "revoked", dependencies: [] as AdaScope[] };
    const expires = new Date(String(rec.expires_at));
    if (expires.getTime() <= Date.now()) return { valid: false, reason: "expired", dependencies: [] as AdaScope[] };

    const deps = await sql.query<AdaScope>(
      `SELECT scope_type, scope_id, version::int AS version FROM receipt_dependencies WHERE receipt_id=$1 ORDER BY scope_type,scope_id`,
      [data.receipt_id],
    );
    for (const d of deps) {
      const cur = (
        await sql.query<{ version: number }>(`SELECT version FROM scope_versions WHERE scope_type=$1 AND scope_id=$2`, [
          d.scope_type,
          d.scope_id,
        ])
      )[0];
      if (!cur || Number(cur.version) !== Number(d.version)) {
        return { valid: false, reason: `stale_context:${d.scope_type}:${d.scope_id}`, dependencies: deps };
      }
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
      expires_at: toIsoSeconds(rec.expires_at as string | Date),
      key_id: String(rec.key_id),
      signature_alg: String(rec.signature_alg),
    };
    if (String(rec.signature_alg) !== "HMAC-SHA256" || !hmacVerify(payload, String(rec.signature))) {
      return { valid: false, reason: "bad_signature", dependencies: deps };
    }
    return { valid: true, reason: "ok", dependencies: deps };
  });

export const adaListMemory = createServerFn({ method: "POST" }).handler(async () => {
  const sql = await db();
  const memories = (
    await sql.query<Record<string, unknown>>(
      `SELECT id,canonical_key,record_type,scope_type,scope_id,priority,authority,provenance,
              privacy_class,title,content,summary,checksum
       FROM memory_records WHERE status='ACTIVE' ORDER BY priority ASC, canonical_key`,
    )
  ).map(mapMemory);
  const tools = await sql.query<AdaTool>(
    `SELECT tool_name, side_effect_class, mutation_type, requires_receipt, requires_snapshot, default_decision, enabled FROM tool_registry ORDER BY tool_name`,
  );
  const passports = await sql.query<Record<string, unknown>>(
    `SELECT id,agent_id,task_type,allowed_sites,allowed_tools,allowed_mutation_types,max_batch_size,approval_classes,version FROM agent_passports WHERE enabled=true`,
  );
  const state = (
    await sql.query<Record<string, unknown>>(`SELECT * FROM project_states WHERE project_id='qalam' AND lane='main'`)
  )[0];
  const policy = (
    await sql.query<{ release: string; content_hash: string }>(
      `SELECT release, content_hash FROM policy_releases WHERE component='qalam' AND status='ACTIVE' LIMIT 1`,
    )
  )[0];
  return {
    memories,
    tools,
    passports: passports.map((p) => ({
      id: String(p.id),
      agent_id: String(p.agent_id),
      task_type: String(p.task_type),
      allowed_sites: (p.allowed_sites as string[]) ?? [],
      allowed_tools: (p.allowed_tools as string[]) ?? [],
      allowed_mutation_types: (p.allowed_mutation_types as string[]) ?? [],
      max_batch_size: Number(p.max_batch_size),
      approval_classes: (p.approval_classes as string[]) ?? [],
      version: Number(p.version),
    })),
    state: state
      ? {
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
          updated_by: String(state.updated_by),
        }
      : null,
    qalam_release: policy?.release ?? null,
    preview_hmac: receiptHmacKey() === PREVIEW_HMAC,
  };
});

export const adaAuthorize = createServerFn({ method: "POST" })
  .validator((d: { agent_id: string; task_type: string; tool_name: string; receipt_id?: string; site_id?: string }) => d)
  .handler(async ({ data }) => {
    const sql = await db();
    const tool = (
      await sql.query<AdaTool>(`SELECT tool_name, side_effect_class, mutation_type, requires_receipt, requires_snapshot, default_decision, enabled FROM tool_registry WHERE tool_name=$1 AND enabled=true`, [
        data.tool_name,
      ])
    )[0];
    if (!tool) return { decision: "DENY" as const, reason: "unknown_or_disabled_tool" };
    const pp = (
      await sql.query<Record<string, unknown>>(
        `SELECT * FROM agent_passports WHERE agent_id=$1 AND enabled=true AND task_type IN ($2,'*')
         AND valid_from<=now() AND (valid_until IS NULL OR valid_until>now())
         ORDER BY CASE WHEN task_type=$2 THEN 0 ELSE 1 END, updated_at DESC LIMIT 1`,
        [data.agent_id, data.task_type],
      )
    )[0];
    if (!pp) return { decision: "DENY" as const, reason: "missing_passport" };
    const allowedTools = (pp.allowed_tools as string[]) ?? [];
    if (!allowedTools.includes(data.tool_name)) return { decision: "DENY" as const, reason: "tool_not_in_passport" };
    const allowedSites = (pp.allowed_sites as string[]) ?? [];
    if (data.site_id && allowedSites.length && !allowedSites.includes(data.site_id)) {
      return { decision: "DENY" as const, reason: "site_not_in_passport" };
    }
    if (tool.requires_receipt) {
      if (!data.receipt_id) return { decision: "DENY" as const, reason: "missing_context_receipt" };
      const rec = (
        await sql.query<Record<string, unknown>>(`SELECT * FROM context_receipts WHERE id=$1`, [data.receipt_id])
      )[0];
      if (!rec) return { decision: "DENY" as const, reason: "receipt_not_found" };
      if (rec.revoked_at) return { decision: "DENY" as const, reason: "revoked" };
      if (new Date(String(rec.expires_at)).getTime() <= Date.now()) return { decision: "DENY" as const, reason: "expired" };
    }
    if (["WRITE", "DELETE", "EXTERNAL_MESSAGE", "POLICY_CHANGE"].includes(tool.side_effect_class)) {
      const allowedMut = (pp.allowed_mutation_types as string[]) ?? [];
      if (tool.mutation_type && allowedMut.length && !allowedMut.includes(tool.mutation_type)) {
        return { decision: "DENY" as const, reason: "mutation_type_not_in_passport" };
      }
      if (tool.default_decision === "ESCALATE") return { decision: "ESCALATE" as const, reason: "tool_requires_approval" };
    }
    return { decision: tool.default_decision === "DENY" ? ("DENY" as const) : ("ALLOW" as const), reason: "ok" };
  });

export const adaQuarantine = createServerFn({ method: "POST" })
  .validator((d: { source_kind: string; content_text: string; source_uri?: string }) => d)
  .handler(async ({ data }) => {
    const sql = await db();
    const id = newId();
    const hash = sha256Text(data.content_text);
    await sql.query(
      `INSERT INTO external_inputs(id,source_uri,source_kind,trust_class,content_hash,content_text,quarantine_status,ingested_by)
       VALUES ($1,$2,$3,'UNTRUSTED_EXTERNAL',$4,$5,'QUARANTINED','qalam-factory')`,
      [id, data.source_uri ?? null, data.source_kind, hash, data.content_text.slice(0, 4000)],
    );
    return { id, quarantine_status: "QUARANTINED" as const, promoted: false };
  });
