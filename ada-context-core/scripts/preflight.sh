#!/usr/bin/env bash
set -euo pipefail
printf 'Ada Phase-1 preflight\n'
printf 'Host: '; hostname
printf 'Kernel: '; uname -sr
printf 'CPU: '; nproc
free -h || true
df -h / /var /srv 2>/dev/null || true
python3 --version || true
psql --version || echo 'PostgreSQL client not installed yet'
printf '\nListening candidate ports:\n'
ss -ltn 2>/dev/null | grep -E ':(8791|8792)\b' || echo '8791/8792 appear free'
printf '\nIMPORTANT: Do not restart vps-mcp/wp-mcp control-plane services during this installation.\n'
