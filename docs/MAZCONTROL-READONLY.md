# Least-privilege mazcontrol read-only inspection (AAX-3)

This is the smallest extra access Ada needs to finish AAX-3 AC2/AC3
and AAX-7 source-vs-live reconciliation. It is **not** installed on
the VPS yet. Do not treat this document as live evidence.

`grok-ada-readonly` (`mistralops`, MCP `readOnly=true`) already
reaches `/opt/maziyar-control-core` and can `ls` / `cat` / `grep` /
`stat` / `wc`. It still cannot:

- `systemctl show` (ActiveState/SubState)
- `sha256sum`
- MariaDB `SHOW TABLES` / `SHOW CREATE TABLE` / `information_schema`

Do **not** clear viewer `readOnly`. Do **not** grant a root shell.
Do **not** allow arbitrary `mysql`. Do **not** read
`/etc/maziyar-control-core.env` into git.

## Preferred design

One hardcoded helper, run as `mazcontrol` (the existing control-core
Unix user), not as root.

| Piece | Path | Mode |
| --- | --- | --- |
| Helper | `/usr/local/bin/ada-inspect` | `root:root` `0755` |
| Sudoers | `/etc/sudoers.d/ada-inspect` | `root:root` `0440` |
| Repo copy | `ops/mazcontrol-readonly/ada-inspect` | source of truth |

`mazcontrol` can already read `/etc/maziyar-control-core.env`
(`0640 root:mazcontrol`). That file stays unread by `mistralops`.

### Allowed verbs

- `units` — `systemctl show` for a hardcoded unit list
- `hashes` — `sha256sum` of hardcoded source/unit files
- `tables` — `SHOW TABLES` plus `ada_%` / `pd_%` presence
- `create TABLE` / `columns TABLE` — schema only, allowlisted names
- `schema` — live source tables CREATE + columns

### Forbidden

- `systemctl start/stop/restart/kill`
- SQL `INSERT` / `UPDATE` / `DELETE` / `DROP` / `ALTER` / `CREATE`
- row dumps, `SELECT *`, payload JSON
- `cat` of env files / API tokens / SSH keys
- package install, file writes, visudo, `/bin/sh`

## Install (human, on the VPS)

```bash
install -o root -g root -m 0755 ops/mazcontrol-readonly/ada-inspect \
  /usr/local/bin/ada-inspect
visudo -c -f ops/mazcontrol-readonly/sudoers.example
install -o root -g root -m 0440 ops/mazcontrol-readonly/sudoers.example \
  /etc/sudoers.d/ada-inspect
```

MCP `grok-temp.toml` (path
`/var/lib/mcpvps/.config/ssh-mcp/grok-temp.toml`, unread by viewer)
then needs one allowlist addition so `read-command` accepts:

```text
sudo -n -u mazcontrol /usr/local/bin/ada-inspect
```

Keep `readOnly=true`. Do not add raw `mysql`, `sha256sum`, or
unfiltered `systemctl` if the helper is installed — the helper is
the allowlist.

## Why a helper instead of widening the classifier

The current ssh-mcp policy refuses some otherwise-safe commands
because the profile is `readOnly`. Widening `systemctl` / `mysql`
to the viewer would also allow argument injection. A verb-only
binary is smaller.

## After install, AAX-3 should capture

1. `ada-inspect units` — ActiveState/SubState/MainPID
2. `ada-inspect hashes` — `control_core.py` sha256
3. `ada-inspect tables` — live `ada_*` presence/absence (AC3)
4. `ada-inspect create pending_external_sync`
5. `ada-inspect create jobs` / `schedules` (lease columns)
6. If present: `pd_worker_runs` / `pd_outbox` CREATE (AAX-7)

Still never applied: repo `ada_*` SQL.
