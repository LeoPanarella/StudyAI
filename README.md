# StudyAI — Plataforma Inteligente de Apoio aos Estudos

> **Projeto de Conclusão Integrado (PCI)**  
> **Autor:** Leo Panarella  
> **Tecnologias:** Python (FastAPI), React (Vite + TypeScript), PostgreSQL, Google Gemini API, Docker  

---

## 📌 Sobre o Projeto

Durante a faculdade e rotinas intensas de estudo, é muito comum acumularmos dezenas de livros e apostilas em formato PDF que acabam esquecidos em pastas do computador. O **StudyAI** nasceu como meu Projeto de Conclusão Integrado com o objetivo de transformar esse material passivo em um ambiente de aprendizagem ativa e contínua.

A plataforma resolve três grandes dores do estudante:
1. **Dificuldade em sintetizar conteúdos longos:** A plataforma processa o PDF e gera resumos estruturados com Inteligência Artificial (visão geral, conceitos-chave, tópicos práticos e perguntas de fixação).
2. **Curva do esquecimento:** Transforma o material em flashcards inteligentes utilizando o algoritmo **SuperMemo SM-2** (mesmo algoritmo do Anki), agendando revisões periódicas com base no nível de dificuldade que o aluno sentiu.
3. **Falta de visão associativa dos conteúdos:** Apresenta um **Grafo de Conhecimento Interativo** inspirado no Obsidian, permitindo conectar materiais correlatos, pré-requisitos e desdobramentos de estudo em um mapa visual navegável.

---

## 🚀 Funcionalidades Principais

- **Autenticação Segura de Usuários:** Cadastro e login com senhas criptografadas usando `bcrypt` e tokens JWT (Bearer + Cookie `httpOnly`). Cada aluno enxerga apenas seus próprios materiais.
- **Upload e Extração de Documentos:** Envio de PDFs de até 25 MB com extração de texto puro via biblioteca `PyMuPDF` (execução local sem depender de OCR externo).
- **Resumos Inteligentes:** Geração de sínteses didáticas via Google Gemini com modelo de alta performance (`gemini-3.5-flash-lite`) e processamento assíncrono em segundo plano para não travar o navegador.
- **Flashcards com Repetição Espaçada (SM-2):** 
  - Cartões interativos com efeito 3D de virada (pergunta/resposta).
  - 4 botões de avaliação: *Errei (1)*, *Difícil (2)*, *Bom (3)* e *Fácil (4)* com suporte a atalhos de teclado.
  - Recálculo matemático em tempo real do intervalo de dias e fator de facilidade (*Ease Factor*).
- **Grafo de Conhecimento Interativo (Estilo Obsidian):**
  - Renderizado em **HTML5 Canvas nativo** (60 FPS, sem bibliotecas pesadas).
  - Simulação de forças elásticas: repulsão entre nós, atração por conexões e gravidade central.
  - Suporte completo a **arrastar e soltar (drag & drop)**, zoom com roda do mouse e navegação direta ao clicar no nó.
  - Modos duplo: *Grafo Local* (focado no material aberto) e *Grafo Global* (todo o acervo conectado).

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.13** com **FastAPI:** Framework web assíncrono, moderno e com validação tipada automática.
- **PostgreSQL 17:** Banco de dados relacional robusto com chave estrangeira em cascata e índices otimizados.
- **SQLAlchemy 2.0 & Alembic:** ORM para manipulação das tabelas e migrações versionadas do banco.
- **PyMuPDF (`fitz`):** Leitura de baixo nível e extração de texto direto dos arquivos PDF.
- **Google GenAI SDK:** Integração oficial com os modelos Gemini (`gemini-3.5-flash-lite` e cadeia de fallback).
- **Uvicorn:** Servidor ASGI para produção.

### Frontend
- **React 18** com **Vite:** Build rápido e experiência de desenvolvimento ágil.
- **TypeScript:** Tipagem estática em 100% dos componentes e chamadas de API.
- **React Router 6:** Roteamento dinâmico SPA (Single Page Application).
- **React Markdown & Remark GFM:** Renderização formatada de resumos acadêmicos, tabelas e listas.
- **CSS3 Puro:** Estilização modular com variáveis CSS, sem excesso de frameworks genéricos.

---

## 🎨 Decisões de Design e Interface (UI/UX)

Para a interface, evitei templates genéricos cheios de cores fluorescentes ou emojis infantis. A inspiração visual veio diretamente de duas ferramentas consagradas de estudo e produtividade:
- **Obsidian:** Tema escuro confortável em tons de grafite e carvão (`#14161f` e `#1e2029`), focado em leitura prolongada sem fadiga visual.
- **AnkiWeb:** Cartões de estudo limpos com divisórias nítidas, tipografia legível e feedback claro de repetição espaçada.

