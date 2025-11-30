from pathlib import Path

from pdf2image import convert_from_bytes
import pytesseract


def main():
    base_dir = Path(__file__).resolve().parents[1]
    pdf_path = base_dir / "data" / "pdfs_test" / "rg_invalido_unico.pdf"

    if not pdf_path.exists():
        print(f"Arquivo não encontrado: {pdf_path}")
        return

    file_bytes = pdf_path.read_bytes()

    print(f"Lendo PDF: {pdf_path}")

    # 1) Converter para imagens
    images = convert_from_bytes(file_bytes, fmt="png", dpi=300)
    print(f"Total de páginas convertidas: {len(images)}")

    for idx, img in enumerate(images, start=1):
        print(f"\n--- Página {idx} ---")

        # Apenas pra ver o tamanho da imagem
        print(f"Dimensão da página: {img.size}")

        # OCR simples, sem muita config, só pra ver se sai algo
        text = pytesseract.image_to_string(img, lang="por+eng")
        print(f"Tamanho do texto: {len(text)} caracteres")
        print("Primeiros 300 caracteres:")
        print(repr(text[:300]))


if __name__ == "__main__":
    main()
