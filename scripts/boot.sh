#!/usr/bin/env bash
set -e

echo "=== 1. Instalando e configurando PostgreSQL ==="
if ! command -v psql >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq postgresql postgresql-contrib
fi

echo "=== 2. Iniciando PostgreSQL Cluster ==="
sudo pg_ctlcluster 17 main start || true

echo "=== 3. Configurando usuário e banco ==="
sudo -u postgres psql -c "CREATE USER studyai WITH SUPERUSER PASSWORD 'studyai_dev_password';" || true
sudo -u postgres psql -c "CREATE DATABASE studyai OWNER studyai;" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE studyai TO studyai;" || true
sudo -u postgres psql -d studyai -c "GRANT ALL ON SCHEMA public TO studyai;" || true

echo "=== 4. Restaurando dados e migrações ==="
PGPASSWORD="studyai_dev_password" psql -h 127.0.0.1 -U studyai -d studyai -f /home/user/studyai/db/backup.sql >/dev/null 2>&1 || true
sudo -u postgres psql -d studyai -c "ALTER TABLE ai_jobs ADD COLUMN IF NOT EXISTS focus VARCHAR(500);" || true

echo "=== 5. Instalando dependências Python ==="
python3 -m pip install -r /home/user/studyai/backend/requirements.txt -q

echo "=== 6. Sincronizando senhas de teste ==="
python3 -c "
import psycopg, bcrypt
pwd = 'senha-forte-123'.encode('utf-8')
hashed = bcrypt.hashpw(pwd, bcrypt.gensalt()).decode('utf-8')
conn = psycopg.connect('postgresql://studyai:studyai_dev_password@127.0.0.1:5432/studyai')
cur = conn.cursor()
cur.execute('UPDATE users SET password_hash = %s WHERE email IN (%s, %s);', (hashed, 'leo@gmail.com', 'maria@exemplo.com'))
cur.execute('UPDATE materials SET user_id = 2 WHERE user_id = 1;')
conn.commit()
print('Credenciais e materiais sincronizados com sucesso.')
"

echo "=== 7. Compilando Frontend SPA ==="
cd /home/user/studyai/frontend
npm install --no-audit --no-fund -q
npm run build

echo "=== Pronto para iniciar servidores ==="
