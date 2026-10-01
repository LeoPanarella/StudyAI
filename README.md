# StudyAI

Sistema web de estudos com IA: upload de PDFs, extração de texto, resumos, flashcards
de revisão espaçada, tutor de IA contextualizado e plano de estudos.

**Stack:** Python 3.13 · FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL 17 · PyMuPDF · React 18 + Vite + TypeScript · Google Gemini (fases 3–5)

## Estado do projeto

| # | Funcionalidade | Status |
|---|----------------|--------|
| 1 | Cadastro e login (JWT Bearer + cookie httpOnly, senha com bcrypt) | Concluído |
| 2 | Upload de PDF + extração de texto (PyMuPDF), persistido no PostgreSQL | Concluído |
| 3 | Resumo via IA (Gemini), gerado em segundo plano com retry/fallback | Concluído |
| 4 | Flashcards via IA + revisão espaçada (SM-2, virar cartão 3D, 4 notas) | Concluído |
| 4.5 | Conexões de Estudo bidirecionais (estilo Obsidian) + Geração de Flashcards com foco temático | Concluído |
| 5 | Tutor de IA (chat com contexto do material) | Próxima etapa |
| 6 | Plano de estudos (CRUD) | Em planejamento |

## Estrutura

```
studyai/
├── backend/               # API FastAPI
│   ├── app/
│   │   ├── api/           # rotas: auth, materials (+ deps de autenticação)
│   │   ├── core/          # config (env) e segurança (bcrypt, JWT)
│   │   ├── db/            # engine/sessão SQLAlchemy
│   │   ├── models/        # User, Material, Summary, Flashcard, StudyPlan(+Item)
│   │   ├── schemas/       # modelos Pydantic de entrada/saída
│   │   └── services/      # pdf_extractor (PyMuPDF), jobs (execução em 2º plano), ai/ (gemini, summarizer)
│   ├── alembic/versions/  # migrações versionadas do banco
│   ├── uploads/           # PDFs originais (uploads/<user_id>/<uuid>.pdf) — fora do git
│   └── .env               # DATABASE_URL, SECRET_KEY, GEMINI_API_KEY...
├── frontend/              # React + Vite (proxy /api -> :8000 em dev)
├── db/schema.sql          # schema de referência gerado do banco (para revisão/DBA)
├── samples/               # PDF de exemplo para testes
└── scripts/               # setup_db.sh, dev.sh, db_dump.sh
```

## Rodando

```bash
# 1) Banco: crie um PostgreSQL e um banco vazio do seu jeito. Para dev local, há um atalho:
./scripts/setup_db.sh

# 2) Backend
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env           # edite DATABASE_URL e SECRET_KEY
.venv/bin/alembic upgrade head # cria as tabelas
.venv/bin/uvicorn app.main:app --reload --port 8000

# 3) Frontend
cd frontend
npm install
npm run dev                    # http://localhost:5173  (proxy /api -> 8000)
```

Docs interativas da API: `http://localhost:8000/api/docs`

