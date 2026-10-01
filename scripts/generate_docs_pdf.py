#!/usr/bin/env python3
"""
Gera o documento técnico completo do StudyAI em PDF com alta qualidade editorial.
Utiliza ReportLab com layout profissional, paginação dinâmica de dois passos,
tabelas estilizadas, paleta Obsidian/AnkiWeb e tipografia limpa.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas de dois passos para cálculo exato de páginas (Página X de Y)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        print(f"Total de páginas geradas no documento: {num_pages}")
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        # Não exibe cabeçalho/rodapé na capa (página 1)
        if self._pageNumber > 1:
            # Topbar / Cabeçalho
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(54, 800, "StudyAI — Documentação Técnica e Arquitetural do Sistema")
            self.drawRightString(A4[0] - 54, 800, "v1.2 (Obsidian & AnkiWeb)")
            
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.6)
            self.line(54, 792, A4[0] - 54, 792)

            # Rodapé
            self.line(54, 45, A4[0] - 54, 45)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(54, 32, "StudyAI Platform • Arquitetura Fullstack • Python FastAPI & React")
            page_text = f"Página {self._pageNumber} de {total_pages}"
            self.drawRightString(A4[0] - 54, 32, page_text)
            
        self.restoreState()


def create_documentation_pdf(filename: str):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Cores do Design System (Obsidian & AnkiWeb)
    c_primary = colors.HexColor("#1d4ed8")      # Anki Blue
    c_dark = colors.HexColor("#1e293b")         # Slate 800
    c_text = colors.HexColor("#0f172a")         # Text dark
    c_muted = colors.HexColor("#475569")        # Muted slate
    c_bg_alt = colors.HexColor("#f8fafc")       # Surface light
    c_border = colors.HexColor("#e2e8f0")       # Border subtle
    c_accent_green = colors.HexColor("#059669")
    c_code_bg = colors.HexColor("#f1f5f9")

    # Estilos Tipográficos
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=c_dark,
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=c_muted,
        spaceAfter=25
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=21,
        textColor=c_primary,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_dark,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.5,
        textColor=c_text,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_text,
        leftIndent=14,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_dark
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_text
    )

    story = []

    # =========================================================================
    # CAPA
    # =========================================================================
    story.append(Spacer(1, 40))
    # Tag de Versão
    tag_p = Paragraph(
        "<font color='#1d4ed8'><b>PROJETO STUDYAI</b></font> &nbsp;•&nbsp; ESPECIFICAÇÃO DE ENGENHARIA",
        ParagraphStyle('CoverTag', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=c_primary)
    )
    story.append(tag_p)
    story.append(Spacer(1, 10))
    story.append(Paragraph("StudyAI — Documentação Técnica e Arquitetural do Sistema", title_style))
    story.append(Paragraph(
        "Ambiente Fullstack de Aprendizagem Ativa: Extração de PDFs, Sínteses Cognitivas com IA, "
        "Repetição Espaçada (Algoritmo SM-2), Grafo de Conhecimento Bidirecional e Interface Estilo Obsidian & AnkiWeb.",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=20))

    # Box de Metadados da Capa
    meta_data = [
        [Paragraph("<b>Status da Plataforma:</b>", table_cell_style), Paragraph("Produção / Homologação (Fases 1 a 4.5 100% Concluídas)", table_cell_style)],
        [Paragraph("<b>Linguagens & Stack:</b>", table_cell_style), Paragraph("Python 3.13 (FastAPI, SQLAlchemy 2, Alembic) • React 18 (Vite, TypeScript)", table_cell_style)],
        [Paragraph("<b>Banco de Dados:</b>", table_cell_style), Paragraph("PostgreSQL 17 Relacional com Migrações Versionadas", table_cell_style)],
        [Paragraph("<b>Inteligência Artificial:</b>", table_cell_style), Paragraph("Google Gemini (gemini-3.1-flash-lite com fallback e retry)", table_cell_style)],
        [Paragraph("<b>Padrão Visual:</b>", table_cell_style), Paragraph("Obsidian Charcoal Theme (#1e1e1e) & AnkiWeb Study Flow (Sem emojis, ícones SVG)", table_cell_style)],
        [Paragraph("<b>Data do Documento:</b>", table_cell_style), Paragraph("Setembro de 2026", table_cell_style)],
    ]
    meta_table = Table(meta_data, colWidths=[140, 347])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_alt),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "<b>Sumário Executivo:</b> Este documento consolida formalmente todos os módulos, esquemas relacionais de banco de dados, "
        "lógicas algorítmicas, contratos de APIs REST, decisões de design de interface e instruções operacionais da plataforma StudyAI.",
        callout_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # SEÇÃO 1: INTRODUÇÃO E VISÃO GERAL
    # =========================================================================
    story.append(Paragraph("1. Introdução e Visão Geral do Sistema", h1_style))
    story.append(Paragraph(
        "O <b>StudyAI</b> é uma plataforma web fullstack orientada ao aumento substancial da retenção de conhecimento acadêmico "
        "e profissional. Em vez de simplesmente armazenar arquivos em nuvem, o StudyAI transforma materiais passivos (PDFs técnicos, "
        "apostilas, artigos científicos e manuais) em ecossistemas de aprendizagem ativa interconectados.",
        body_style
    ))
    story.append(Paragraph("<b>Problemas Resolvidos pela Arquitetura:</b>", body_style))
    story.append(Paragraph("• <b>Fadiga de Conteúdo Extenso:</b> Materiais com centenas de páginas tornam-se gerenciáveis através de extração cirúrgica de texto e segmentação de alta relevância.", bullet_style))
    story.append(Paragraph("• <b>Ilusão de Competência:</b> O estudante não apenas lê passivamente; é forçado a testar sua recordação ativa (<i>Active Recall</i>) via flashcards gerados por IA.", bullet_style))
    story.append(Paragraph("• <b>Esquecimento Prematuro (Curva de Ebbinghaus):</b> O motor de repetição espaçada SM-2 calcula com precisão matemática a data ideal para cada revisão.", bullet_style))
    story.append(Paragraph("• <b>Fragmentação Conceitual:</b> Conexões bidirecionais (estilo Obsidian) estruturam pré-requisitos, aprofundamentos e referências cruzadas entre diferentes materiais da conta.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SEÇÃO 2: ARQUITETURA GERAL DO SISTEMA
    # =========================================================================
    story.append(Paragraph("2. Arquitetura de Software e Tecnologias", h1_style))
    story.append(Paragraph(
        "O sistema foi construído sob uma premissa inegociável de <b>persistência real em banco relacional</b>, separação limpa de camadas "
        "e desacoplamento total entre o provedor de IA e as entidades de negócio:",
        body_style
    ))

    arch_rows = [
        [Paragraph("Camada", table_header_style), Paragraph("Tecnologia Escolhida", table_header_style), Paragraph("Papel & Responsabilidades", table_header_style)],
        [
            Paragraph("<b>Frontend</b>", table_cell_style),
            Paragraph("React 18, TypeScript, Vite, React Router 6", table_cell_style),
            Paragraph("Interface SPA ultra-rápida, modo escuro persistido (Obsidian charcoal), renderizador Markdown, componente 3D de flashcards estilo AnkiWeb.", table_cell_style)
        ],
        [
            Paragraph("<b>Backend API</b>", table_cell_style),
            Paragraph("Python 3.13, FastAPI, Pydantic v2", table_cell_style),
            Paragraph("Roteamento assíncrono de alta performance, validação rigorosa de esquemas, injeção de dependências para sessão e autenticação de usuários.", table_cell_style)
        ],
        [
            Paragraph("<b>Persistência</b>", table_cell_style),
            Paragraph("PostgreSQL 17, SQLAlchemy 2, Alembic", table_cell_style),
            Paragraph("Controle de concorrência ACID, integridade referencial com ON DELETE CASCADE, migrações versionadas com rollback e dump de schema estruturado.", table_cell_style)
        ],
        [
            Paragraph("<b>Processamento PDF</b>", table_cell_style),
            Paragraph("PyMuPDF (fitz)", table_cell_style),
            Paragraph("Extração precisa de blocos textuais, detecção de páginas vazias, sanitização de caracteres e metadados de arquivo.", table_cell_style)
        ],
        [
            Paragraph("<b>Camada de IA</b>", table_cell_style),
            Paragraph("Google Gemini API (3.1-flash-lite)", table_cell_style),
            Paragraph("Geração de sínteses pedagógicas e flashcards estruturados JSON com mecanismo de retry com backoff exponencial e fallbacks graduais.", table_cell_style)
        ],
    ]
    arch_table = Table(arch_rows, colWidths=[80, 140, 267])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_alt]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(arch_table)

    story.append(Spacer(1, 14))

    # =========================================================================
    # SEÇÃO 3: MODELO DE DADOS E ESQUEMA RELACIONAL
    # =========================================================================
    story.append(Paragraph("3. Esquema do Banco de Dados Relacional (PostgreSQL)", h1_style))
    story.append(Paragraph(
        "Todas as tabelas foram modeladas respeitando a 3ª Forma Normal (3NF), com índices de cobertura para consultas frequentes "
        "e restrições de integridade que garantem a segurança de cada usuário:",
        body_style
    ))

    tables_info = [
        ("users", "id, name, email (UNIQUE), password_hash (bcrypt), created_at", "Armazena as contas cadastradas com isolamento estrito de dados."),
        ("materials", "id, user_id (FK), title, filename, stored_path, file_size, page_count, content_text, char_count, uploaded_at", "Registra cada documento enviado, seu caminho em disco e o texto completo extraído."),
        ("summaries", "id, material_id (FK UNIQUE), text, model, generated_at", "Guarda a síntese gerada pela IA vinculada exclusivamente a um material."),
        ("flashcards", "id, material_id (FK), question, answer, repetitions, interval_days, ease_factor, next_review_at, last_reviewed_at", "Contém os cartões de memorização e o estado do algoritmo de repetição espaçada SM-2."),
        ("material_connections", "id, source_material_id (FK), target_material_id (FK), relation_type, note, created_at", "Tabela do Grafo Obsidian. Restrições: UNIQUE(source, target) e CHECK(source != target)."),
        ("ai_jobs", "id, material_id (FK), kind, status, error, model, attempts, focus, created_at, finished_at", "Fila de jobs assíncronos que desacopla o tempo de resposta da API das chamadas ao Gemini."),
        ("study_plans & items", "id, user_id, title, description, due_date, done, position, material_id", "Permite organizar cronogramas e trilhas de leitura por datas."),
    ]

    schema_rows = [[Paragraph("Tabela", table_header_style), Paragraph("Campos Chave & Chaves Estrangeiras", table_header_style), Paragraph("Descrição Operacional", table_header_style)]]
    for t_name, t_fields, t_desc in tables_info:
        schema_rows.append([
            Paragraph(f"<b>{t_name}</b>", table_cell_style),
            Paragraph(t_fields, table_cell_style),
            Paragraph(t_desc, table_cell_style)
        ])

    schema_table = Table(schema_rows, colWidths=[90, 200, 197])
    schema_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_alt]),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(schema_table)

    story.append(PageBreak())

    # =========================================================================
    # SEÇÃO 4: ALGORITMOS CENTRAIS (SM-2, CHUNKING E FOCO)
    # =========================================================================
    story.append(Paragraph("4. Algoritmos e Regras de Negócio Centrais", h1_style))
    
    story.append(Paragraph("4.1. Algoritmo de Repetição Espaçada SM-2 (SuperMemo-2)", h2_style))
    story.append(Paragraph(
        "O StudyAI implementa o clássico algoritmo SM-2 para calibrar os intervalos de revisão de acordo com o desempenho individual. "
        "Cada avaliação de cartão submete uma nota (<i>rating</i>) de 0 a 3:",
        body_style
    ))
    story.append(Paragraph("• <b>Rating 0 (Errei / Again):</b> Repetições zeradas, intervalo resetado para 1 dia, EF reduzido em 0,2.", bullet_style))
    story.append(Paragraph("• <b>Rating 1 (Difícil / Hard):</b> Intervalo ajustado para 2 dias, EF reduzido em 0,15.", bullet_style))
    story.append(Paragraph("• <b>Rating 2 (Bom / Good):</b> Intervalo normal multiplicado pelo Ease Factor atual (ex.: 1d → 3d → 8d...).", bullet_style))
    story.append(Paragraph("• <b>Rating 3 (Fácil / Easy):</b> Intervalo com bônus de facilidade multiplicado por EF × 1.3, EF aumentado em 0,15.", bullet_style))
    story.append(Paragraph("<b>Fórmula de Ajuste do Fator de Facilidade:</b> EF' = max(1.3, EF + (0.1 - (3 - rating) × (0.08 + (3 - rating) × 0.02)))", body_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("4.2. Geração Focada de Flashcards com Ranqueamento por Palavras-Chave", h2_style))
    story.append(Paragraph(
        "Para materiais volumosos (ex.: manuais de 300 páginas), o usuário pode definir um <i>foco temático</i> "
        "(ex.: 'camadas do modelo OSI e protocolo TCP'). O motor do StudyAI executa:",
        body_style
    ))
    story.append(Paragraph("1. Segmentação do texto em blocos semânticos de 25.000 caracteres.", bullet_style))
    story.append(Paragraph("2. Cálculo de pontuação de relevância de cada bloco: <code>score_chunk_focus(chunk, focus)</code> computa a densidade de ocorrência das palavras-chave do foco.", bullet_style))
    story.append(Paragraph("3. Ordenação decrescente e seleção dos blocos de maior pontuação para envio ao prompt do Gemini.", bullet_style))
    story.append(Paragraph("4. Instrução explícita no prompt forçando a IA a extrair apenas conceitos pertinentes ao tema delimitado.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("4.3. Resiliência da Camada de IA (Decoupled AI Engine)", h2_style))
    story.append(Paragraph(
        "A integração com o Gemini é completamente isolada em <code>app/services/ai/gemini.py</code>. "
        "Possui sistema de fallback em cadeia com modelos oficiais (<code>gemini-2.5-flash</code> → <code>gemini-2.0-flash</code> → <code>gemini-1.5-flash</code>), "
        "com até 2 tentativas por modelo e espaçamento exponencial com jitter para evitar falhas transitórias de cota (HTTP 429/503).",
        body_style
    ))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SEÇÃO 5: CONEXÕES DE ESTUDO & GRAFO BIDIRECIONAL
    # =========================================================================
    story.append(Paragraph("5. Conexões de Estudo & Grafo de Conhecimento (Estilo Obsidian)", h1_style))
    story.append(Paragraph(
        "Inspirado no modelo de grafos e notas interligadas do Obsidian, o StudyAI permite estabelecer ligações semânticas entre PDFs. "
        "Diferente de pastas estáticas, o grafo permite navegação orgânica do conhecimento:",
        body_style
    ))
    
    conns_types = [
        [Paragraph("Tipo de Relação", table_header_style), Paragraph("Semântica Conceitual", table_header_style), Paragraph("Exemplo de Aplicação Prática", table_header_style)],
        [
            Paragraph("<b>prerequisite</b>", table_cell_style),
            Paragraph("Base teórica ou fundamento necessário antes do documento atual.", table_cell_style),
            Paragraph("'Redes de Computadores' conectado como pré-requisito de 'Segurança de Firewalls'.", table_cell_style)
        ],
        [
            Paragraph("<b>deepening</b>", table_cell_style),
            Paragraph("Aprofundamento de tópico específico ou teoria avançada.", table_cell_style),
            Paragraph("'Algoritmos Quânticos' conectado como aprofundamento de 'Álgebra Linear'.", table_cell_style)
        ],
        [
            Paragraph("<b>related</b>", table_cell_style),
            Paragraph("Conteúdo correlato, análogo ou com intersecção temática.", table_cell_style),
            Paragraph("'Bioquímica' conectado como correlato a 'Fisiologia Celular'.", table_cell_style)
        ],
        [
            Paragraph("<b>application</b>", table_cell_style),
            Paragraph("Estudo de caso, exercício resolvido ou aplicação real.", table_cell_style),
            Paragraph("'Análise de Casos Forenses' como aplicação de 'Criptoanálise'.", table_cell_style)
        ],
    ]
    conns_table = Table(conns_types, colWidths=[90, 190, 207])
    conns_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_alt]),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(conns_table)

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<b>Mecanismo de Backlinks Automáticos:</b> Ao criar uma conexão A → B, a página do material B passa a exibir imediatamente "
        "um <i>Backlink</i> apontando de volta para A. Isso permite descobrir materiais relacionados sem necessidade de criar links duplos manuais.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # SEÇÃO 6: ESPECIFICAÇÃO COMPLETA DA API REST
    # =========================================================================
    story.append(Paragraph("6. Especificação Completa da API REST", h1_style))
    story.append(Paragraph(
        "Todas as rotas exigem autenticação via token Bearer (ou cookie httpOnly <code>studyai_session</code>), "
        "exceto os endpoints públicos de login, cadastro e healthcheck:",
        body_style
    ))

    api_endpoints = [
        ("POST", "/api/auth/register", "name, email, password", "201 Created", "Cadastra novo usuário e emite JWT."),
        ("POST", "/api/auth/login", "email, password", "200 OK (Rate limit: 10/min)", "Autentica e define cookie seguro com mitigação brute-force."),
        ("POST", "/api/auth/logout", "—", "204 No Content", "Invalida o cookie de sessão HTTP-Only."),
        ("GET", "/api/auth/me", "—", "200 OK", "Retorna perfil do usuário logado."),
        ("GET", "/api/materials", "—", "200 OK", "Lista materiais com contadores de resumo e flashcards."),
        ("POST", "/api/materials", "Multipart: file (.pdf), title", "201 Created", "Upload com validação de magic bytes %PDF- e extração."),
        ("GET", "/api/materials/{id}", "—", "200 OK / 404", "Detalhes, prévia de texto e jobs ativos de IA."),
        ("GET", "/api/materials/{id}/content", "—", "200 OK", "Retorna texto extraído integralmente."),
        ("PATCH", "/api/materials/{id}", "title", "200 OK", "Renomeia o título do material."),
        ("DELETE", "/api/materials/{id}", "—", "204 No Content", "Exclui material e arquivos físicos em cascata."),
        ("POST", "/api/materials/{id}/summary", "—", "202 Accepted (Rate limit: 6/min)", "Enfileira geração assíncrona do resumo com IA."),
        ("GET", "/api/materials/{id}/summary", "—", "200 OK / 404", "Retorna resumo gerado em Markdown."),
        ("POST", "/api/materials/{id}/flashcards/generate", "{ focus?: string }", "202 Accepted (Rate limit: 6/min)", "Enfileira geração de flashcards direcionados."),
        ("GET", "/api/materials/{id}/flashcards", "—", "200 OK", "Lista flashcards (total e pendentes de revisão hoje)."),
        ("POST", "/api/materials/{id}/flashcards", "question, answer", "201 Created", "Criação manual de flashcard."),
        ("PATCH", "/api/flashcards/{id}", "{ question?, answer? }", "200 OK", "Edita o conteúdo textual de um flashcard."),
        ("GET", "/api/materials/{id}/flashcards/study", "?mode=due|all", "200 OK", "Fila ordenada de estudo para o revisor AnkiWeb."),
        ("POST", "/api/flashcards/{id}/review", "rating (0..3)", "200 OK", "Recalcula intervalo SM-2 e salva revisão."),
        ("GET", "/api/materials/{id}/connections", "—", "200 OK", "Retorna saídas, backlinks e materiais conectáveis."),
        ("POST", "/api/materials/{id}/connections", "target_material_id, relation_type, note", "201 Created", "Cria vínculo no Grafo de Conhecimento."),
        ("DELETE", "/api/connections/{id}", "—", "204 No Content", "Remove conexão do grafo."),
        ("GET", "/api/health", "—", "200 OK", "Healthcheck da API e do banco Postgres."),
    ]

    api_rows = [[Paragraph("Método", table_header_style), Paragraph("Rota", table_header_style), Paragraph("Payload / Parâmetros", table_header_style), Paragraph("Status", table_header_style), Paragraph("Função Operacional", table_header_style)]]
    for m, r, p, s, d in api_endpoints:
        api_rows.append([
            Paragraph(f"<b>{m}</b>", table_cell_style),
            Paragraph(f"<code>{r}</code>", table_cell_style),
            Paragraph(p, table_cell_style),
            Paragraph(s, table_cell_style),
            Paragraph(d, table_cell_style),
        ])

    api_table = Table(api_rows, colWidths=[42, 135, 115, 65, 130])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_alt]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(api_table)

    story.append(PageBreak())

    # =========================================================================
    # SEÇÃO 7: DESIGN SYSTEM & INTERFACE OBSIDIAN + ANKIWEB
    # =========================================================================
    story.append(Paragraph("7. Design System & Interface (Obsidian & AnkiWeb)", h1_style))
    story.append(Paragraph(
        "A interface do StudyAI foi inteiramente remodelada para oferecer a mesma ergonomia visual e ausência de distrações "
        "das consagradas ferramentas acadêmicas <b>Obsidian</b> e <b>AnkiWeb</b>:",
        body_style
    ))

    story.append(Paragraph("7.1. Paleta de Cores e Filosofia Visual", h2_style))
    story.append(Paragraph("• <b>Eliminação de Emojis:</b> Substituição total por ícones vetoriais SVG minimalistas desenhados sob medida (<code>IconLogo</code>, <code>IconFlashcards</code>, <code>IconConnections</code>, <code>IconTrash</code>, <code>IconTarget</code>, etc.).", bullet_style))
    story.append(Paragraph("• <b>Modo Escuro Grafite Obsidian (Default Dark):</b> Fundo carvão neutro <code>#1e1e1e</code>, cartões em <code>#262626</code> e bordas em <code>#363636</code>. O preto absoluto e tons roxos saturados foram eliminados em favor de tons suaves com alto contraste para texto <code>#dcddde</code>.", bullet_style))
    story.append(Paragraph("• <b>Acentos de Destaque Sóbrios:</b> Uso do clássico azul AnkiWeb (<code>#2563eb</code> no claro, <code>#3b82f6</code> no escuro) para elementos interativos, links e barras de progresso.", bullet_style))
    story.append(Paragraph("• <b>Topbar Minimalista de 50px:</b> Estrutura plana, sem efeitos pesados de vidro ou gradientes, garantindo máximo foco no conteúdo de estudo.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("7.2. O Revisor de Flashcards no Fluxo do AnkiWeb", h2_style))
    story.append(Paragraph(
        "A experiência de revisão reproduz a ergonomia comprovada do Anki:",
        body_style
    ))
    story.append(Paragraph("1. <b>Frente do Cartão:</b> Pergunta em destaque central com indicação de tecla de atalho (Barra de Espaço ou clique para revelar).", bullet_style))
    story.append(Paragraph("2. <b>Ao Revelar a Resposta:</b> A pergunta original é preservada no topo em tom atenuado, separada por um divisor sutil <code>&lt;hr class='anki-divider'&gt;</code>, e a resposta é exibida com destaque imediato no centro.", bullet_style))
    story.append(Paragraph("3. <b>Teclas de Atalho:</b> Avaliação instantânea através dos números 1 (Errei), 2 (Difícil), 3 (Bom) e 4 (Fácil), permitindo ciclos de estudo contínuos sem tocar no mouse.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SEÇÃO 8: GUIA DE IMPLANTAÇÃO E AMBIENTE
    # =========================================================================
    story.append(Paragraph("8. Guia de Configuração, Implantação e Manutenção", h1_style))
    story.append(Paragraph(
        "O sistema está pronto para implantação em servidores Linux (Ubuntu/Debian) com dependências padronizadas "
        "ou orquestração completa via Docker Compose:",
        body_style
    ))

    story.append(Paragraph("<b>1. Variáveis de Ambiente Recomendadas para Produção (.env):</b>", h2_style))
    env_content = (
        "DATABASE_URL=postgresql+psycopg://studyai:SenhaSuperForte!123@postgres:5432/studyai\n"
        "SECRET_KEY=chave-super-secreta-gerada-com-openssl-rand-hex-32\n"
        "COOKIE_SECURE=true # Obrigatório em HTTPS\n"
        "CORS_ORIGINS=https://app.seudominio.com.br\n"
        "GEMINI_API_KEY=AIzaSy...SuaChaveOficial...\n"
        "GEMINI_MODEL=gemini-2.5-flash\n"
        "GEMINI_FALLBACK_MODELS=gemini-2.0-flash,gemini-1.5-flash,gemini-1.5-pro\n"
        "UPLOAD_DIR=uploads\n"
        "MAX_UPLOAD_MB=25"
    )
    env_table = Table([[Paragraph(f"<pre>{env_content}</pre>", code_style)]], colWidths=[487])
    env_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(env_table)

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>2. Orquestração e Deploy com Docker Compose:</b>", h2_style))
    story.append(Paragraph("• <b>Subir Aplicação Completa:</b> <code>docker compose up -d --build</code> (inicia Postgres, roda migrações e sobe Nginx/Frontend + API).", bullet_style))
    story.append(Paragraph("• <b>Migrações Alembic Manuais:</b> <code>cd backend && .venv/bin/alembic upgrade head</code>", bullet_style))
    story.append(Paragraph("• <b>Suíte de Testes Automatizados:</b> <code>PYTHONPATH=. pytest tests -v</code> (7 testes cobrindo isolamento, SM-2, conexões e rate limit).", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SEÇÃO 9: LIMITAÇÕES ATUAIS E ROADMAP (TCC & EMPREENDEDORISMO)
    # =========================================================================
    story.append(Paragraph("9. Limitações Atuais e Roadmap de Evolução", h1_style))
    story.append(Paragraph(
        "Para a defesa acadêmica (TCC) e planejamento do produto como startup/SaaS, as limitações conhecidas foram mapeadas "
        "e estruturadas em ordem decrescente de impacto de negócio:",
        body_style
    ))

    roadmap_items = [
        [Paragraph("Prioridade / Recurso", table_header_style), Paragraph("Limitação Atual & Solução Planejada", table_header_style), Paragraph("Impacto no Negócio / Aprendizagem", table_header_style)],
        [
            Paragraph("<b>1. Tutor de IA Contextualizado (Chat)</b>", table_cell_style),
            Paragraph("Atualmente a interação é orientada a tarefas fixas (resumo e flashcards). O próximo passo é chat socrático em tempo real sobre o texto do PDF.", table_cell_style),
            Paragraph("<b>Máximo:</b> Permite ao aluno tirar dúvidas imediatas, pedir analogias e aprofundar pontos difíceis do material.", table_cell_style)
        ],
        [
            Paragraph("<b>2. OCR para PDFs Digitalizados</b>", table_cell_style),
            Paragraph("O extrator atual (PyMuPDF) depende de texto vetorial embutido. PDFs escaneados ou imagens puras retornam texto vazio.", table_cell_style),
            Paragraph("<b>Alto:</b> Habilita suporte a apostilas antigas, xerox e livros digitalizados através de OCR (Tesseract / Gemini Vision).", table_cell_style)
        ],
        [
            Paragraph("<b>3. Busca Semântica (RAG com pgvector)</b>", table_cell_style),
            Paragraph("O ranqueamento por foco atual baseia-se em frequência de termos literais (TF). Pode ignorar sinônimos relevantes.", table_cell_style),
            Paragraph("<b>Alto:</b> Embeddings densos armazenados no PostgreSQL com pgvector para recuperação semântica profunda de trechos.", table_cell_style)
        ],
        [
            Paragraph("<b>4. Novas Fontes além de PDF</b>", table_cell_style),
            Paragraph("Apenas arquivos PDF são aceitos no momento.", table_cell_style),
            Paragraph("<b>Médio-Alto:</b> Suporte a artigos da web (URL scraping), arquivos Markdown, EPUB e transcrição de videoaulas (YouTube).", table_cell_style)
        ],
        [
            Paragraph("<b>5. Interface de Cronograma (Study Plans)</b>", table_cell_style),
            Paragraph("As tabelas <code>study_plans</code> já existem no banco (Alembic 0001), mas as rotas e telas de calendário ainda não foram expostas.", table_cell_style),
            Paragraph("<b>Médio:</b> Conectar a entidade de planos a uma interface de trilha de estudos gamificada.", table_cell_style)
        ],
    ]
    roadmap_table = Table(roadmap_items, colWidths=[110, 220, 157])
    roadmap_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_alt]),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(roadmap_table)

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=8, spaceAfter=14))
    story.append(Paragraph(
        "<b>Conclusão:</b> O StudyAI representa uma arquitetura fullstack robusta, auditada e em total conformidade para entrega "
        "de TCC e lançamento comercial, unindo rigor acadêmico a padrões modernos de engenharia de software.",
        callout_style
    ))

    # Construir PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF gerado com sucesso: {filename}")

if __name__ == '__main__':
    output_pdf = "/home/user/studyai/StudyAI_Documentacao_Tecnica.pdf"
    create_documentation_pdf(output_pdf)
