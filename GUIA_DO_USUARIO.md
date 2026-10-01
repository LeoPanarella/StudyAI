# StudyAI — Pacote de Entrega: Fase de Construção (Iteração 1)
## Guia do Usuário, Diagrama de Implantação e Roteiro de Demonstração em Vídeo

**Curso / Disciplina:** Engenharia de Software / Projeto de Empreendedorismo & TCC  
**Projeto:** StudyAI — Plataforma Inteligente de Aprendizagem Ativa e Repetição Espaçada  
**Fase:** Construção • **Iteração:** 1  

---

# PARTE 1: GUIA DO USUÁRIO (MANUAL DE OPERAÇÃO)

Bem-vindo ao **StudyAI**, seu ambiente inteligente de estudos projetado para maximizar a retenção de conteúdo complexo através de Inteligência Artificial, Recordação Ativa (*Active Recall*), Repetição Espaçada (Algoritmo SM-2) e Conexões Associativas de Conhecimento (estilo Obsidian).

---

### 1. Primeiros Passos: Cadastro e Acesso Seguro

O StudyAI adota autenticação individual para garantir que seus PDFs, notas e histórico de repetição espaçada permaneçam restritos à sua conta:

1. **Acessando a Plataforma:**
   * Abra seu navegador web e acerte o endereço do sistema (ex.: `http://localhost:5173` em ambiente local ou o domínio de produção `https://seudominio.com.br`).
2. **Criando sua Conta:**
   * Na tela inicial de Login, clique em **"Criar conta"**.
   * Preencha seu **Nome Completo**, **E-mail** e uma **Senha segura** (mínimo de 8 caracteres).
   * Clique em **"Cadastrar"**. Você será autenticado e redirecionado automaticamente para o painel principal.
3. **Fazendo Login:**
   * Insira seu e-mail e senha cadastrados e clique em **"Entrar"**.
   * *Conta de Teste/Demonstração pré-configurada:*  
     **E-mail:** `maria@exemplo.com` | **Senha:** `senha-forte-123`