## API (fase atual)

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/auth/register` | cria conta e inicia sessão |
| POST | `/api/auth/login` | inicia sessão (cookie httpOnly) |
| POST | `/api/auth/logout` | encerra sessão |
| GET | `/api/auth/me` | usuário logado |
| GET | `/api/materials` | lista materiais do usuário |
| POST | `/api/materials` | upload (multipart `file`, `title` opcional) → extrai texto |
| GET | `/api/materials/{id}` | detalhe + prévia do texto |
| GET | `/api/materials/{id}/content` | texto extraído completo |
| POST | `/api/materials/{id}/summary` | enfileira geração do resumo (202 + job); acompanhe em `summary_job` do detalhe |
| GET | `/api/materials/{id}/summary` | resumo atual (404 se ainda não houver) |
| GET | `/api/materials/{id}/flashcards` | lista flashcards do material (total, pendentes de revisão hoje) |
| POST | `/api/materials/{id}/flashcards` | cria flashcard manual ({question, answer}) |
| POST | `/api/materials/{id}/flashcards/generate` | enfileira geração com IA (aceita `{ "focus": "..." }`) |
| GET | `/api/materials/{id}/flashcards/study` | cartões para sessão de estudo (?mode=due\|all) |
| POST | `/api/flashcards/{id}/review` | submete nota de revisão ({rating: 0..3}) e recalcula SM-2 |
| PATCH | `/api/flashcards/{id}` | edita pergunta ou resposta |
| DELETE | `/api/flashcards/{id}` | exclui flashcard |
| GET | `/api/materials/{id}/connections` | lista materiais conectados (saída) e backlinks (entrada) |
| POST | `/api/materials/{id}/connections` | conecta a outro material ({target_material_id, relation_type, note}) |
| DELETE | `/api/connections/{id}` | remove conexão bidirecional |
| PATCH | `/api/materials/{id}` | renomear |
| DELETE | `/api/materials/{id}` | excluir (cascata em resumo/flashcards + arquivo) |

## Como a IA funciona (fases 3 e 4)

- **Camada isolada** em `app/services/ai/`: `gemini.py` (cliente com retry/fallback), `summarizer.py` (resumos) e `flashcards_generator.py` (extração de cartões).
- **Execução em segundo plano**: `POST .../summary` e `POST .../flashcards/generate` criam registros em `ai_jobs` e respondem `202`; o frontend faz polling do detalhe a cada 2,5 s. O estado vive no banco (`ai_jobs`), sobrevivendo a recarregamentos de página.
- **Flashcards & Repetição Espaçada (SM-2)**:
  - Os flashcards são gerados em JSON estruturado com perguntas focadas em recordação ativa (*Active Recall*) e no princípio da informação mínima.
  - Cada revisão submete uma avaliação de 0 a 3 (**Errei**, **Difícil**, **Bom**, **Fácil**).
  - O algoritmo SM-2 atualiza dinamicamente o fator de facilidade (`ease_factor`), o intervalo (`interval_days`), as repetições e agenda a próxima revisão (`next_review_at`) no PostgreSQL.
- **Resiliência do Gemini**: *Round-robin* com backoff crescente por até 8 rodadas entre múltiplos modelos de fallback para contornar oscilações e códigos 503/429 do tier gratuito.
- **Prompt** em português, com estrutura fixa (Visão geral · Conceitos-chave · Pontos principais · Para fixar), instruído a usar somente o conteúdo do material.
- Em produção, recomenda-se **ativar faturamento no projeto Google (pay-as-you-go)**: os limites sobem ordens de grandeza e as rejeições por "alta demanda" praticamente desaparecem.

## Decisões de segurança

- Senhas: bcrypt (12 rounds); nunca armazenadas em texto puro.
- Sessão: JWT assinado (HS256). O SPA envia o token no header `Authorization: Bearer` (guardado em `localStorage`) — necessário porque em previews embutidos em iframe os navegadores bloqueiam cookies de terceiros. A API também emite o token em cookie `httpOnly` (`SameSite=None; Secure; Partitioned` atrás de HTTPS, `Lax` em HTTP local) como canal secundário. Tokens expiram em 7 dias.
- Markdown gerado pela IA é renderizado sem HTML bruto (react-markdown), o que elimina XSS por conteúdo gerado.
- `GEMINI_API_KEY` fica só em `backend/.env` (ignorado pelo git) e nunca é registrada em logs.
- Login com mensagem genérica (não revela se o e-mail existe); e-mails normalizados em minúsculas.
- Todo acesso a material filtra por `user_id`; material de outro usuário responde 404.
- Upload: extensão + assinatura binária `%PDF-` (*magic bytes*) verificadas, limite de tamanho (`MAX_UPLOAD_MB`) com leitura em blocos, PDFs protegidos por senha rejeitados com mensagem clara.
- Rate Limiting em memória nas rotas críticas: mitigação de força bruta em `/api/auth/login` (10 req/min) e proteção de cotas da IA em `/api/materials/{id}/summary` e `/api/materials/{id}/flashcards/generate` (6 req/min).
- O banco é acessado apenas via `DATABASE_URL`; a app não precisa de superusuário — só de um role dono do banco.

## Limitações e Próximos Passos (Roadmap TCC & Startup)

Ordenado por impacto de negócio e relevância pedagógica:

1. **Tutor de IA Contextualizado (Chat Socrático)**:
   - *Impacto: Máximo*. Interação conversacional direta com o PDF carregado, permitindo ao estudante tirar dúvidas em linguagem natural, pedir exemplos e explicações passo a passo.
2. **OCR para PDFs Digitalizados / Imagens**:
   - *Impacto: Alto*. Extração de texto de PDFs escaneados ou imagens via Tesseract / Gemini Multimodal, cobrindo apostilas digitalizadas e livros físicos fotografados.
3. **Busca Semântica com Embeddings (RAG com pgvector)**:
   - *Impacto: Alto*. Substituir o ranqueamento atual por contagem de termos por busca vetorial semântica usando `pgvector` nativo no PostgreSQL.
4. **Ingestão de Múltiplos Formatos (Além de PDF)**:
   - *Impacto: Médio-Alto*. Suporte a páginas web (URL scraping), arquivos Markdown, EPUB e transcrição de áudios de aulas.
5. **Módulo de Cronograma e Trilhas de Estudo (Fase 6)**:
   - *Impacto: Médio*. As tabelas relacionais `study_plans` e `study_plan_items` já estão modeladas e versionadas no banco; o próximo passo é a interface visual de calendário e metas diárias.

## Deploy em Produção

O projeto conta com orquestração completa por Docker Compose:
- Consulte o guia passo a passo em [DEPLOY.md](./DEPLOY.md) para subir em VPS (com HTTPS automático via Caddy) ou em plataformas PaaS (Render / Railway).
- Comando único de subida: `docker compose up -d --build`.
