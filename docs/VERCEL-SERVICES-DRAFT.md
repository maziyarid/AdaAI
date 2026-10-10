# Internal Vercel prototype draft — 2026-10-10

Owner confirmation: “Isolated prototype draft only” and “Yes: both internal, no public paths”. This branch prepares the earlier PostgreSQL Context Core experiment only. The canonical MariaDB control core, existing controller, queue, scheduler, bridge, bot and disabled delivery controls remain unchanged. This is not a production migration or deployment approval.

Source: isolated branch `draft/ada-vercel-prototype-only-20261010`, based on remote main at AdaAI `15c98a1eee21d50b00441777b7d7beaf846d663f`. Only the prototype changes from original draft `f2911904c7b6437f077a03db2a7d6d13545c434f` were cherry-picked. The three unpublished AAX-44 bridge commits are excluded; the original draft branch and archives are preserved. AAX-39 candidate `b55f00948757d48750362268c187eee46807b83e` is unavailable and is not represented by this draft. Ownership was recorded in AAX-31 comment `01M4KCPA548XJMA42PP48ZHA8M` before edits.

## Proposed service graph

`mcp → app → external PostgreSQL`

| Service | Root / entrypoint | Callers and paths |
| --- | --- | --- |
| app | `ada-context-core`, `app.main:app` | MCP calls `/healthz`, `/v1/bootstrap`, `/v1/receipts/{id}/validate`, `/v1/memory/upsert`, `/v1/state/update` |
| mcp | `ada-context-core/mcp`, `vercel_entry:app` | Internal ASGI `/mcp`; no public route or authenticated external caller configured |

The complete proposed configuration is the root `vercel.json`. Its only binding is caller-side on `mcp`: service `app`, type `service`, format `url`, environment name `ADA_CORE_URL`. Empty rewrites intentionally expose no public path. There is no app-to-MCP call. `ada-reliability` is a library and CLI collection, not an HTTP service. The example bootstrap client remains an external example; it is not another deployed service.

The app root is the parent directory of its Python package so `app.main` retains relative imports. A root requirements file delegates to the existing app requirements. MCP gets a separate ASGI export with stateless HTTP, leaving its existing standalone run command intact. Its real HTTP call sites resolve `ADA_CORE_URL` when called, keeping `X-Ada-Internal-Key` on protected calls. Missing bindings fail closed on Vercel; local standalone development retains its loopback default.

## Environment and security boundaries

| Variable | Service | Provisioning status |
| --- | --- | --- |
| `ADA_CORE_URL` | mcp | Vercel runtime service binding; do not manually provision a deployment URL |
| `ADA_INTERNAL_API_KEY` | app and mcp | Existing application authentication; no secret created or changed |
| `ADA_DATABASE_URL` | app | PostgreSQL prototype connection; disposable experiment destination not selected or provisioned |
| `ADA_RECEIPT_HMAC_KEY` | app | Existing receipt signing requirement; no secret created or changed |
| `ADA_RECEIPT_KEY_ID` | app | Existing optional signing identifier |

App import currently validates its DB URL and API key and creates a PostgreSQL connection pool (1–8 connections). Signing validates its HMAC key when used. Serverless lifecycle, connection budgets and isolated schema provisioning need real validation. The schema is PostgreSQL-specific; it cannot be pointed at the canonical MariaDB database.

MCP currently has no inbound caller authentication. The app's shared key does not independently establish a human approver's identity. Neither boundary is redesigned here. Service bindings bypass public routing protections, so existing application authorization must remain in place. Any future public exposure needs a separately agreed authentication gateway and route policy. No public paths are present in this draft. If prefixes are introduced later, route selection alone does not strip the prefix; request-path transformation or matching application routes must be verified.

## Verification and outstanding acceptance

Five source wiring tests passed with framework and HTTP spies: runtime binding changes, missing-binding failure, preserved local default, real MCP call-site paths/authentication headers and ASGI export arguments, and config/service-entrypoint shape. The spies perform no network or database activity. They do not validate FastMCP protocol behavior, real ASGI lifecycle, official JSON schema acceptance or a Vercel build.

Command (isolated process, credentials absent):

```sh
env -i PATH=/usr/bin:/bin LANG=C.UTF-8 PLATFORM_LAUNCH_DB_TEST=0 PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest discover -s ada-context-core/tests -p test_vercel_draft.py -v
```

The original draft run passed 5 tests in 0.012s, exit 0. The clean branch is independently rerun; its execution log is retained in the accompanying local evidence directory. No failed or skipped tests. Real dependency import/build and DB integration were not run: FastAPI, FastMCP, httpx, psycopg, psycopg_pool and the Vercel CLI are absent from the checked Python environment. No packages were installed. No credentials, migrations, deployments, provider sends, pushes or PRs were performed.

Next executable step after separate environment authorization: build this exact revision with the declared dependencies and Vercel CLI, verify the real MCP ASGI lifecycle and binding behavior, then run app integration against an explicitly disposable PostgreSQL instance. Provisioning and deployment approval remain separate. Production readiness is not established. Rollback is to discard this isolated draft or revert its single draft commit; existing deployed services and prior AAX-44 artifacts are unaffected.

## Source and platform references

Source inspected: `ada-context-core/app/main.py`, `app/core.py`, `mcp/server.py`, `mcp/requirements.txt`, `app/requirements.txt`, `sql/001_schema.sql`, `examples/bootstrap_client.py`, `ada-reliability/pyproject.toml`, README, AGENTS.md and existing deployment/divergence documentation. No Docker or Compose service graph was present.

- https://vercel.com/docs/services
- https://vercel.com/docs/services/config-reference
- https://vercel.com/docs/services/bindings
- https://vercel.com/docs/services/routing
- https://gofastmcp.com/deployment/http

These references informed the draft; they do not substitute for a build of this repository.

## Publication preflight boundary

The canonical remote is https://github.com/maziyarid/AdaAI.git; this isolated checkout has a local clone origin. Publication is pending owner approval request `Sentinel_863a4799f7b48191b19a86a5f6c10dad`; no approval is inferred from that request. A push may trigger an automatic preview build. Main remains unchanged and both services remain internal. The parent reported a verified Vercel workspace HTTP 403: this is an access limitation, and empty unscoped project/team lists do not establish absence of actual projects. The actual import branch and automatic deployment settings remain unverified.
