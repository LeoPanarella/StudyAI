# Guia de Deploy em Produção — StudyAI

Este documento contém o passo a passo direto para colocar a plataforma **StudyAI** em produção, com persistência real em PostgreSQL, certificados SSL/HTTPS automáticos e orquestração por containers.

---

## Opção A: Deploy em VPS (DigitalOcean / Hetzner / AWS Lightsail / Linode)

Esta é a opção recomendada para o TCC e negócios reais, oferecendo controle total com baixo custo (a partir de $4-$6/mês).

### 1. Requisitos na Máquina
Acesse seu servidor Ubuntu via SSH e instale Docker e Docker Compose:
```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### 2. Clonar o Projeto e Configurar o `.env`
No servidor, clone o repositório e crie o arquivo `.env`:
```bash
git clone <URL_DO_REPOSITORIO> studyai
cd studyai
cp backend/.env.example .env
```

Edite o `.env` gerando credenciais reais:
```bash
# Gere uma SECRET_KEY segura:
openssl rand -hex 32

# Configure no arquivo .env:
POSTGRES_DB=studyai
POSTGRES_USER=studyai_admin
POSTGRES_PASSWORD=DefinaUmaSenhaSuperForte!123
SECRET_KEY=<CHAVE_GERADA_ACIMA>
COOKIE_SECURE=true
GEMINI_API_KEY=AIzaSy...SuaChaveRealDoGoogleGemini...
GEMINI_MODEL=gemini-2.5-flash
GEMINI_FALLBACK_MODELS=gemini-2.0-flash,gemini-1.5-flash,gemini-1.5-pro
PORT=80
```

### 3. Subir a Aplicação com Docker Compose
Execute:
```bash
docker compose up -d --build
```
* O banco de dados PostgreSQL iniciará com volume persistente.
* O backend executará automaticamente as migrações do banco (`alembic upgrade head`) antes de subir a API na porta `8000`.
* O Nginx servirá o frontend na porta `80` e fará proxy transparente de `/api/` para o backend.

### 4. Configurar HTTPS Automático com Caddy (ou Certbot)
Para obter HTTPS grátis com certificado Let's Encrypt em 2 minutos, instale o **Caddy**:
```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLF 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLF 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy -y
```

Edite o arquivo `/etc/caddy/Caddyfile`:
```caddy
seudominio.com.br {
    reverse_proxy 127.0.0.1:80
}
```
Reinicie o Caddy:
```bash
sudo systemctl reload caddy
```
O Caddy gerará e renovará os certificados SSL automaticamente.

---

## Opção B: Deploy em PaaS (Render / Railway)

### 1. PostgreSQL Gerenciado
1. No dashboard da Render ou Railway, crie uma instância de **PostgreSQL**.
2. Copie a `Internal Database URL` fornecida.

### 2. Backend (FastAPI Web Service)
1. Crie um novo **Web Service** apontando para o diretório raiz ou `/backend`.
2. Comando de inicialização (`Start Command`):
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
   ```
3. Variáveis de ambiente configuradas no painel:
   * `DATABASE_URL`: URL do PostgreSQL criado no passo 1.
   * `SECRET_KEY`: string aleatória de 32 caracteres.
   * `COOKIE_SECURE`: `true`.
   * `CORS_ORIGINS`: `https://app.seudominio.com` (URL do frontend).
   * `GEMINI_API_KEY`: sua chave de IA do Google Gemini.
   * `GEMINI_MODEL`: `gemini-2.5-flash`.
   * `GEMINI_FALLBACK_MODELS`: `gemini-2.0-flash,gemini-1.5-flash,gemini-1.5-pro`.

### 3. Frontend (React / Vite Static Site)
1. Crie um novo **Static Site** apontando para o diretório `/frontend`.
2. Build command: `npm install && npm run build`.
3. Publish directory: `dist`.
4. Configure a variável de ambiente:
   * `VITE_API_URL`: URL do backend (caso não utilize proxy reverso).

---

## Verificação e Healthcheck Pós-Deploy

Para confirmar se o deploy está 100% saudável:
```bash
curl -I https://seudominio.com.br/api/health
```
Resposta esperada:
```json
HTTP/2 200
{"status":"ok","database":"ok","env":"production"}
```
