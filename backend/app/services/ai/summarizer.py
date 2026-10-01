"""Geração de resumos didáticos a partir do texto extraído de um material."""

from app.services.ai.gemini import generate_text
from app.services.ai.text_utils import split_into_chunks

# Acima disso dividimos em partes (map-reduce). Os modelos aceitam ~1M tokens, mas na prática
# o tier gratuito rejeita com 503 ("alta demanda") pedidos caros (entrada grande + saída longa)
# com muito mais frequência do que pedidos pequenos. Partes de ~30k caracteres (≈7k tokens)
# passam com facilidade; o custo é mais chamadas sequenciais para materiais longos.
MAX_CHARS_SINGLE_CALL = 40_000  # ≈ 10k tokens ≈ 12-15 páginas de texto
CHUNK_CHARS = 30_000

SYSTEM_INSTRUCTION = """Você é um tutor especialista em criar materiais de estudo.
Você recebe o texto extraído de um PDF (apostila, artigo ou anotações) e produz resumos
didáticos, fiéis ao conteúdo. Regras:
- Use SOMENTE informações presentes no texto. Não invente fatos, datas ou exemplos.
- Escreva no mesmo idioma do material (se houver dúvida, português do Brasil).
- Formate em Markdown simples (títulos ##, listas com -, **negrito** para termos-chave).
- Não inclua preâmbulos como "Aqui está o resumo". Comece direto no conteúdo.
- Ignore ruídos típicos de PDF: cabeçalhos/rodapés repetidos, números de página, sumário."""

SUMMARY_PROMPT = """Material: "{title}"

Produza um resumo de estudo com exatamente esta estrutura:

## Visão geral
Um parágrafo (3 a 5 frases) explicando do que trata o material e por que importa.

## Conceitos-chave
Lista dos termos/conceitos essenciais, cada um como `- **Termo**: definição curta`.

## Pontos principais
Os pontos mais importantes organizados por tema ou seção do material, em tópicos.
Inclua fórmulas, classificações, etapas de processos e relações de causa e efeito quando existirem.

## Para fixar
De 3 a 5 perguntas curtas de autoavaliação (sem respostas) cobrindo os pontos mais cobrados.

=== TEXTO DO MATERIAL ===
{text}
=== FIM DO TEXTO ==="""

PARTIAL_PROMPT = """Material: "{title}" — parte {index} de {total}.

Faça um resumo detalhado em tópicos (Markdown) desta parte do material: conceitos, definições,
pontos principais, fórmulas e etapas de processos. Seja fiel ao texto; não invente.

=== TEXTO (PARTE {index}/{total}) ===
{text}
=== FIM ==="""

CONSOLIDATE_PROMPT = """Material: "{title}"

Abaixo estão resumos parciais de partes consecutivas do mesmo material.
Consolide-os em UM resumo de estudo final, sem repetições, com exatamente esta estrutura:

## Visão geral
## Conceitos-chave
## Pontos principais
## Para fixar

(Use o mesmo formato: parágrafo na visão geral; `- **Termo**: definição` nos conceitos;
tópicos organizados por tema nos pontos principais; 3 a 5 perguntas de autoavaliação para fixar.)

=== RESUMOS PARCIAIS ===
{partials}
=== FIM ==="""


def summarize_material(title: str, text: str) -> tuple[str, str]:
    """Retorna (resumo_markdown, modelo_usado)."""
    text = text.strip()
    if not text:
        raise ValueError("Material sem texto.")

    if len(text) <= MAX_CHARS_SINGLE_CALL:
        return generate_text(
            SUMMARY_PROMPT.format(title=title, text=text),
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3,
        )

    # Material longo: resume cada parte e depois consolida.
    chunks = split_into_chunks(text, CHUNK_CHARS)
    partials: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        partial, _ = generate_text(
            PARTIAL_PROMPT.format(title=title, index=i, total=len(chunks), text=chunk),
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,
            max_output_tokens=2048,  # resumos parciais curtos: pedidos baratos são aceitos com mais facilidade
        )
        partials.append(f"### Parte {i}\n{partial}")

    return generate_text(
        CONSOLIDATE_PROMPT.format(title=title, partials="\n\n".join(partials)),
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.3,
    )