---

## ⚙️ Como Rodar o Projeto Localmente

### Pré-requisitos
- Python 3.11+ instalado
- Node.js 18+ instalado
- PostgreSQL rodando localmente (ou via Docker)

### Opção 1: Via Docker Compose (Mais Fácil)
Se você tiver o Docker instalado, pode subir o sistema completo com um único comando:

```bash
# Na raiz do projeto:
docker compose up --build
```
Acesse a aplicação pronta em: `http://localhost:3000`

---

### Opção 2: Rodando Manualmente em Desenvolvimento

#### 1. Configurando o Banco de Dados (PostgreSQL)
Crie um banco de dados chamado `studyai` no seu PostgreSQL local.

#### 2. Configurando o Backend
```bash
cd backend

# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Crie o arquivo de variáveis de ambiente
cp .env.example .env

# Execute as migrações para criar as tabelas no banco
alembic upgrade head

# Inicie o servidor FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
A documentação interativa Swagger ficará acessível em: `http://localhost:8000/api/docs`

#### 3. Configurando o Frontend
Em outro terminal:
```bash
cd frontend

# Instale os pacotes npm
npm install

# Inicie o servidor Vite
npm run dev
```
Abra no navegador em: `http://localhost:5173`

---

## 🔑 Variáveis de Ambiente (`backend/.env`)

| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| `DATABASE_URL` | String de conexão do PostgreSQL | `postgresql+psycopg://usuario:senha@localhost:5432/studyai` |
| `SECRET_KEY` | Chave para assinar os tokens JWT | `uma-chave-secreta-bem-longa-aqui` |
| `GEMINI_API_KEY` | Chave da API gratuita do Google Gemini | Obter em [aistudio.google.com](https://aistudio.google.com) |
| `GEMINI_MODEL` | Modelo padrão de IA | `gemini-3.5-flash-lite` |
| `ENV` | Ambiente de execução | `development` ou `production` |

---

## 📁 Estrutura de Pastas do Projeto

```text
studyai/
├── backend/
│   ├── alembic/              # Scripts versionados de migração do banco
│   ├── app/
│   │   ├── api/              # Rotas da API (auth, materials, flashcards, connections)
│   │   ├── core/             # Configurações (env), segurança (JWT/bcrypt) e rate limits
│   │   ├── db/               # Conexão com banco e sessão SQLAlchemy
│   │   ├── models/           # Entidades do banco de dados (ORM)
│   │   ├── schemas/          # Validações de entrada/saída com Pydantic
│   │   └── services/         # Lógica de negócio: extração de PDF, integração Gemini e algoritmo SM-2
│   ├── uploads/              # Armazenamento local dos PDFs dos alunos
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/              # Cliente HTTP e tipagens TypeScript
│   │   ├── auth/             # Contexto de autenticação e proteção de rotas
│   │   ├── components/       # Componentes reutilizáveis (GraphCanvas, Flashcards, Alertas, Ícones)
│   │   └── pages/            # Telas da aplicação (Login, Meus Materiais, Detalhe do Estudo)
│   ├── index.html
│   └── package.json
├── db/                       # Dump de referência do schema SQL
├── docker-compose.yml        # Orquestração para deploy e testes locais
├── render.yaml               # Configuração para deploy do backend no Render
└── vercel.json               # Configuração para deploy do frontend na Vercel
```

---

## 🧠 Aprendizados e Desafios Superados no PCI

1. **Tratamento de Rate-Limit e Resiliência com a API do Gemini:**  
   No plano gratuito, a API do Google ocasionalmente retorna códigos como `429 (Too Many Requests)` ou `503 (Model Unavailable)`. Para contornar isso, criei uma rotina de retry com modelo de fallback automático: se o modelo principal oscilar, o backend tenta automaticamente o modelo secundário sem frustrar o usuário.
2. **Implementação Real do Algoritmo SM-2:**  
   Em vez de apenas sortear flashcards, estudei a fórmula matemática original do SuperMemo-2 criada por Piotr Woźniak. O cálculo leva em conta as repetições consecutivas, a nota de 1 a 4 informada pelo aluno e o fator de facilidade (mínimo de 1.3), gerando intervalos reais em dias.
3. **Desenvolvimento do Grafo Interativo com HTML5 Canvas Puro:**  
   Para evitar bibliotecas externas pesadas e dependências que quebrassem em navegadores diferentes, implementei a física do grafo manualmente usando o loop `requestAnimationFrame`. As leis de Hooke (molas) e repulsão eletrostática simples garantem que os nós se organizem de forma orgânica e fluida na tela.

---

## 👤 Autor

**Leo Panarella**  
Projeto de Conclusão Integrado (PCI) — 2026.
