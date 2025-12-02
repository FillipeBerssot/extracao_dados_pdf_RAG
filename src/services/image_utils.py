import io
import base64
from PIL import ImageEnhance
from pdf2image import convert_from_bytes


def convert_pdf_to_images(file_bytes):
    """Converte bytes de PDF em uma lista de imagens PIL."""
    return convert_from_bytes(file_bytes)


def melhorar_imagem(img):
    """Aplica filtros para melhorar a legibilidade para OCR."""
    img = img.convert('L')

    enhancer_contrast = ImageEnhance.Contrast(img)
    img = enhancer_contrast.enhance(2.0)

    enhancer_sharpness = ImageEnhance.Sharpness(img)
    img = enhancer_sharpness.enhance(2.0)

    return img


def encode_image_to_base64(pil_image):
    """Converte imagem PIL para string base64."""
    buffered = io.BytesIO()

    pil_image.convert("RGB").save(buffered, format="JPEG")
    
    return base64.b64encode(buffered.getvalue()).decode('utf-8')