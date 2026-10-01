# StudyAI — Sistema de Design & UI/UX Guidelines
## Baseado nas Especificações de `bergside/awesome-design-skills`

Este repositório incorporou as diretrizes de design, tokens visuais e padrões de interface do projeto **`bergside/awesome-design-skills`** para aprimorar a identidade visual, a usabilidade e a ergonomia de estudo do **StudyAI**.

---

### 1. Habilidades de Design Importadas e Sintetizadas

| Skill Importada | Conceito Chave | Aplicação no StudyAI |
|---|---|---|
| **`minimal`** | Foco absoluto no conteúdo, ausência de ruído visual e máxima clareza. | Layout sóbrio, foco no texto dos PDFs e resumos, sem excesso de botões ou enfeites. |
| **`clean`** | Espaçamento generoso, paleta restrita e hierarquia visual evidente. | Alinhamento em grade modular (4/8/12/16/24/32px), contraste WCAG AA e divisores finos. |
| **`shadcn`** | Micro-interações táteis, anéis de foco acessíveis e tokens consistentes. | Bordas com raio proporcional (6px a 12px), anéis `outline-offset: 2px` e micro-estados ativos (`scale(0.985)`). |
| **`editorial`** | Tipografia pensada para leitura prolongada, títulos marcantes e ritmo visual. | Resumos com entrelinha otimizada (1.65), blocos de citação com barra lateral e seções estruturadas. |
| **`sleek` & `refined`** | Sombras multicamadas sutis, desfoques de vidro (*backdrop-filter*) e superfícies polidas. | Barra de navegação com desfoque de 12px, modais com profundidade suave e cartões com leve elevação no hover. |
| **`mono`** | Estética técnica para metadados, atalhos de teclado e tags de sistema. | Pílulas de atalho (`[Espaço]`, `[1]`, `[2]`, `[3]`, `[4]`), contadores numéricos tabulares e badges de status. |

---

### 2. Princípios de Identidade Visual Adotados

1. **Anti-Fadiga Visual (Estética Obsidian & AnkiWeb):**
   - **Modo Claro:** Fundo neutro ardósia suave (`#f8fafc`), cartões em branco puro (`#ffffff`) e bordas neutras (`#e2e8f0`).
   - **Modo Escuro:** Carvão e grafite neutros (`#18181b` e `#222226`). **Sem roxo neon ou preto puro reflexivo.** Ideal para horas consecutivas de leitura e revisão.
2. **Zero Emojis na Interface (Ícones SVG Vetoriais):**
   - Todos os estados visuais (PDF, Flashcards, Conexões, Sucesso, Erro, Tema) utilizam exclusivamente **ícones SVG customizados**, garantindo sobriedade profissional e acadêmica.
3. **Ergonomia do Revisor AnkiWeb:**
   - Cartões com visual clássico e foco na recordação ativa.
   - Linha divisória limpa entre pergunta e resposta.
   - Pílulas indicativas de atalhos no teclado diretamente nos botões de nota SM-2.
4. **Profundidade e Camadas:**
   - Sombras suaves em 4 níveis (`--shadow-xs` a `--shadow-lg`).
   - Efeito *lift* de -2px em cartões de materiais no hover para indicar interatividade tangível.
