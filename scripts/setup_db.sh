#!/usr/bin/env bash
# Provisiona um PostgreSQL LOCAL de desenvolvimento (Debian/Ubuntu) e aplica as migrações.
# Em produção, crie o banco do seu jeito e apenas aponte DATABASE_URL no backend/.env.
set -euo pipefail
cd "$(dirname "$0")/.."

DB_NAME="${DB_NAME:-studyai}"
DB_USER="${DB_USER:-studyai}"
DB_PASS="${DB_PASS:-studyai_dev_password}"

if ! command -v psql >/dev/null; then
  echo ">> Instalando PostgreSQL..."
  sudo apt-get update -qq && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq postgresql postgresql-contrib
fi

echo ">> Iniciando cluster..."
sudo pg_ctlcluster 17 main start 2>/dev/null || true

echo ">> Criando role/banco (idempotente)..."
sudo -u postgres psql -v ON_ERROR_STOP=0 -qc "CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASS}';" 2>/dev/null || true
sudo -u postgres psql -v ON_ERROR_STOP=0 -qc "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};" 2>/dev/null || true

if [ -f db/backup.sql ]; then
  echo ">> Restaurando db/backup.sql..."
  PGPASSWORD="$DB_PASS" psql -h 127.0.0.1 -U "$DB_USER" -d "$DB_NAME" -q -f db/backup.sql >/dev/null
fi

echo ">> Aplicando migrações (alembic upgrade head)..."
cd backend && .venv/bin/alembic upgrade head
echo ">> Banco pronto."
