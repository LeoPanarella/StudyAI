#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/user/studyai"
cd "$ROOT"

echo "=== 1. Checking / Installing PostgreSQL ==="
if ! command -v psql >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq postgresql postgresql-contrib
fi

echo "=== 2. Starting PostgreSQL Cluster ==="
sudo pg_ctlcluster 17 main start 2>/dev/null || true

echo "=== 3. Ensuring Database and Role ==="
sudo -u postgres psql -v ON_ERROR_STOP=0 -qc "CREATE ROLE studyai WITH LOGIN PASSWORD 'studyai_dev_password';" 2>/dev/null || true
sudo -u postgres psql -v ON_ERROR_STOP=0 -qc "CREATE DATABASE studyai OWNER studyai;" 2>/dev/null || true

echo "=== 4. Setting up Python venv ==="
if [ ! -f "$ROOT/backend/.venv/bin/uvicorn" ]; then
  python3 -m venv "$ROOT/backend/.venv"
  "$ROOT/backend/.venv/bin/pip" install -q -r "$ROOT/backend/requirements.txt"
fi

echo "=== 5. Applying Alembic Migrations ==="
if [ -f "$ROOT/db/backup.sql" ]; then
  PGPASSWORD=studyai_dev_password psql -h 127.0.0.1 -U studyai -d studyai -q -f "$ROOT/db/backup.sql" 2>/dev/null || true
fi
cd "$ROOT/backend"
"$ROOT/backend/.venv/bin/alembic" upgrade head

echo "=== 6. Setting up Frontend node_modules ==="
cd "$ROOT/frontend"
if [ ! -d "$ROOT/frontend/node_modules" ]; then
  npm install --silent --no-audit --no-fund
fi

echo "=== Environment Ready! ==="
