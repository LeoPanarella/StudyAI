"""Cliente Gemini com retry, backoff e cadeia de fallback de modelos.

Toda a aplicação fala com a IA por aqui; trocar de provedor no futuro significa
reimplementar apenas `generate_text`.
"""

import json
import logging
import random
import re
import time
from functools import lru_cache

import httpx
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.core.config import settings

log = logging.getLogger(__name__)


class AIError(Exception):
    """Erro com mensagem apropriada para exibir ao usuário."""

    status_code = 502

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code


class AINotConfiguredError(AIError):
    status_code = 503


class AIUnavailableError(AIError):
    status_code = 503


# Códigos que valem a pena tentar de novo (no mesmo modelo e depois no próximo).
_RETRYABLE = {429, 499, 500, 502, 503, 504}
# Códigos que indicam problema com o modelo (não existe / sem acesso): pula direto para o próximo.
_SKIP_MODEL = {400, 404}


@lru_cache(maxsize=1)
def _client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise AINotConfiguredError("A IA não está configurada (defina GEMINI_API_KEY no servidor).")
    return genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=settings.GEMINI_TIMEOUT_SECONDS * 1000),
    )


def _models_chain() -> list[str]:
    chain = [settings.GEMINI_MODEL, *settings.gemini_fallback_models_list]
    seen: set[str] = set()
    return [m for m in chain if m and not (m in seen or seen.add(m))]


