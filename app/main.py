import sys
from pathlib import Path

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from core.pdf_reader import (
    PDFExtractionError,
    PDFExtractionResult,
    extract_text_from_pdf_bytes,
)
from core.extractor_ai import (
    ExtractionAIError,
    people_to_public_dict_list,
    extract_people_from_text,   
)
from core.utils import (
    build_document_records,
    add_document_records,
    reset_documents_db,
)



def main():
    st.set_page_config(
        page_title="Extração de Dados PDF + RAG",
        page_icon="📄",
        layout="wide",
    )

    if "DB_RESET_DONE" not in st.session_state:
        reset_documents_db()
        st.session_state["DB_RESET_DONE"] = True

    st.title("📄 Extração de Dados de PDFs com IA + RAG")
    st.caption(
        "Protótipo de demonstração para extração automática de dados de documentos "
        "e consulta inteligente desses dados via RAG."
    )

    st.markdown("---")

    # Configurações da API
    st.sidebar.header("⚙️ Configurações da OpenAI")

    api_key = st.sidebar.text_input(
        "Informe sua OpenAI API Key",
        type="password",
        help="Sua chave é usada apenas nesta sessão. Nenhuma informação sensível será armazenada."
    )

    if not api_key:
        st.warning(
            "Por favor, insira sua OpenAI API Key na barra lateral para continuar."
        )
        st.stop()

    st.session_state["OPENAI_API_KEY"] = api_key

    st.success("✅ Chave da OpenAI configurada com sucesso!")

    st.markdown("---")

    # Seções
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Extração de dados do PDF")
        st.info(
            "Nesta seção, você poderá enviar um documento em PDF. "
            "O sistema irá ler o conteúdo e identificar se é um PDF com texto ou "
            "possivelmente um PDF escaneado (apenas imagem). "
            "A IA irá extrair os campos: Nome, CPF, RG, Data de Nascimento, Gênero e Orgão Emissor."
        )

        uploaded_file = st.file_uploader(
            "📎 Envie um arquivo PDF de documento",
            type=["pdf"],
        )

        if uploaded_file is not None:
            st.write(f"**Arquivo recebido:** {uploaded_file.name}")

            file_bytes = uploaded_file.read()

            with st.spinner("Lendo e analisando o PDF..."):
                try:
                    result: PDFExtractionResult = extract_text_from_pdf_bytes(file_bytes)
                except PDFExtractionError as e:
                    st.error(f"❌ Erro ao extrair dados do PDF: {e}")
                    return
                except Exception as e:
                    st.error(f"❌ Erro inesperado ao processar o PDF: {e}")
                    return
                
            st.success("✅ PDF processado com sucesso!")

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Páginas", result.num_pages)
            with col_b:
                st.metric(
                    "Provavelmente scaneado?",
                    "Sim" if result.is_probably_scanned else "Não",
                )
            with col_c:
                st.metric("Tamanho do texto (caracteres)", len(result.full_text))

            st.markdown("### 🧾 Pré-visualização do texto extraído")
            if result.full_text.strip():
                st.text_area(
                    "Texto extraído do PDF",
                    value=result.full_text,
                    height=300,
                )
            else:
                st.warning(
                    "Nenhum texto foi extraído deste PDF. "
                    "Ele provavelmente é um documento scaneado apenas como imagem."
                )

            st.markdown("### 🧬 Extração de campos do documento com IA")

            if not result.full_text.strip():
                st.info(
                    "Não há texto extraído suficiente para enviar à IA. "
                    "Se este documento for apenas uma imagem, será necessário OCR "
                    "para extrair o texto antes (passo que podemos adicionar depois)."
                )
            else:
                if st.button("🔍 Extrair campos com IA (uma ou mais pessoas)"):
                    with st.spinner("Chamando a IA para extrair campos..."):
                        try:
                            people = extract_people_from_text(
                                document_text=result.full_text,
                                api_key=st.session_state["OPENAI_API_KEY"],
                            )
                        except ExtractionAIError as e:
                            st.error(f"❌ Erro na extração via IA: {e}")
                        except Exception as e:
                            st.error(f"❌ Erro inesperado na extração via IA: {e}")
                        else:
                            if not people:
                                st.warning(
                                    "Nenhuma pessoa foi identificada no texto do documento."
                                )
                            else:
                                st.success(
                                    f"✅ Campos extraídos com sucesso para {len(people)} pessoa(s)!"
                                )
                            
                                records = build_document_records(
                                    people=people,
                                    source_file_name=uploaded_file.name,
                                    source_pdf_is_scanned=result.is_probably_scanned,
                                )
                                add_document_records(records)

                                st.info(
                                    f"💾 {len(records)} registro(s) salvo(s) na base local "
                                    "`data/documentos.json`."
                                )

                                public_list = people_to_public_dict_list(people)

                                for idx, person_dict in enumerate(public_list, start=1):
                                    st.markdown(f"#### 👤 Pessoa {idx}")
                                    st.json(person_dict)

    with col2:
        st.subheader("2. Consulta aos dados (RAG)")
        st.info(
            "Após extrair e armazenar os dados, você poderá fazer perguntas em linguagem natural "
            "sobre os documentos, e o sistema RAG irá responder com base na base de dados."
        )

        st.markdown(
            "> 🔧 As funcionalidades de upload, extração e chat ainda serão implementadas nos próximos passos. "
            "Por enquanto estamos só estruturando a interface e a configuração da chave."
        )


if __name__ == "__main__":
    main()