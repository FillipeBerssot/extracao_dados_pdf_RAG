import sys
import os

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    os.environ['LANG'] = 'C.UTF-8'
    os.environ['LC_ALL'] = 'C.UTF-8'
except AttributeError:
    pass

import streamlit as st

from src.ui.interface import render_sidebar, render_chat
from src.services.ai_service import extrair_dados_documento



# Configuração da Página
st.set_page_config(page_title="Extrator de Dados", page_icon="🕵️", layout="wide")

st.title("🕵️ Extrator de Dados (Documentos PDF + RAG)")
st.markdown("Sistema organizado com **GPT-4o** e **Pré-processamento**.")

api_key = render_sidebar()

if not api_key:
    st.warning("🔒 Insira sua API Key para começar.")
    st.stop()

uploaded_file = st.file_uploader("Envie o documento (PDF)", type=["pdf"])

if uploaded_file is not None:
    if st.button("🔍 Extrair Dados"):
        try:
            with st.spinner("Analisando documentos e separando identidades..."):
                resultado, imagens = extrair_dados_documento(uploaded_file.read(), api_key)

            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Imagens Processadas")
                if len(imagens) > 1:
                    abas = st.tabs([f"Pág {i+1}" for i in range(len(imagens))])
                    for i, aba in enumerate(abas):
                        aba.image(imagens[i], use_container_width=True)
                else:
                    st.image(imagens[0], caption="Página Única", use_container_width=True)
            
            with col2:
                st.subheader("📄 Documentos Identificados")
                st.success(f"Encontrados: {len(resultado.pessoas_identificadas)}")
                
                lista_dados = resultado.pessoas_identificadas
                
                if lista_dados:
                    nomes_abas = [doc.nome_completo or f"Doc {i+1}" for i, doc in enumerate(lista_dados)]
                    abas_docs = st.tabs(nomes_abas)
                    
                    for i, aba in enumerate(abas_docs):
                        with aba:
                            st.json(lista_dados[i].model_dump())
                            st.info(f"Tipo detectado: {lista_dados[i].tipo_documento}")

                if "dados_documentos" not in st.session_state:
                    st.session_state["dados_documentos"] = []
                
                st.session_state["dados_documentos"].append(resultado.model_dump())

        except Exception as e:
            st.error(f"Erro no processamento: {e}")


render_chat(api_key)