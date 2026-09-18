# CI status

Ada Context Core's pure contract tests currently pass locally: **7/7**, and `python -m compileall app mcp` succeeds.

Phase-1 `ada-reliability` now has `.github/workflows/ada-reliability.yml`. Hosted Actions previously failed to start in this repository (`docs/CI.md` history below). If the new workflow is skipped by GitHub policy, the equivalent proof is a clean venv:

```bash
python -m venv .venv
. .venv/bin/activate
pip install pytest
pip install -e ada-reliability
python -c "from ada_reliability import AdaEngine, seed_phase1"
cd ada-reliability && pytest -q
```

GitHub-hosted Actions was previously not enabled in this repository. Three attempts, including a one-line `echo` runner probe, failed before any workflow step began. That pattern points to a GitHub Actions repository/account runner or policy availability issue rather than an Ada test failure.

The permanently failing workflow was removed from `main` so the repository does not present a false red build signal. The `ada-reliability` workflow is a new, narrower probe; treat a missing run as "Actions unavailable", not as "tests failed".


## Local / VPS validation

From `ada-context-core/`:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r app/requirements.txt
pip install -r mcp/requirements.txt
pip install pytest
python -m compileall app mcp
pytest -q
```

Database integration tests should run against an isolated Ada test database by setting `ADA_TEST_DATABASE_URL`. They must not use the production Context Core database.

## Re-enabling GitHub CI

Re-add a workflow only after a minimal hosted-runner probe can actually start. At that point CI should run:

1. Python compilation
2. pure contract tests
3. schema/static checks
4. database integration tests using an ephemeral PostgreSQL service or isolated test database
5. no production credentials and no production MCP mutation

The absence of GitHub CI does not weaken the production gate: the VPS deployment itself must run the same tests before service installation or upgrade.

## 2026-09-19T23:20Z — runner still never starts (HEAD `7953eab`)

GitHub Actions workflow `.github/workflows/ada-reliability.yml` is
`state=active`. Latest runs on this SHA:

- pull_request run `35404703254` job `105791932183`
- push run `35404699202` job `105791920594`

Both `conclusion=failure` in ~2 seconds. Job JSON:
`runner_id=0`, `runner_name=""`, `runner_group_id=0`. Log download
returns HTTP 404. Checkout / setup-python / pytest never ran.

This is hosted-runner assignment, not a failing Ada suite. Local
clean venv on the same tree: **149 passed**, import
`AdaEngine` / `seed_phase1` / `FailedRunOutbox` OK. Do not rewrite
application code to satisfy a runner that never starts.

`mergeable_state=unstable` on PR #2 is this Actions signal. Greptile
5/5 on implementation `3513278` is independent of it.

