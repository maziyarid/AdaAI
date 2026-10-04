#!/usr/bin/env bash
set -euo pipefail
if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root/sudo." >&2
  exit 2
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="$ROOT/ops/ada-telegram-bot"
QALAM="$ROOT/skills/qalam/RELEASE.json"
DEST=/opt/ada-telegram-bot

install -d -o root -g root -m 0755 "$DEST"
install -d -o root -g root -m 0700 "$DEST/backups"
BACKUP="$(mktemp -d "$DEST/backups/$(date -u +%Y%m%dT%H%M%SZ)-pre-install.XXXXXX")"
chown root:root "$BACKUP"
chmod 0700 "$BACKUP"
install -d -o adabot -g adabot -m 0750 /var/lib/ada-telegram-bot
for f in bot.py check_config.py feedback_admin.py healthcheck.py send_alert.py system_prompt.txt RUNBOOK.md README.md qalam-release.json; do
  [ -e "$DEST/$f" ] && cp -p "$DEST/$f" "$BACKUP/$f" || true
done

for f in bot.py check_config.py feedback_admin.py healthcheck.py send_alert.py; do
  install -o root -g root -m 0755 "$SRC/$f" "$DEST/$f"
done
for f in system_prompt.txt RUNBOOK.md README.md; do
  install -o root -g root -m 0644 "$SRC/$f" "$DEST/$f"
done
install -o root -g root -m 0644 "$QALAM" "$DEST/qalam-release.json"
install -o root -g root -m 0644 "$SRC/systemd/ada-telegram-bot.service" /etc/systemd/system/ada-telegram-bot.service
install -o root -g root -m 0755 "$SRC/bin/ada-botctl" /usr/local/bin/ada-botctl
install -o root -g root -m 0755 "$SRC/bin/ada-bot-health" /usr/local/bin/ada-bot-health
install -o root -g root -m 0755 "$SRC/bin/ada-send-alert" /usr/local/bin/ada-send-alert
install -o root -g root -m 0755 "$SRC/bin/ada-bot-set-token" /usr/local/sbin/ada-bot-set-token

[ -e /var/lib/ada-telegram-bot/state.sqlite3 ] && chown adabot:adabot /var/lib/ada-telegram-bot/state.sqlite3 && chmod 0600 /var/lib/ada-telegram-bot/state.sqlite3 || true
systemctl daemon-reload
echo "Installed AdaLLMbot runtime. Token activation remains a separate operator action."
echo "Rollback backup: $BACKUP"
