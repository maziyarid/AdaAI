#!/usr/bin/env bash
set -euo pipefail
if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root/sudo." >&2
  exit 2
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="$ROOT/ops/ms-robot-bridge"
DEST=/srv/ms-robot-bridge
TS="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$DEST/backups/$TS-pre-install"

mkdir -p "$BACKUP"
for f in bridge.py event-envelope.schema.json CONTRACT.md README.md; do
  [ -e "$DEST/$f" ] && cp -p "$DEST/$f" "$BACKUP/$f" || true
done
install -o root -g msrobot-bridge -m 0750 "$SRC/bridge.py" "$DEST/bridge.py"
install -o root -g msrobot-bridge -m 0640 "$SRC/event-envelope.schema.json" "$DEST/event-envelope.schema.json"
install -o root -g msrobot-bridge -m 0640 "$SRC/CONTRACT.md" "$DEST/CONTRACT.md"
install -o root -g msrobot-bridge -m 0640 "$SRC/README.md" "$DEST/README.md"
install -o root -g root -m 0644 "$SRC/systemd/ms-robot-bridge.service" /etc/systemd/system/ms-robot-bridge.service
systemctl daemon-reload
systemctl restart ms-robot-bridge.service
curl -fsS --max-time 5 http://127.0.0.1:9110/healthz
echo
echo "Rollback backup: $BACKUP"
