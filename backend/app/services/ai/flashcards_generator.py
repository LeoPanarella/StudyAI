"""Geração de flashcards com IA a partir do texto do material.

Produz cartões focados em recordação ativa (active recall) e no princípio
da informação mínima (cada cartão testa um único conceito ou relação).
Suporta direcionamento temático personalizado definido pelo estudante.
"""

import json
import logging
import re

from app.services.ai.gemini import AIError, generate_text
from app.services.ai.text_utils import split_into_chunks

log = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = (
    "Você é um especialista em aprendizagem ativa, memorização e técnicas de repetição "
    "espaçada (spaced repetition / Anki). Sua tarefa é extrair os conceitos mais importantes "
    "do material fornecido e transformá-los em flashcards de alta eficiência cognitiva.\n\n"
    "Diretrizes obrigatórias:\n"
    "1. Princípio da Informação Mínima: cada flashcard deve testar exatamente UM conceito, termo, "
    "relação de causa-efeito, processo ou diferença crucial. Nunca coloque listas longas na resposta.\n"
    "2. Pergunta (frente): direta, clara e instigante. Estimule a recordação ativa (ex.: 'O que é...', "
    "'Qual a função de...', 'Como ocorre...', 'Por que...'). Evite perguntas vagas ou de 'Sim/Não'.\n"
    "3. Resposta (verso): concisa, precisa e sem enrolação (1 a 3 frases curtas).\n"
    "4. Idioma: Português do Brasil (pt-BR).\n"
    "5. Formato: Retorne estritamente um JSON no formato de lista: "
    '[{"question": "...", "answer": "..."}, ...]'
)

FLASHCARDS_PROMPT = (
    "Com base no material de estudo a seguir, crie entre 6 e 15 flashcards essenciais "
    "para quem precisa dominar este conteúdo.{focus_section}\n\n"
    "Título do material: {title}\n\n"
    "Texto do material:\n"
    "---\n"
    "{text}\n"
    "---\n\n"
    "Retorne apenas o JSON com a lista de flashcards."
)


def _clean_json_text(raw: str) -> str:
    text = raw.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    return text


def _parse_flashcards(raw_json: str) -> list[dict[str, str]]:
    cleaned = _clean_json_text(raw_json)
    try:
        data = json.loads(cleaned)
    except Exception as exc:
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(cleaned[start : end + 1])
            except Exception:
                raise AIError("Não foi possível processar o formato dos flashcards gerados.") from exc
        else:
            raise AIError("Não foi possível processar o formato dos flashcards gerados.") from exc

    if isinstance(data, dict):
        for key in ("flashcards", "cards", "items", "data"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
        else:
            data = [data]

    if not isinstance(data, list):
        raise AIError("Formato de flashcards inválido retornado pela IA.")

    cards: list[dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        q = str(item.get("question") or item.get("pergunta") or item.get("front") or "").strip()
        a = str(item.get("answer") or item.get("resposta") or item.get("back") or "").strip()
        if q and a:
            cards.append({"question": q, "answer": a})

    if not cards:
        raise AIError("A IA não identificou conceitos suficientes para gerar flashcards.")

    return cards


def score_chunk_focus(chunk: str, focus: str | None) -> int:
    """Calcula a pontuação de relevância de um bloco em relação ao foco."""
    if not focus or not focus.strip():
        return 0
    keywords = [k.lower() for k in re.findall(r"\w+", focus) if len(k) > 2]
    if not keywords:
        return 0
    c_low = chunk.lower()
    return sum(c_low.count(kw) for kw in keywords)


def generate_flashcards_from_text(
    title: str, text: str, focus: str | None = None
) -> tuple[list[dict[str, str]], str]:
    """Gera lista de flashcards ({question, answer}).

    Se `focus` for informado (ex.: 'Modelo OSI', 'Criptografia Assimétrica'),
    direciona a IA especificamente para esse tema no documento.
    """
    clean_text = text.strip()
    if not clean_text:
        raise AIError("O material não contém texto suficiente para gerar flashcards.")

    focus_section = ""
    if focus and focus.strip():
        focus_section = (
            f"\n\nATENÇÃO - FOCO ESPECÍFICO DEFINIDO PELO ALUNO:\n"
            f"O aluno determinou que os flashcards DEVEM focar prioritariamente no tema: '{focus.strip()}'.\n"
            f"Concentre as perguntas e respostas nos conceitos, processos e distinções ligados a esse foco."
        )

    # Texto curto/médio (até ~35k caracteres)
    if len(clean_text) <= 35_000:
        prompt = FLASHCARDS_PROMPT.format(title=title, text=clean_text, focus_section=focus_section)
        raw_output, model = generate_text(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3,
            max_output_tokens=3072,
        )
        return _parse_flashcards(raw_output), model

    # Texto longo: divide em blocos de 25k caracteres
    chunks = split_into_chunks(clean_text, max_chars=25_000)

    # Se houver foco, prioriza os blocos onde os termos do foco mais aparecem
    if focus and focus.strip():
        chunks.sort(key=lambda c: score_chunk_focus(c, focus), reverse=True)

    all_cards: list[dict[str, str]] = []
    last_model = "gemini"

    # Processa até os 3 blocos mais relevantes
    selected_chunks = chunks[:3]
    for idx, chunk in enumerate(selected_chunks):
        prompt = FLASHCARDS_PROMPT.format(
            title=f"{title} (Seção {idx + 1}/{len(selected_chunks)})",
            text=chunk,
            focus_section=focus_section,
        )
        raw_output, last_model = generate_text(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3,
            max_output_tokens=2048,
        )
        try:
            chunk_cards = _parse_flashcards(raw_output)
            all_cards.extend(chunk_cards)
        except Exception:
            log.warning("Falha ao parsear bloco %d de flashcards", idx + 1)
            continue

    if not all_cards:
        raise AIError("Não foi possível extrair flashcards deste material com o foco solicitado.")

    return all_cards[:20], last_model
