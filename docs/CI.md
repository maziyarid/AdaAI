# CI status

## 2026-09-19T08:40Z — runner still unassigned on `d7537ca`

`maziyarid/AdaAI` is **public**. Latest hosted `pytest` checks on
`d7537cada013e278552354411ac09707562ec30d`:

- pull_request run `35431725702` job `105867421213` (~2s, `conclusion=failure`)
- Job JSON: `runner_id=0`, `runner_name=""`, `runner_group_id=0`
- Greptile Review check `105867429476` on the same SHA: **success**
  (completed 08:25:18Z, independent 5/5)

Checkout / setup-python / pytest never ran. This is Actions
provisioning, not a test failure. Do not rewrite Ada application code
for `runner_id=0`. Human check remains account Actions / billing /
abuse.

Local suite on this tree is the proof.


## 2026-09-19T08:25Z — runner still unassigned on `ae4fd13`

`maziyarid/AdaAI` is **public**. Latest hosted `pytest` checks on
`ae4fd13af8b137e3f39bdc0cb19cac583960762a`:

- pull_request run `35431230028` job `105866075903` (~2s, `conclusion=failure`)
- push run `35431227906` job `105866070181` (~2s, `conclusion=failure`)
- Job JSON: `runner_id=0`, `runner_name=""`, `runner_group_id=0`
- Greptile Review check `105866085783` on the same SHA: **success**
  (completed 08:15:09Z, independent 5/5)

Checkout / setup-python / pytest never ran. This is Actions
provisioning, not a test failure. Repo Actions is enabled,
`allowed_actions=all`, 0 self-hosted runners. Do not rewrite Ada
application code for `runner_id=0`. Human check remains account
Actions / billing / abuse.

Local suite on this tree is the proof.


## 2026-09-19T08:10Z — runner still unassigned on `58e64c7`

`maziyarid/AdaAI` is **public**. Latest hosted `pytest` checks on
`58e64c788bbea747251a82c4d5a8c68bd15a7cda`:

- pull_request run `35430640282` job `105864455803` (~2s, `conclusion=failure`)
- Job JSON: `runner_id=0`, `runner_name=""`, `runner_group_id=0`

Checkout / setup-python / pytest never ran. This is Actions
provisioning, not a test failure. Do not rewrite Ada application code
for `runner_id=0`. Human check remains Settings → Actions (repo +
account) and org/rulesets.

Local suite on this tree is the proof.


## 2026-09-19T07:50Z — runner still unassigned on `1a1c995`

`maziyarid/AdaAI` is **public**. Latest hosted `pytest` checks on
`1a1c995f87978f0c1d00dea6954a4792debea0d2`:

- push run `35428657819` job `105859050654` (~2s, `conclusion=failure`)
- pull_request run `35428655847` job `105859044037` (~1s, `conclusion=failure`)

Checkout / setup-python / pytest never ran. This is Actions
provisioning, not a test failure. Do not rewrite Ada application code
for `runner_id=0`. Human check remains Settings → Actions (repo +
account) and org/rulesets.

Local suite on this tree is the proof. Greptile Review completed on
the same SHA independently of hosted pytest.


## 2026-09-19T07:15Z — runner_id=0 on a public repo (HEAD `d7e41a6`)

`maziyarid/AdaAI` is **public**. This is not a private-minutes billing
fail. Latest `ada-reliability` runs on `d7e41a6`:

- pull_request run `35427532496` job `105855958119`
- push run `35427530049`

Both `conclusion=failure` in ~2–3 seconds. Job JSON:
`runner_id=0`, `runner_name=""`, `runner_group_id=0`. Checkout /
setup-python / pytest never ran. Local suite on this tree: **170
passed** after the AAX-8/AAX-7 additions.

Human check (do not rewrite Ada application code):

1. GitHub → repo Settings → Actions → General: actions enabled,
   "Allow all actions and reusable workflows", Ubuntu GitHub-hosted
   runners allowed.
2. Account Settings → Actions → General for `maziyarid`.
3. Confirm no org/ruleset is blocking hosted runners.

`mergeable_state=unstable` on PR #2 is this Actions signal. Greptile
5/5 on `d7e41a6` is independent of it.


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

## 2026-09-18T23:30Z — runner still never starts (HEAD `872ad1d`)

Same pattern on the mazcontrol-helper SHA:

- pull_request run `35405493093` job `105794291766`
- push run `35405489842` job `105794285774`

Both `conclusion=failure` in ~3 seconds. Job JSON again:
`runner_id=0`, `runner_name=""`, `runner_group_id=0`. Log download
HTTP 404. Checkout / setup-python / pytest never ran.

Do not rewrite Ada application code for a runner that is never
assigned. Local proof remains the test oracle until a hosted runner
actually starts.

