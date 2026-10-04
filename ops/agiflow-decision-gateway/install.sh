#!/usr/bin/env bash
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Run as root/sudo." >&2; exit 2; }
id adabot >/dev/null
[ "$(id -u adabot)" -ne 0 ] || { echo "Bot account must be non-root." >&2; exit 2; }
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST=/opt/ada-decision-gateway
if ! id ada-decision-gateway >/dev/null 2>&1; then
  useradd --system --no-create-home --shell /usr/sbin/nologin --gid adabot ada-decision-gateway
else
  gateway_uid="$(id -u ada-decision-gateway)"
  gateway_gid="$(id -g ada-decision-gateway)"
  expected_gid="$(id -g adabot)"
  gateway_shell="$(getent passwd ada-decision-gateway | awk -F: 'NR==1 {print $7}')"
  gateway_groups="$(id -G ada-decision-gateway)"
  [ "$gateway_uid" -ne 0 ] || { echo "Gateway account must be non-root." >&2; exit 2; }
  [ "$gateway_gid" -eq "$expected_gid" ] || { echo "Gateway account has unexpected primary group." >&2; exit 2; }
  case "$gateway_shell" in
    /usr/sbin/nologin|/sbin/nologin|/bin/false) ;;
    *) echo "Gateway account must use a non-login shell." >&2; exit 2 ;;
  esac
  [ "$gateway_groups" = "$expected_gid" ] || { echo "Gateway account has unexpected supplementary groups." >&2; exit 2; }
  [ "$(getent passwd "$gateway_uid" | wc -l)" -eq 1 ] || { echo "Gateway UID must not be shared." >&2; exit 2; }
fi
install -d -o root -g root -m 0755 "$DEST"
BACKUP="$DEST/backups/$(date -u +%Y%m%dT%H%M%SZ)"
install -d -o root -g root -m 0700 "$BACKUP"
for name in gateway.py README.md; do
  [ ! -e "$DEST/$name" ] || cp -p "$DEST/$name" "$BACKUP/$name"
done
[ ! -e /etc/systemd/system/ada-decision-gateway.service ] || cp -p /etc/systemd/system/ada-decision-gateway.service "$BACKUP/"
install -o root -g root -m 0755 "$SRC/gateway.py" "$DEST/gateway.py"
install -o root -g root -m 0644 "$SRC/README.md" "$DEST/README.md"
install -o root -g root -m 0644 "$SRC/ada-decision-gateway.service" /etc/systemd/system/
if [ ! -e /etc/ada-decision-gateway.env ]; then
  install -o root -g root -m 0600 "$SRC/gateway.env.example" /etc/ada-decision-gateway.env
fi
systemctl daemon-reload
echo "Installed disabled source. No service was started or enabled."
