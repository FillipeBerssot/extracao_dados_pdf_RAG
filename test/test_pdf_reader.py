from pathlib import Path

from core.pdf_reader import extract_text_from_pdf_bytes, PDFExtractionError


def main():
    base_dir = Path(__file__).resolve().parents[1]

    pdfs_dir = base_dir / "data" / "pdfs_test"
    pdf_path = pdfs_dir / "Dados_pessoais_falsos_texto_3.pdf"

    if not pdf_path.exists():
        print(f"Arquivo não encontrado: {pdf_path}")
        print(f"Caminho esperado: {pdf_path}")
        return

    file_bytes = pdf_path.read_bytes()

    try:
        result = extract_text_from_pdf_bytes(file_bytes)
    except PDFExtractionError as e:
        print("Erro na extração:", e)
        return

    print(f"Número de páginas: {result.num_pages}")
    print(f"Provavelmente scaneado? {result.is_probably_scanned}")
    print("\nTexto (primeiros 500 caracteres):\n")
    print(result.full_text[:500])


if __name__ == "__main__":
    main()