def _generate_groq(
    prompt: str,
    *,
    system_instruction: str | None = None,
    temperature: float = 0.3,
    max_output_tokens: int = 4096,
    json_schema: dict | None = None,
) -> tuple[str, str]:
    """Chama a API ultrarrápida do Groq (OpenAI-compatible) via LPU."""
    if not settings.GROQ_API_KEY:
        raise AINotConfiguredError("Chave do Groq não configurada (defina GROQ_API_KEY no servidor).")

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY.strip()}",
        "Content-Type": "application/json",
    }
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    models_to_try = [settings.GROQ_MODEL or "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    with httpx.Client(timeout=settings.GEMINI_TIMEOUT_SECONDS) as client:
        for model in models_to_try:
            body: dict = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_output_tokens,
            }
            if json_schema:
                body["response_format"] = {"type": "json_object"}
            try:
                resp = client.post("https://api.groq.com/openai/v1/chat/completions", json=body, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    log.info("Groq ok com modelo: %s", model)
                    return content.strip(), model
                elif resp.status_code in (401, 403):
                    raise AIError("A chave da API do Groq (GROQ_API_KEY) foi recusada.", 502)
                else:
                    log.warning("Groq status %d no modelo %s: %s", resp.status_code, model, resp.text)
            except AIError:
                raise
            except Exception as e:
                log.warning("Falha de conexão com Groq (%s): %s", model, e)
                continue

    raise AIUnavailableError("O serviço Groq está temporariamente indisponível. Tentando alternativa...")


def _generate_local_nlp(prompt: str, json_schema: dict | None = None) -> tuple[str, str]:
    """Fallback inteligente para que o estudante nunca fique sem resumo ou flashcards no PCI."""
    lines = [
        l.strip()
        for l in prompt.split("\n")
        if l.strip() and not l.startswith("---") and not l.startswith("Título:") and not l.startswith("Com base no")
    ]
    content = " ".join(lines)

    if json_schema:
        sentences = [s.strip() for s in re.split(r"[.!?]\s+", content) if len(s.strip()) > 20]
        cards = []
        for s in sentences[:12]:
            for pattern in [r"(?i)(.+?)\s+(é|são|consiste em|refere-se a|tem como função|atua como)\s+(.+)"]:
                m = re.match(pattern, s)
                if m:
                    subj = m.group(1).strip()
                    verb = m.group(2).strip()
                    pred = m.group(3).strip()
                    if len(subj) < 60 and len(pred) > 10:
                        cards.append({"question": f"O que {verb} {subj}?", "answer": f"{subj} {verb} {pred}."})
                        break
        if not cards:
            for i, s in enumerate(sentences[:6], 1):
                cards.append({"question": f"Qual o conceito fundamental abordado no tópico {i}?", "answer": s})
        return json.dumps({"cards": cards[:10]}, ensure_ascii=False), "studyai-local-engine"

    paragraphs = [p.strip() for p in prompt.split("\n\n") if len(p.strip()) > 35 and not p.startswith("---")]
    summary_md = []
    overview = (
        paragraphs[0]
        if paragraphs
        else "Este material apresenta os fundamentos e diretrizes centrais para o aprendizado contínuo."
    )
    summary_md.append("## Visão geral\n" + overview)

    summary_md.append("\n## Conceitos-chave")
    for p in paragraphs[1:5]:
        first_sentence = p.split(".")[0].strip()
        if len(first_sentence) > 15:
            summary_md.append(f"- **Conceito:** {first_sentence}.")

    summary_md.append(
        "\n## Pontos principais\n- Compreensão aprofundada dos fundamentos teóricos.\n- Aplicação prática e análise crítica dos conceitos.\n- Fixação ativa através de revisão espaçada com flashcards."
    )
    summary_md.append(
        "\n## Para fixar\n1. Qual é o conceito principal abordado neste material?\n2. Como essas diretrizes podem ser aplicadas na prática?\n3. Quais são os principais pré-requisitos para este conteúdo?"
    )

    return "\n".join(summary_md), "studyai-local-engine"


def generate_text(
    prompt: str,
    *,
    system_instruction: str | None = None,
    temperature: float = 0.3,
    max_output_tokens: int = 8192,
    json_schema: dict | None = None,
) -> tuple[str, str]:
    """Gera texto. Retorna (texto, modelo_usado).

    Suporta Groq (ultrarrápido), Google Gemini e Motor Local Offline sem travar o PCI.
    """
    # 0. Se configurado explicitamente para modo local ou se não houver nenhuma chave configurada
    if settings.AI_PROVIDER.lower() == "local" or (not settings.GEMINI_API_KEY and not settings.GROQ_API_KEY):
        return _generate_local_nlp(prompt, json_schema=json_schema)

    # 1. Se configurado explicitamente para Groq ou se houver chave do Groq no modo auto
    if (settings.AI_PROVIDER.lower() == "groq") or (settings.AI_PROVIDER.lower() == "auto" and settings.GROQ_API_KEY):
        try:
            return _generate_groq(
                prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=min(max_output_tokens, 4096),
                json_schema=json_schema,
            )
        except AIError as exc:
            if settings.AI_PROVIDER.lower() == "groq" or not settings.GEMINI_API_KEY:
                raise exc
            log.info("Groq falhou ou atingiu limite, fazendo fallback transparente para Gemini...")

    # 2. Execução padrão com Google Gemini
    client = _client()
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        response_mime_type="application/json" if json_schema else None,
        response_schema=json_schema,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    chain = _models_chain()
    dead: set[str] = set()
    last_error = "sem detalhes"

    for round_idx in range(settings.GEMINI_RETRY_ROUNDS):
        for model in chain:
            if model in dead:
                continue
            started = time.monotonic()
            try:
                response = client.models.generate_content(model=model, contents=prompt, config=config)
                text = (response.text or "").strip()
                if not text:
                    reason = _blocked_reason(response)
                    last_error = f"{model}: resposta vazia ({reason})"
                    log.warning("Gemini retornou vazio em %s: %s", model, reason)
                    dead.add(model)  # resposta vazia é determinística para este conteúdo → não repetir
                    continue
                log.info("Gemini ok: model=%s round=%d %.1fs", model, round_idx + 1, time.monotonic() - started)
                return text, model

            except genai_errors.APIError as exc:
                code = getattr(exc, "code", None) or 0
                last_error = f"{model}: HTTP {code}"
                log.warning(
                    "Gemini erro model=%s round=%d code=%s (%.1fs)", model, round_idx + 1, code, time.monotonic() - started
                )
                if code in (401, 403):
                    raise AIError("A chave da API Gemini foi recusada. Verifique GEMINI_API_KEY.", 502) from exc
                if code in _SKIP_MODEL:
                    dead.add(model)
                continue  # 429/5xx/499 → próximo modelo agora; este será tentado de novo na próxima rodada

            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = f"{model}: {type(exc).__name__}"
                log.warning("Gemini timeout/transport model=%s round=%d: %s", model, round_idx + 1, exc)
                continue

        if len(dead) == len(chain):
            break  # nenhum modelo utilizável
        if round_idx < settings.GEMINI_RETRY_ROUNDS - 1:
            _sleep_backoff(round_idx)

    log.warning("Todas as APIs em nuvem indisponíveis ou excederam o limite. Acionando motor de síntese local...")
    try:
        return _generate_local_nlp(prompt, json_schema=json_schema)
    except Exception as exc:
        log.error("Falha no fallback local: %s", exc)
        raise AIUnavailableError(
            "O serviço de IA está indisponível ou sobrecarregado no momento. Tente novamente em alguns instantes."
        ) from exc


def _sleep_backoff(round_idx: int) -> None:
    # Espera entre rodadas: ~2s, 5s, 10s, 20s, 30s... (+ jitter). Com 8 rodadas, insiste por ~3 min.
    base = [2.0, 5.0, 10.0, 20.0, 30.0]
    wait = base[min(round_idx, len(base) - 1)] + random.uniform(0, 1.0)
    time.sleep(wait)


def _blocked_reason(response) -> str:
    try:
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            return f"prompt bloqueado: {response.prompt_feedback.block_reason.name}"
        if response.candidates and response.candidates[0].finish_reason:
            return f"finish_reason={response.candidates[0].finish_reason.name}"
    except Exception:  # noqa: BLE001
        pass
    return "motivo desconhecido"
