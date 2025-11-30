from __future__ import annotations

from dataclasses import dataclass
from typing import List

from pdf2image import convert_from_bytes
import pytesseract
from PIL import ImageOps, ImageFilter, Image


class OCRExtractionError(Exception):
    """Erro genérico para problemas na extração via OCR."""
    pass


@dataclass
class OCRExtractionResult:
    """
    Representa o resultado da extração OCR de um PDF.

    Atributos:
        full_text: texto completo concatenado de todas as páginas.
        per_page_texts: lista com o texto extraído página a página.
    """
    full_text: str
    per_page_texts: List[str]


def _preprocess_image(img: Image.Image) -> Image.Image:
    """
    Aplica pré-processamento agressivo na imagem para tentar
    melhorar o resultado do OCR em documentos complicados (como RG).
    """
    # 1) Tons de cinza
    proc = img.convert("L")

    # 2) Aumenta contraste automaticamente
    proc = ImageOps.autocontrast(proc)

    # 3) Aumenta um pouco o tamanho (upsample) para facilitar leitura
    scale_factor = 1.5
    new_size = (int(proc.width * scale_factor), int(proc.height * scale_factor))
    proc = proc.resize(new_size, Image.LANCZOS)

    # 4) Binarização simples (preto/branco) - threshold ajustável
    #    Tudo abaixo de 150 vira preto (0), acima vira branco (255)
    proc = proc.point(lambda x: 0 if x < 150 else 255, mode="L")

    # 5) Um sharpen leve para realçar bordas
    proc = proc.filter(ImageFilter.SHARPEN)

    return proc


def extract_text_from_scanned_pdf_bytes(
    file_bytes: bytes,
    api_key: str | None = None,  # mantemos a assinatura compatível, mas não usamos a API key
) -> OCRExtractionResult:
    """
    Usa o Tesseract OCR (com pré-processamento agressivo) para extrair texto
    de um PDF que provavelmente é escaneado.

    Fluxo:
    - Converte o PDF em imagens (uma por página) com pdf2image.
    - Pré-processa cada imagem (cinza, contraste, binarização, resize, sharpen).
    - Para cada página, testa múltiplas configs do Tesseract e escolhe o melhor texto.
    - Concatena os textos em um único string.
    """
    try:
        # Aumentamos o DPI para melhorar a qualidade do OCR
        images = convert_from_bytes(file_bytes, fmt="png", dpi=300)
    except Exception as exc:  # noqa: BLE001
        raise OCRExtractionError(f"Erro ao converter PDF em imagens: {exc}") from exc

    if not images:
        raise OCRExtractionError("Nenhuma página foi gerada a partir do PDF.")

    per_page_texts: List[str] = []

    for page_index, img in enumerate(images):
        try:
            proc = _preprocess_image(img)

            # Diversas configurações do Tesseract para tentar extrair o máximo possível
            configs = [
                "--oem 3 --psm 6",   # bloco de texto
                "--oem 3 --psm 4",   # coluna de texto
                "--oem 1 --psm 6",   # modo legacy + LSTM
                "--oem 3 --psm 7",   # linha única
            ]

            best_text = ""
            for cfg in configs:
                text = pytesseract.image_to_string(
                    proc,
                    lang="por+eng",
                    config=cfg + " -c preserve_interword_spaces=1",
                )
                text = text.strip()
                if len(text) > len(best_text):
                    best_text = text

            page_text = best_text

        except Exception as exc:  # noqa: BLE001
            raise OCRExtractionError(
                f"Erro ao aplicar OCR na página {page_index + 1}: {exc}"
            ) from exc

        per_page_texts.append(page_text)

    full_text = "\n\n".join(per_page_texts).strip()

    return OCRExtractionResult(
        full_text=full_text,
        per_page_texts=per_page_texts,
    )
