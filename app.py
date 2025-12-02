import streamlit as st
import os
import io
import base64

from pydantic import BaseModel, Field
from typing import List, Optional
from openai import OpenAI
from pdf2image import convert_from_bytes



# Configuração da Página
st.set_page_config(
    page_title="Extrator Inteligente de PDFs",
    page_icon="🕵️",
    layout="wide",
)

st.title("🕵️ Extrator de Documentos com IA")
st.markdown("Extração de alta precisão usando **OpenAI GPT-4o** e **Pydantic**.")

# Modelagem de Dados
class DadosDocumento(BaseModel):
    nome_completo: str = Field(description="O nome completo da pessoa portadora do documento.")
    data_nascimento: str = Field(description="Data de nascimento no formato DD/MM/AAAA.")
    numero_rg: Optional[str] = Field(description="Número do RG (Registro Geral)sem pontos ou traços, se houver.")
    numero_cpf: Optional[str] = Field(description="Número do CPF (Cadastro de Pessoas Físicas) sem pontos ou traços, se houver.")
    filiacao: List[str] = Field(description="Lista com os nomes dos pais (filiação).")
    genero: Optional[str] = Field(description="Gênero ou sexo listado no documento (Masculino, Feminino, Outro), se disponível.")
    orgao_emissor: Optional[str] = Field(description="Órgão emissor do documento (ex: SSP/SP, DETRAN), se disponível.")


# Funções Auxiliares
def encode_image_to_base64(pil_image):
    """
    Converte uma imagem PIL para uma string base64
    para enviar à OpenAI.
    """
    buffered = io.BytesIO()
    pil_image.save(buffered, format="JPEG")

    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def processar_documento(uploaded_file, api_key):
    """
    Recebe o arquivo PDF/Imagem, converte, envia para o GTP-4o
    e retorna os dados estruturados.
    """
    client = OpenAI(api_key=api_key)

    images = convert_from_bytes(uploaded_file.read())
    first_page_image = images[0]

    base64_image = encode_image_to_base64(first_page_image)

    with st.spinner("A IA está analisando o documento..."):
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em extração de dados de documentos brasileiros (RG, CNH). Extraia os dados com precisão absoluta."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analise a imagem deste documento e extraia os dados solicitados."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ],
                    }
                ],
                response_format=DadosDocumento,
            )

            return completion.choices[0].message.parsed, first_page_image
    

# Interface do Usuário
with st.sidebar:
    st.header("⚙️ Configurações")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.info("Nota: Usamos o modelo GPT-4o que tem custo por uso.")

if not api_key:
    st.warning("🔒 Por favor, insira sua OpenAI API Key na barra lateral para começar.")
    st.stop()

uploaded_file = st.file_uploader("Envie o documento (PDF)", type=["pdf"])

if uploaded_file is not None:
    if st.button("🔍 Extrair Dados"):
        try:
            dados_extraidos, imagem_doc = processar_documento(uploaded_file, api_key)

            col1, col2 = st.columns([1, 1])

            with col1:
                st.image(imagem_doc, caption="Documento Processado", use_container_width=True)

            with col2:
                st.success("✅ Dados Extraídos com Sucesso!")
                st.json(dados_extraidos.model_dump())

                #Futuro RAG
                if "dados_documentos" not in st.session_state:
                    st.session_state["dados_documentos"] = []
                st.session_state["dados_documentos"].append(dados_extraidos.model_dump())

        except Exception as e:
            st.error(f"❌ Ocorreu um erro ao processar o documento: {e}")