4. **Alternância de Tema (Modo Escuro / Modo Claro):**
   * No canto superior direito da barra de navegação, clique no ícone de **Lua / Sol** para alternar entre o **Modo Claro** e o **Modo Escuro Grafite (#1e1e1e)** (estética inspirada no Obsidian, sem cansaço visual). Sua escolha fica salva automaticamente no navegador.

---

### 2. Gestão de Materiais de Estudo (Upload e Extração)

O ponto de partida no StudyAI é o envio de apostilas, artigos científicos ou livros em formato PDF:

1. **Enviando um novo PDF:**
   * Na página **"Meus materiais"**, clique no botão **"+ Enviar PDF"**.
   * Clique na área tracejada para selecionar o arquivo no seu computador (ou arraste o arquivo até a área).
   * *(Opcional)* Você pode personalizar o **Título do material** ou deixar que o sistema gere um título limpo com base no nome do arquivo.
   * Clique em **"Salvar e extrair texto"**.
2. **Validação Automática e Segurança:**
   * O sistema aceita arquivos de até **25 MB**.
   * Todos os uploads passam por verificação binária de assinatura (*magic bytes* `%PDF-`), rejeitando arquivos falsos ou corrompidos.
   * O texto vetorial é extraído instantaneamente via PyMuPDF e indexado no banco de dados com a contagem de páginas e caracteres.
3. **Organização da Biblioteca:**
   * Na listagem, cada material exibe o número de páginas, tamanho, data de envio e badges indicando se o resumo já foi gerado e quantos flashcards existem na fila.

---

### 3. Sínteses e Resumos Cognitivos com IA

Transforme documentos volumosos em sínteses pedagógicas estruturadas:

1. **Acessando o Detalhe do Material:**
   * Na lista de materiais, clique sobre o cartão do documento desejado.
2. **Gerando o Resumo:**
   * Na aba **"Resumo"**, clique no botão **"Gerar resumo com IA"**.
   * O sistema criará um job em segundo plano utilizando o modelo **Google Gemini**. Uma barra animada indicará que a IA está lendo o documento.
   * *Tempo estimado:* entre 5 a 20 segundos. Você pode navegar para outras abas ou sair da página sem perder o processo.
3. **Leitura Editorial Estruturada:**
   * O resumo gerado adota uma metodologia em 4 blocos:
     * **Visão Geral:** Contextualização e objetivo central do texto.
     * **Conceitos-Chave:** Definições essenciais em destaque.
     * **Pontos Principais:** Tópicos explicados com clareza.
     * **Para Fixar:** Conclusões práticas para retenção.
4. **Regeneração:**
   * Caso queira atualizar a síntese, basta clicar em **"Regenerar"**.

---

### 4. Flashcards & Repetição Espaçada (Algoritmo SM-2)

A funcionalidade central para garantir memorização duradoura:

#### 4.1. Geração Automática com IA (Com Foco Personalizado)
1. Na página do material, acerte a aba **"Flashcards SM-2"**.
2. Clique no botão **"Gerar com foco"** (ou "Gerar com IA"):
   * **Geração Geral:** Deixe o campo em branco para que a IA identifique os conceitos mais importantes de todo o documento.
   * **Geração com Foco Temático (Recurso Exclusivo):** Digite o assunto ou capítulo específico que deseja focar (ex.: *"Focar estritamente nas camadas do modelo OSI e encapsulamento TCP/IP"*). A IA priorizará os trechos do PDF correspondentes e criará perguntas exclusivamente ligadas ao tema.
3. Clique em **"Iniciar geração"**. Em instantes, os novos cartões formulados em *Active Recall* surgirão na tela.

#### 4.2. Adição Manual de Flashcards
* Se preferir criar seus próprios cartões personalizados, clique em **"+ Adicionar manual"**, digite a **Pergunta (frente)** e a **Resposta (verso)** e clique em **"Salvar cartão"**.

#### 4.3. Como Executar a Sessão de Estudo (Modo AnkiWeb)
1. Clique no botão **"Praticar agora"**. Uma janela de revisão focada e livre de distrações será aberta.
2. **Frente do Cartão:** Leia a pergunta e tente recordá-la ativamente de memória.
3. **Revelando a Resposta:**
   * Pressione a **Barra de Espaço** no teclado (ou clique no cartão).
   * O cartão gira suavemente, exibindo a pergunta de contexto no topo, a linha divisória e a resposta correta no centro (estilo AnkiWeb).
4. **Classificando sua Lembrança (Algoritmo SM-2):**
   * Pressione o número correspondente no teclado ou clique no botão:
     * **1. Errei (Again):** Você não lembrou da resposta. O cartão voltará para revisão amanhã (1 dia).
     * **2. Difícil (Hard):** Lembrou com grande esforço. O cartão avança de forma conservadora (2 dias).
     * **3. Bom (Good):** Lembrou com facilidade normal. O cartão avança de acordo com seu Fator de Facilidade (ex.: 3 dias).
     * **4. Fácil (Easy):** Conteúdo totalmente dominado. O cartão recebe bônus de espaçamento (4+ dias).
5. **Estatísticas da Sessão:**
   * Ao finalizar, o sistema exibe o resumo completo de cartões revisados e acertos, recalculando a agenda no banco PostgreSQL.

---

### 5. Grafo de Conhecimento & Conexões (Estilo Obsidian)

Conecte seus estudos em uma rede associativa de aprendizagem:

1. **Acessando a Aba "Conexões de Estudo":**
   * No detalhe de qualquer material, clique na 3ª aba.
2. **Criando um Novo Vínculo:**
   * Clique em **"+ Nova conexão"**.
   * Selecione o outro PDF com o qual deseja conectar este estudo.
   * Escolha o **Tipo de Relação**:
     * **Pré-requisito:** Fundamento ou base conceitual necessária.
     * **Aprofundamento:** Tópico avançado ou desdobramento detalhado.
     * **Correlato:** Conteúdo análogo ou interdisciplinar.
     * **Aplicação:** Estudo de caso prático no mundo real.
   * *(Opcional)* Adicione uma **Nota explicativa** (ex.: *"Dominar handshake TCP antes de estudar protocolos de transporte"*).
   * Clique em **"Salvar conexão"**.
3. **Navegando por Backlinks:**
   * Sempre que o Material A aponta para o Material B, o Material B exibe automaticamente um **Backlink** de retorno. Clicar no cartão direciona você imediatamente para o outro PDF.

---

# PARTE 2: DIAGRAMA DE IMPLANTAÇÃO (FASE DE CONSTRUÇÃO)

Para a entrega na seção *“Aplicando o conhecimento”*, o diagrama modela a arquitetura física e lógica conteinerizada:

```text
┌─────────────────────────┐          HTTPS :80/443          ┌───────────────────────────────────┐
│ «device»                │ ──────────────────────────────► │ «node» Servidor de Aplicação      │
│ Computador do Aluno     │                                 │ ┌───────────────────────────────┐ │
│ ┌─────────────────────┐ │                                 │ │ Nginx (Servidor Web & Proxy)  │ │
│ │ Navegador Web:      │ │                                 │ └──────────────┬────────────────┘ │
│ │ StudyAI Frontend    │ │                                 │                │ HTTP :8000       │
│ │ (React 18 / SPA)    │ │                                 │ ┌──────────────▼────────────────┐ │
│ └─────────────────────┘ │                                 │ │ FastAPI (Python 3.13)         │ │
└─────────────────────────┘                                 │ │ API REST & Regras de Negócio  │ │
                                                            │ └───────┬───────────────┬───────┘ │
                                                            └─────────┼───────────────┼─────────┘
                                                                      │ TCP :5432     │ HTTPS :443
                                                                      ▼               ▼
                                                     ┌──────────────────┐    ┌──────────────────┐
                                                     │ «database system»│    │ «cloud service»  │
                                                     │ PostgreSQL 17    │    │ Google Gemini AI │
                                                     │ (Dados ACID)     │    │ (gemini-2.5)     │
                                                     └──────────────────┘    └──────────────────┘
```

* **Arquivo Visual em Vetor:** `studyai/diagrama_implantacao_simples.svg` (e versão expandida em `studyai/diagrama_implantacao_iteracao1.svg`).
* **Nós Principais:**
  1. `Cliente (Browser)`: Execução da SPA React 18 / TypeScript.
  2. `Servidor Nginx (Porta 80/443)`: Entrega estática de assets e proxy reverso para `/api/*`.
  3. `Servidor FastAPI (Porta 8000)`: Regras de negócio, PyMuPDF, SM-2, Rate Limiting e migrações Alembic.
  4. `PostgreSQL 17 DBMS (Porta 5432)`: Persistência relacional de dados com volume `pg_data`.
  5. `Google Gemini AI (Porta 443)`: Geração inteligente via chamadas seguras de API.

---

# PARTE 3: ROTEIRO DO VÍDEO DE DEMONSTRAÇÃO (8 MINUTOS)

Para gravação do vídeo exigido pela rubrica de avaliação, utilize o roteiro cronometrado minuto a minuto:

* **Link da Demonstração (YouTube / Google Drive):**  
  `https://youtu.be/SEU_LINK_DO_VIDEO_AQUI` *(Substitua pela URL do vídeo gravado pelo grupo)*

---

### Script de Gravação Minuto a Minuto (00:00 a 08:00)

| Minuto | Bloco / Tela | O que falar e demonstrar no vídeo |
|---|---|---|
| **00:00 – 01:00** | **Apresentação e Arquitetura** | Apresentar os integrantes do grupo, o objetivo do StudyAI (aprendizagem ativa com IA e repetição espaçada) e mostrar rapidamente a topologia do **Diagrama de Implantação** (React + FastAPI + PostgreSQL + Docker). |
| **01:00 – 02:00** | **Autenticação e Modo Escuro** | Demonstrar a tela de login/cadastro, efetuar login com `maria@exemplo.com`, alternar entre o **Modo Claro** e o **Modo Escuro Grafite (Obsidian)** pelo botão de topo, destacando a ausência de cansaço visual e zero emojis. |
| **02:00 – 03:15** | **Upload e Extração de PDF** | Clicar em **"+ Enviar PDF"**, selecionar um arquivo técnico (ex.: redes ou biologia), demonstrar a validação imediata de *magic bytes* e o processamento de texto com contador de caracteres e páginas persistidos no PostgreSQL. |
| **03:15 – 04:30** | **Resumo Cognitivo com IA** | Clicar em **"Gerar resumo com IA"**, explicar o funcionamento da fila assíncrona (`ai_jobs`) que não trava o navegador e demonstrar o resumo formatado em 4 seções pedagógicas com modelo Gemini. |
| **04:30 – 06:00** | **Flashcards com Foco Personalizado** | Acessar a aba de flashcards, clicar em **"Gerar com foco"**, digitar um tema específico (ex.: *"Focar no modelo OSI e protocolos TCP"*), mostrar o processamento e a formulação de perguntas assertivas voltadas à recordação ativa. |
| **06:00 – 07:00** | **Sessão Prática de Estudo (SM-2)** | Clicar em **"Praticar agora"**, demonstrar os atalhos de teclado (Espaço para virar o cartão no estilo AnkiWeb, teclas 1 a 4 para avaliar), explicando como o algoritmo SM-2 atualiza o intervalo de repetição no banco. |
| **07:00 – 07:45** | **Grafo de Conhecimento (Obsidian)** | Acessar a aba **"Conexões de Estudo"**, criar uma conexão do tipo *Pré-requisito*, mostrar o vínculo salvo e demonstrar a navegação imediata através do **Backlink** automático no material referenciado. |
| **07:45 – 08:00** | **Conclusão e Encerramento** | Concluir destacando a robustez fullstack (banco real, testes automatizados e deploy em Docker pronto para entrar no ar). Agradecer ao professor e à banca. |
