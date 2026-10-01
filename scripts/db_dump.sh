#!/usr/bin/env bash
# Faz um dump completo (schema + dados) do banco de desenvolvimento em db/backup.sql.
set -euo pipefail
cd "$(dirname "$0")/.."
PGPASSWORD="${DB_PASS:-studyai_dev_password}" pg_dump -h 127.0.0.1 -U "${DB_USER:-studyai}" -d "${DB_NAME:-studyai}" \
  --clean --if-exists --no-owner --no-privileges > db/backup.sql
echo "Dump salvo em db/backup.sql ($(wc -c < db/backup.sql) bytes)"
