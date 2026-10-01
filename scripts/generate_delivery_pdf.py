#!/usr/bin/env python3
"""
Gera o PDF consolidado de entrega da Iteração 1:
- Guia do Usuário (Manual de Operação)
- Diagrama de Implantação (UML 2.5)
- Roteiro e Link do Vídeo de 8 Minutos
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        if self._pageNumber > 1:
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(54, 800, "StudyAI — Pacote de Entrega: Fase de Construção (Iteração 1)")
            self.drawRightString(A4[0] - 54, 800, "Guia do Usuário & Implantação")
            
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.6)
            self.line(54, 792, A4[0] - 54, 792)

            self.line(54, 45, A4[0] - 54, 45)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(54, 32, "Entrega Acadêmica • Seção 'Aplicando o conhecimento' • Momento com o Professor")
            page_text = f"Página {self._pageNumber} de {total_pages}"
            self.drawRightString(A4[0] - 54, 32, page_text)
        self.restoreState()


def create_delivery_pdf(filename: str):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#1d4ed8")
    c_dark = colors.HexColor("#1e293b")
    c_text = colors.HexColor("#0f172a")
    c_muted = colors.HexColor("#475569")
    c_bg_alt = colors.HexColor("#f8fafc")
    c_border = colors.HexColor("#e2e8f0")

    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=24, leading=30,
        textColor=c_dark, spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=12, leading=17,
        textColor=c_muted, spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'SectionH1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14, leading=19,
        textColor=c_primary, spaceBefore=14, spaceAfter=8, keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=15,
        textColor=c_dark, spaceBefore=10, spaceAfter=5, keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=14,
        textColor=c_text, spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletCustom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=13,
        textColor=c_text, leftIndent=12, spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'CalloutText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12.5,
        textColor=c_dark
    )

    table_header = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=10,
        textColor=colors.white
    )

    table_cell = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.5, leading=10,
        textColor=c_text
    )

    story = []

    # =========================================================================
    # CAPA
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "<font color='#1d4ed8'><b>PROJETO STUDYAI</b></font> &nbsp;•&nbsp; ENGENHARIA DE SOFTWARE & TCC",
        ParagraphStyle('CoverTag', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=c_primary)
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Pacote de Entrega Oficial — Iteração 1 (Construção)", title_style))
    story.append(Paragraph(
        "Documento consolidado contendo: (1) Guia do Usuário Completo; (2) Diagrama de Implantação UML; "
        "(3) Roteiro e Link do Vídeo de Demonstração em Funcionamento (8 minutos).",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=15))

    # Box de Identificação Acadêmica
    meta_data = [
        [Paragraph("<b>Atividade Acadêmica:</b>", table_cell), Paragraph("Seção 'Aplicando o conhecimento' • Momento com o Professor", table_cell)],
        [Paragraph("<b>Fase / Iteração:</b>", table_cell), Paragraph("Fase de Construção — Iteração 1 (Processo Unificado / RUP)", table_cell)],
        [Paragraph("<b>Link do Vídeo (8 min):</b>", table_cell), Paragraph("<b>https://youtu.be/SEU_LINK_DO_VIDEO_AQUI</b> <i>(Substituir pela URL do grupo)</i>", table_cell)],
        [Paragraph("<b>Diagrama de Implantação:</b>", table_cell), Paragraph("Anexo na Parte 2 e arquivo <code>diagrama_implantacao_simples.svg</code>", table_cell)],
        [Paragraph("<b>Credenciais de Demonstração:</b>", table_cell), Paragraph("maria@exemplo.com &nbsp;/&nbsp; senha-forte-123", table_cell)],
        [Paragraph("<b>Ambiente do Projeto:</b>", table_cell), Paragraph("FastAPI + React 18 + PostgreSQL 17 + Google Gemini (Dockerizado)", table_cell)],
    ]
    meta_table = Table(meta_data, colWidths=[140, 347])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_alt),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 15))
    story.append(PageBreak())

    # =========================================================================
    # PARTE 1: GUIA DO USUÁRIO
    # =========================================================================
    story.append(Paragraph("Parte 1: Guia do Usuário (Manual de Operação)", h1_style))
    story.append(Paragraph(
        "Este manual descreve a operação passo a passo de todas as funcionalidades desenvolvidas na Iteração 1.",
        body_style
    ))

    story.append(Paragraph("1. Acesso Seguro e Configuração de Visualização", h2_style))
    story.append(Paragraph("• <b>Autenticação:</b> Acesse a tela de Login ou crie sua conta na opção 'Criar conta'. O sistema utiliza senhas com hash bcrypt e tokens JWT protegidos por cookies HTTP-Only.", bullet_style))
    story.append(Paragraph("• <b>Modo Escuro Grafite (Obsidian Theme):</b> No topo da aplicação, clique no ícone de Sol/Lua para alternar para o tema escuro neutro (#1e1e1e). O sistema salva sua escolha automaticamente no navegador sem cansar a visão.", bullet_style))

    story.append(Paragraph("2. Envio e Extração de PDFs", h2_style))
    story.append(Paragraph("• <b>Upload Seguro:</b> Na página 'Meus materiais', clique em '+ Enviar PDF'. Arraste ou selecione arquivos de até 25 MB.", bullet_style))
    story.append(Paragraph("• <b>Validação de Magic Bytes:</b> Arquivos renomeados incorretamente são bloqueados; apenas PDFs reais com assinatura binária <code>%PDF-</code> são aceitos.", bullet_style))
    story.append(Paragraph("• <b>Processamento:</b> O texto é extraído instantaneamente via PyMuPDF e indexado com contagem de caracteres e páginas.", bullet_style))

    story.append(Paragraph("3. Resumos Cognitivos com IA", h2_style))
    story.append(Paragraph("• <b>Geração Assíncrona:</b> No detalhe do material, clique em 'Gerar resumo com IA'. O backend processa a síntese em segundo plano sem travar a interface.", bullet_style))
    story.append(Paragraph("• <b>Estrutura Editorial:</b> O texto é estruturado pedagogicamente em: Visão Geral, Conceitos-Chave, Pontos Principais e Para Fixar.", bullet_style))

    story.append(Paragraph("4. Flashcards com Foco Personalizado & Repetição Espaçada (SM-2)", h2_style))
    story.append(Paragraph("• <b>Geração Direcionada por Tema:</b> Na aba de Flashcards, utilize a função 'Gerar com foco' e digite o assunto específico (ex.: 'Modelo OSI e TCP'). A IA ranqueia os trechos mais relevantes do PDF e formula perguntas estritamente voltadas a esse tópico.", bullet_style))
    story.append(Paragraph("• <b>Revisor de Estudo no Modo AnkiWeb:</b> Clique em 'Praticar agora' para iniciar a sessão focada. Use a tecla <b>Espaço</b> para revelar o verso (mantendo a pergunta no topo com divisor) e avalie sua retenção com as teclas <b>1 (Errei)</b>, <b>2 (Difícil)</b>, <b>3 (Bom)</b> ou <b>4 (Fácil)</b>.", bullet_style))
    story.append(Paragraph("• <b>Cálculo SM-2:</b> O algoritmo atualiza a repetição e o intervalo exato para a próxima revisão no banco de dados.", bullet_style))

    story.append(Paragraph("5. Grafo de Conhecimento e Backlinks (Estilo Obsidian)", h2_style))
    story.append(Paragraph("• <b>Conexões Semânticas:</b> Na aba 'Conexões de Estudo', vincule outros PDFs cadastrados através de relações tipadas (Pré-requisito, Aprofundamento, Conteúdo correlato ou Aplicação prática).", bullet_style))
    story.append(Paragraph("• <b>Backlinks Automáticos:</b> O documento referenciado exibe instantaneamente um link reverso apontando para a origem.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(PageBreak())

    # =========================================================================
    # PARTE 2: DIAGRAMA DE IMPLANTAÇÃO
    # =========================================================================
    story.append(Paragraph("Parte 2: Diagrama de Implantação (UML 2.5)", h1_style))
    story.append(Paragraph(
        "O diagrama documenta a distribuição física e lógica dos nós, contêineres e protocolos de comunicação da Iteração 1:",
        body_style
    ))

    # Tabela simplificada de nós
    diag_nodes = [
        [Paragraph("Nó / Tier", table_header), Paragraph("Componentes / Contêineres", table_header), Paragraph("Protocolo & Porta", table_header), Paragraph("Responsabilidade", table_header)],
        [
            Paragraph("<b>«device» Cliente</b>", table_cell),
            Paragraph("Navegador Web (Chrome/Firefox)<br/>• StudyAI SPA (React 18)", table_cell),
            Paragraph("HTTPS :80 / :443", table_cell),
            Paragraph("Interface gráfica, Modo Escuro, Revisor AnkiWeb e SPA.", table_cell)
        ],
        [
            Paragraph("<b>«node» Servidor Web</b>", table_cell),
            Paragraph("Contêiner <code>studyai_frontend</code><br/>• Nginx 1.25 Alpine", table_cell),
            Paragraph("HTTP :8000 (Proxy /api/*)", table_cell),
            Paragraph("Entrega estática de assets e roteamento reverso de chamadas de API.", table_cell)
        ],
        [
            Paragraph("<b>«node» Servidor Backend</b>", table_cell),
            Paragraph("Contêiner <code>studyai_backend</code><br/>• FastAPI + Uvicorn ASGI", table_cell),
            Paragraph("psycopg3 TCP :5432", table_cell),
            Paragraph("Autenticação JWT, extração PDF, motor SM-2 e fila de IA.", table_cell)
        ],
        [
            Paragraph("<b>«database» Banco</b>", table_cell),
            Paragraph("Contêiner <code>studyai_postgres</code><br/>• PostgreSQL 17 DBMS", table_cell),
            Paragraph("Storage Volume<br/>(<code>pg_data</code>)", table_cell),
            Paragraph("Persistência relacional ACID em 3NF e integridade referencial.", table_cell)
        ],
        [
            Paragraph("<b>«cloud service» Nuvem</b>", table_cell),
            Paragraph("Google Cloud Platform<br/>• Gemini AI (gemini-2.5-flash)", table_cell),
            Paragraph("HTTPS REST :443<br/>(API Key Auth)", table_cell),
            Paragraph("Geração inteligente de resumos e formulação de flashcards.", table_cell)
        ],
    ]
    diag_table = Table(diag_nodes, colWidths=[90, 130, 100, 167])
    diag_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_alt]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(diag_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<i>Nota de entrega:</i> O arquivo vetorial completo de modelagem está renderizado em anexo sob o nome "
        "<code>studyai/diagrama_implantacao_simples.svg</code>.",
        callout_style
    ))

    story.append(Spacer(1, 10))
    story.append(PageBreak())

    # =========================================================================
    # PARTE 3: ROTEIRO DO VÍDEO DE DEMONSTRAÇÃO (8 MINUTOS)
    # =========================================================================
    story.append(Paragraph("Parte 3: Roteiro e Demonstração em Vídeo (8 Minutos)", h1_style))
    story.append(Paragraph(
        "Apresentação cronometrada em vídeo demonstrando a aplicação real em funcionamento, cobrindo todos os critérios da rubrica de avaliação:",
        body_style
    ))

    # Box do Link do Vídeo
    link_box_data = [[
        Paragraph(
            "<b>LINK DA GRAVAÇÃO EM VÍDEO (8 MINUTOS):</b><br/>"
            "<font color='#1d4ed8'><u>https://youtu.be/SEU_LINK_DO_VIDEO_AQUI</u></font><br/>"
            "<font color='#64748b' size='7.5'><i>(Substitua pelo link do YouTube ou Google Drive com permissão pública de visualização)</i></font>",
            table_cell
        )
    ]]
    link_box = Table(link_box_data, colWidths=[487])
    link_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#eff6ff")),
        ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor("#93c5fd")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(link_box)
    story.append(Spacer(1, 10))

    # Cronograma Minuto a Minuto
    video_rows = [
        [Paragraph("Tempo", table_header), Paragraph("Etapa / Funcionalidade", table_header), Paragraph("Ações & Script Narrativo para o Vídeo", table_header)],
        [
            Paragraph("<b>00:00 - 01:00</b>", table_cell),
            Paragraph("<b>Abertura & Arquitetura</b>", table_cell),
            Paragraph("Apresentar os membros do grupo e contextualizar a proposta do StudyAI. Exibir rapidamente o Diagrama de Implantação e destacar a persistência real em PostgreSQL.", table_cell)
        ],
        [
            Paragraph("<b>01:00 - 02:00</b>", table_cell),
            Paragraph("<b>Autenticação & Tema</b>", table_cell),
            Paragraph("Demonstrar o fluxo de login com <code>maria@exemplo.com</code>. Alternar entre Modo Claro e Modo Escuro Grafite (#1e1e1e) para evidenciar a ergonomia visual do Obsidian.", table_cell)
        ],
        [
            Paragraph("<b>02:00 - 03:15</b>", table_cell),
            Paragraph("<b>Upload Seguro & Extração</b>", table_cell),
            Paragraph("Realizar upload de um PDF real via interface. Mostrar a validação de assinatura binária (%PDF-) e a contagem de páginas/caracteres extraídos com PyMuPDF.", table_cell)
        ],
        [
            Paragraph("<b>03:15 - 04:30</b>", table_cell),
            Paragraph("<b>Resumo com IA (Gemini)</b>", table_cell),
            Paragraph("Disparar a geração assíncrona do resumo. Explicar a fila de jobs (ai_jobs) e apresentar a estrutura em 4 seções pedagógicas gerada pelo Gemini.", table_cell)
        ],
        [
            Paragraph("<b>04:30 - 06:00</b>", table_cell),
            Paragraph("<b>Flashcards com Foco</b>", table_cell),
            Paragraph("Utilizar a opção 'Gerar com foco', digitar um tema específico do documento e demonstrar a formulação de perguntas assertivas baseadas em Active Recall.", table_cell)
        ],
        [
            Paragraph("<b>06:00 - 07:00</b>", table_cell),
            Paragraph("<b>Sessão de Estudo SM-2</b>", table_cell),
            Paragraph("Iniciar o modo de revisão. Usar a Barra de Espaço para girar a carta (estilo AnkiWeb) e os atalhos 1 a 4 para avaliar, explicando a fórmula do algoritmo SM-2.", table_cell)
        ],
        [
            Paragraph("<b>07:00 - 07:45</b>", table_cell),
            Paragraph("<b>Grafo de Conhecimento</b>", table_cell),
            Paragraph("Vincular dois materiais na aba 'Conexões de Estudo' (relação Pré-requisito). Demonstrar o Backlink automático gerado no material de destino.", table_cell)
        ],
        [
            Paragraph("<b>07:45 - 08:00</b>", table_cell),
            Paragraph("<b>Encerramento & Conclusão</b>", table_cell),
            Paragraph("Destacar os 7 testes automatizados aprovados, a conteinerização com Docker e agradecer ao professor e aos avaliadores.", table_cell)
        ],
    ]
    video_table = Table(video_rows, colWidths=[65, 120, 302])
    video_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_alt]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(video_table)

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph(
        "<b>Conclusão da Entrega:</b> Todos os requisitos da seção 'Aplicando o conhecimento' foram cumpridos integralmente, "
        "com código testado, implantável em contêineres e documentado para a avaliação acadêmica.",
        callout_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF consolidado de entrega gerado: {filename}")

if __name__ == '__main__':
    create_delivery_pdf('/home/user/studyai/StudyAI_Guia_do_Usuario_e_Entrega.pdf')
