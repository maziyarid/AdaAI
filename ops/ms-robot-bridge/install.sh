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
ok=0
for _ in $(seq 1 30); do
  if curl -fsS --max-time 2 http://127.0.0.1:9110/healthz >/tmp/ms-robot-bridge-health.json 2>/dev/null; then
    ok=1
    break
  fi
  sleep 0.2
done
if [ "$ok" -ne 1 ]; then
  systemctl status ms-robot-bridge.service --no-pager -l || true
  exit 1
fi
cat /tmp/ms-robot-bridge-health.json
echo
echo "Rollback backup: $BACKUP"
