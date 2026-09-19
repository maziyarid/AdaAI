# AdaAI Phase-1 VPS Deployment

Inspection-first. The live control plane is MariaDB-backed `maziyar-control-core` on `127.0.0.1:8770`. Do **not** install PostgreSQL or a second scheduler.

For additive `ada_*` schema see `docs/MIGRATION-RUNBOOK.md` and `docs/ROLLBACK-RUNBOOK.md`.

> **Correction 2026-09-16:** Stages below that mention PostgreSQL, port 8791, or `ada-context-core.service` are prototype leftovers. Do not follow them on the live VPS. Phase 1: back up MariaDB → apply additive `ada_*` SQL after approval → wrap Mistral in shadow mode → one Teznevise canary.

## Safety boundary


- Do not restart or reconfigure the existing VPS MCP, WordPress MCP, OAuth gateway, session router, or unrelated site services as part of the Context Core deployment.
- Do not expose the private Context Core REST port publicly.
- Do not install a local 4B+ LLM on the current production VPS during Phase 1.
- Do not seed raw conversation history as canonical memory.
- Back up relevant configuration before changing Nginx, systemd, MariaDB, or OAuth routing.


## Canonical paths and ports

- Repository checkout: `/srv/ada`
- Context Core runtime: `/srv/ada/context-core`
- Environment file: `/etc/ada/context_core.env` (0600)
- Private REST: `127.0.0.1:8791`
- Private MCP adapter: use its packaged loopback configuration after preflight confirms a free port
- Public MCP route: `https://mcp.maziyarid.com/context-mcp` only after authenticated gateway integration

## Stage 0 — read-only preflight

Run `ada-context-core/scripts/preflight.sh` first and record:

- OS/distribution and kernel
- CPU/RAM/swap/disk headroom
- Python version
- PostgreSQL client/server status and version, if present
- current listeners around planned Ada ports
- current Nginx/OAuth/MCP service state without restarting anything
- current backup capacity and off-host destination availability

If memory/disk/process pressure is unsafe, stop before installation.

## Stage 1 — repository and service account

1. Clone `maziyarid/AdaAI` to `/srv/ada` from `main`.
2. Create a dedicated non-login `ada` service user/group if absent.
3. Give Ada ownership only of its own runtime/data directories.
4. Create `/etc/ada/context_core.env` from the example; keep it mode 0600 and never commit secrets.

## Stage 2 — PostgreSQL

1. Reuse an appropriate existing PostgreSQL server if one is already healthy; otherwise install a supported PostgreSQL release only after checking the host's package-management/cPanel constraints.
2. Create a dedicated Ada database and least-privilege database role.
3. Apply `ada-context-core/sql/001_schema.sql`.
4. Keep connection counts conservative on the small production VPS; measure before tuning.
5. Do not add pgvector in Phase 1.

## Stage 3 — recovery before authority

Before importing canonical memory:

1. Configure encrypted database backup using the packaged backup tooling.
2. Configure WAL/PITR appropriate to the discovered PostgreSQL setup.
3. Replicate backups off-host.
4. Run `restore-drill.sh` into a temporary database and prove key Ada tables can be read.
5. Record the restore result.

Context Core is not authoritative until recovery has been tested.

## Stage 4 — Context Core REST

1. Install Python dependencies in an isolated virtual environment under `/srv/ada/context-core`.
2. Install the packaged `ada-context-core.service` after verifying its paths/user match the host.
3. Start **only** this Ada service.
4. Verify `http://127.0.0.1:8791/healthz` locally.
5. Verify the database schema and audit writes.

Do not add a public Nginx route yet.

## Stage 5 — seed a minimal canonical context

Seed only reviewed records required for the first pilot:

- global P0 execution rules
- current Qalam pointer/release policy
- one Teznevise site policy set
- one academic-content task policy
- current working state for the pilot lane

Verify `/v1/bootstrap` returns only the expected scopes, versions, and active records. Then change one relevant policy and prove the old receipt fails with `STALE_CONTEXT` while unrelated scopes remain valid.

## Stage 6 — MCP adapter and authentication

1. Start the Context MCP adapter on loopback.
2. Integrate `/context-mcp` through the existing authenticated OAuth/gateway architecture without changing the behavior of `/vps-mcp` or `/wp-mcp`.
3. Verify unauthenticated public access is rejected.
4. Verify an authenticated read-only bootstrap succeeds.
5. Verify a mutating call without a current receipt is denied before any external side effect.

## Stage 7 — Mistral shadow pilot

Do not replace Mistral yet. Wrap the current worker so it must:

`bootstrap -> inspect -> propose structured action -> validate -> authorize`

In shadow mode, stop before WordPress mutation and compare the proposal with expected target, canonical owner, tool, policy decision, and post-condition. Save these traces for AdaEval.

## Stage 8 — one reversible Teznevise canary

After shadow results are acceptable:

1. choose one low-risk reversible mutation;
2. create an exact pre-state snapshot;
3. bind the task to an idempotency key and current context receipt;
4. execute one canary only;
5. independently re-read WordPress/live HTTP state;
6. compare the observed state with the expected post-condition;
7. rollback on verification failure;
8. persist audit/result/project state.

Only repeated canary success permits broader worker passports or batch fan-out.

## Explicitly deferred

- local large-model inference on this VPS
- pgvector/semantic policy retrieval
- autonomous promotion of AI observations to canonical memory
- bulk publishing
- destructive automation
- multi-site fan-out
- model fine-tuning

The next phase starts from measured pilot evidence, not from adding more infrastructure speculatively.
