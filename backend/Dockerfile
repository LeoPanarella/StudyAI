FROM python:3.13-slim

WORKDIR /app

# Instala dependências do sistema necessárias para compilação e PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cria diretório de uploads padrão
RUN mkdir -p uploads

EXPOSE 8000

# Script de inicialização: roda migrações do Alembic e sobe a API
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"]
