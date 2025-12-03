from openai import OpenAI
from src.models.schemas import (
    AnaliseDocumentos,
)
from src.services.image_utils import (
    convert_pdf_to_images, 
    melhorar_imagem, 
    encode_image_to_base64,
)


def extrair_dados_documento(file_bytes, api_key):
    """
    Fluxo principal: PDF -> Imagens -> Tratamento -> OpenAI -> JSON
    """
    client = OpenAI(api_key=api_key)
    
    raw_images = convert_pdf_to_images(file_bytes)
    processed_images = []

    content_payload = [
        {
            "type": "text", 
            "text": """Analise as imagens visualmente. O seu objetivo é extração de texto OCR de alta fidelidade.
            1. Identifique os campos solicitados.
            2. Transcreva o texto EXATAMENTE como ele aparece na imagem (preservando pontos, traços e formatação).
            3. Se um campo estiver ilegível ou não existir, retorne null (não invente dados).
            4. Se houver múltiplos documentos, separe-os."""
        }
    ]
    
    for img in raw_images:
        img_melhorada = melhorar_imagem(img)
        processed_images.append(img_melhorada) 

        base64_img = encode_image_to_base64(img_melhorada)
        content_payload.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
        })


    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "Você é um motor de OCR de precisão para documentos brasileiros. Não corrija erros de ortografia do documento. Não remova pontuação. Extraia o texto literal."
            },
            {
                "role": "user",
                "content": content_payload
            }
        ],
        response_format=AnaliseDocumentos,
    )

    return completion.choices[0].message.parsed, processed_images


def consultar_chat_rag(pergunta, dados_json, api_key):
    """
    Função de RAG (Retrieval-Augmented Generation).
    Recebe a pergunta do usuário e o JSON dos documentos extraídos.
    A IA responde com base APENAS nesses dados.
    client = OpenAI(api_key=api_key)
    """
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": f"""Você é um assistente especializado em análise de documentos.
                Você tem acesso aos seguintes dados extraídos de documentos (formato JSON):
                
                {dados_json}
                
                Instruções:
                1. Responda à pergunta do usuário baseando-se ESTRITAMENTE nesses dados.
                2. Se a informação não estiver no JSON, diga "Não encontrei essa informação nos documentos".
                3. Seja direto e prestativo.
                """
            },
            {"role": "user", "content": pergunta}
        ]
    )
    return response.choices[0].message.content