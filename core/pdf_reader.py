from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Optional

from pypdf import PdfReader



class PDFExtractionError(Exception):
    """
    Erro específico para problemas na leitura de PDFs.
    """
    pass


@dataclass
class PDFExtractionResult:
    """
    Representa o resultado da leitura de um PDF.

    Atributos:
        full_text: Todo o texto concatenado do PDF.
        num_pages: Número de páginas do documento.
        is_probably_scanned: Heuristica simples indicando se o PDF
            provavelmente é apenas imagem (pouco ou nenhum texto).
    """
    full_text: str
    num_pages: int
    is_probably_scanned: bool


def _extract_page_text(reader: PdfReader, page_index: int) -> str:
    """
    Extrai o texto de uma página específica do PDF.

    Args:
        reader: Instância de PdfReader já carregado.
        page_index: Índice da página (0-based).

    Returns:
        Texto da página (string, possivelmente vazia).
    """
    page = reader.pages[page_index]

    text = page.extract_text() or ""
    return text


def extract_text_from_pdf_bytes(file_bytes: bytes) -> PDFExtractionResult:
    """
    Lê um PDF a partir de bytes e retorna o texto extraído + metadados básicos.

    Esta função:
        - Carrega o PDf em memória (BytesIO).
        - Itera página por página extraindo o texto.
        - Concatena tudo em um unico texto.
        - Aplica uma heuristica simples para tentar detectar se o PDF
            provavelmente é "scaneado" (imagem, com pouco texto).

    Args:
        file_bytes: Conteúdo bruto do arquivo PDF em bytes.

    Returns:
        Um PDFExtractionResult com:
            - full_text: Texto completo.
            - num_pages: Número de páginas.
            - is_probably_scanned: Booleano indicando se o PDF
                provavelmente é apenas imagem (pouco ou nenhum texto).

    Raises:
        PDFExtractionError: se o arquivo não for um PDF válido ou
            ocorrer algum erro na leitura.
    """
    try:
        pdf_stream = BytesIO(file_bytes)
        reader = PdfReader(pdf_stream)
    except Exception as exc:
        raise PDFExtractionError(f"Não foi possível abrir o PDF: {exc}") from exc
    
    num_pages = len(reader.pages)
    if num_pages == 0:
        raise PDFExtractionError("O PDF não possui páginas.")
    
    all_text_parts: list[str] = []

    for page_index in range(num_pages):
        try:
            page_text = _extract_page_text(reader, page_index)
        except Exception as exc:
            raise PDFExtractionError(
                f"Erro ao extrair texto da página {page_index + 1}: {exc}"
            ) from exc
        
        # Normaliza espaços em branco e quebras de linha
        page_text = page_text.strip()
        if page_text:
            all_text_parts.append(page_text)

    full_text = "\n\n".join(all_text_parts)

    avg_chars_per_page = len(full_text) / max(num_pages, 1)
    is_probably_scanned = avg_chars_per_page < 50

    return PDFExtractionResult(
        full_text=full_text,
        num_pages=num_pages,
        is_probably_scanned=is_probably_scanned,
    )
