#!/usr/bin/env bash
# Sobe API (porta 8000) e frontend (porta 5173) em desenvolvimento.
set -euo pipefail
cd "$(dirname "$0")/.."

[ -d backend/.venv ] || { python3 -m venv backend/.venv && backend/.venv/bin/pip install -q -r backend/requirements.txt; }
[ -d frontend/node_modules ] || (cd frontend && npm install --silent --no-audit --no-fund)
[ -f backend/.env ] || { echo "Crie backend/.env a partir de backend/.env.example"; exit 1; }

(cd backend && .venv/bin/alembic upgrade head)
(cd backend && .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir app) &
(cd frontend && npx vite --host 0.0.0.0 --port 5173) &
wait
