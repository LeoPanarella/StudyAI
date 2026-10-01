"""Utilidades de texto compartilhadas pelos serviços de IA."""


def split_into_chunks(text: str, max_chars: int) -> list[str]:
    """Divide o texto em partes de até `max_chars`, respeitando parágrafos quando possível."""
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for paragraph in text.split("\n\n"):
        # Parágrafo maior que o limite: quebra à força.
        while len(paragraph) > max_chars:
            if current:
                chunks.append("\n\n".join(current))
                current, current_len = [], 0
            chunks.append(paragraph[:max_chars])
            paragraph = paragraph[max_chars:]
        if current_len + len(paragraph) + 2 > max_chars and current:
            chunks.append("\n\n".join(current))
            current, current_len = [], 0
        current.append(paragraph)
        current_len += len(paragraph) + 2
    if current:
        chunks.append("\n\n".join(current))
    return chunks
