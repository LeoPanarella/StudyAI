"""Extração de texto de PDFs usando PyMuPDF (MuPDF)."""

import re
from dataclasses import dataclass

import pymupdf


class PdfExtractionError(Exception):
    """Erro amigável para retornar ao usuário."""


@dataclass
class ExtractedPdf:
    text: str
    page_count: int
    char_count: int
    warning: str | None = None


_MULTI_BLANK_LINES = re.compile(r"\n{3,}")
_TRAILING_SPACES = re.compile(r"[ \t]+\n")
_PAGE_SEP = "\n\n"


def is_pdf(data: bytes) -> bool:
    """Verifica a assinatura do arquivo (não confiamos só na extensão / content-type)."""
    return data[:1024].lstrip().startswith(b"%PDF-")


def extract_text(data: bytes) -> ExtractedPdf:
    if not is_pdf(data):
        raise PdfExtractionError("O arquivo enviado não é um PDF válido.")

    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception as exc:  # arquivo corrompido, etc.
        raise PdfExtractionError("Não foi possível abrir o PDF (arquivo corrompido?).") from exc

    try:
        if doc.needs_pass and not doc.authenticate(""):
            raise PdfExtractionError("Este PDF está protegido por senha. Remova a senha e envie novamente.")

        pages: list[str] = []
        for page in doc:
            page_text = page.get_text("text", sort=True) or ""
            page_text = _TRAILING_SPACES.sub("\n", page_text).strip()
            if page_text:
                pages.append(page_text)
        page_count = doc.page_count
    finally:
        doc.close()

    text = _PAGE_SEP.join(pages)
    text = _MULTI_BLANK_LINES.sub("\n\n", text).strip()

    warning = None
    if not text:
        warning = (
            "Nenhum texto foi encontrado neste PDF. Provavelmente é um documento escaneado "
            "(imagens). A geração de resumos e flashcards precisa de texto extraível."
        )
    elif len(text) < 200:
        warning = "Muito pouco texto foi extraído deste PDF; os resultados da IA podem ser limitados."

    return ExtractedPdf(text=text, page_count=page_count, char_count=len(text), warning=warning)
