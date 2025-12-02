from openai import OpenAI
from src.models.schemas import DadosDocumento
from src.services.image_utils import convert_pdf_to_images, melhorar_imagem, encode_image_to_base64
import streamlit as st


def extrair_dados_documento(file_bytes, api_key):
    """
    Fluxo principal: PDF -> Imagens -> Tratamento -> OpenAI -> JSON
    """
    client = OpenAI(api_key=api_key)
    
    raw_images = convert_pdf_to_images(file_bytes)
    processed_images = []
    
    content_payload = [
        {"type": "text", "text": "Analise estas imagens. Extraia os dados solicitados de forma consolidada. Se houver frente e verso, combine as informações."}
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
                "content": "Você é um especialista em extração de dados de documentos brasileiros (RG, CNH e afins)."
            },
            {
                "role": "user",
                "content": content_payload
            }
        ],
        response_format=DadosDocumento,
    )

    return completion.choices[0].message.parsed, processed_images


def consultar_chat_rag(pergunta, dados_json, api_key):
    """Função separada para o Chat RAG"""
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": f"Você é um assistente útil. Responda usando APENAS estes dados JSON: {dados_json}"
            },
            {"role": "user", "content": pergunta}
        ]
    )

    return response.choices[0].message.content