import sys
from pathlib import Path

import streamlit as st

# Ajuste de path para importar o módulo core
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
    sanitize_text_for_ai,  # 👈 NOVO
)
from core.ocr_ia import (
    OCRExtractionError,
    extract_text_from_scanned_pdf_bytes,
)


def main():
    st.set_page_config(
        page_title="Extração de Dados PDF + RAG",
        page_icon="📄",
        layout="wide",
    )

    # Garante que, para cada sessão do Streamlit, o "banco" JSON
    # comece limpo (somente dados desta sessão).
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
        help="Sua chave é usada apenas nesta sessão. Nenhuma informação sensível será armazenada.",
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

    # ==========================
    # COLUNA 1 – EXTRAÇÃO
    # ==========================
    with col1:
        st.subheader("1. Extração de dados do PDF")
        st.info(
            "Nesta seção, você poderá enviar um documento em PDF. "
            "O sistema irá ler o conteúdo e identificar se é um PDF com texto ou "
            "possivelmente um PDF escaneado (apenas imagem). "
            "A IA irá extrair os campos: Nome, CPF, RG, Data de Nascimento, Gênero e Órgão Emissor."
        )

        uploaded_file = st.file_uploader(
            "📎 Envie um arquivo PDF de documento",
            type=["pdf"],
        )

        if uploaded_file is not None:
            st.write(f"**Arquivo recebido:** {uploaded_file.name}")

            file_bytes = uploaded_file.read()

            # 1) Leitura básica do PDF (texto nativo, se houver)
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

            # Pré-visualização do texto extraído pelo pypdf
            st.markdown("### 🧾 Pré-visualização do texto extraído")
            if result.full_text.strip():
                st.text_area(
                    "Texto extraído do PDF (texto nativo)",
                    value=result.full_text,
                    height=300,
                )
            else:
                st.warning(
                    "Nenhum texto foi extraído deste PDF. "
                    "Ele provavelmente é um documento escaneado apenas como imagem."
                )

            # ==========================
            # OCR (Tesseract) para PDFs escaneados
            # ==========================
            if result.is_probably_scanned or not result.full_text.strip():
                st.markdown("### 🔎 Leitura de PDF escaneado com OCR")

                if st.button("🧠 Usar OCR para ler este documento"):
                    with st.spinner("Usando OCR para ler o documento..."):
                        try:
                            ocr_result = extract_text_from_scanned_pdf_bytes(
                                file_bytes=file_bytes,
                                api_key=st.session_state["OPENAI_API_KEY"],  # ignorada no Tesseract
                            )
                        except OCRExtractionError as e:
                            st.error(f"❌ Erro no OCR: {e}")
                        except Exception as e:
                            st.error(f"❌ Erro inesperado no OCR: {e}")
                        else:
                            texto_ocr = ocr_result.full_text

                            st.markdown(
                                f"📝 **Texto OCR extraído:** {len(texto_ocr)} caracteres"
                            )

                            if not texto_ocr.strip():
                                st.warning(
                                    "O OCR não conseguiu extrair texto legível deste documento."
                                )
                            else:
                                st.success("✅ Texto extraído via OCR com sucesso!")

                                st.text_area(
                                    "Texto extraído via OCR",
                                    value=texto_ocr,
                                    height=300,
                                )

                                # 🔧 SANITIZAÇÃO DO TEXTO ANTES DE ENVIAR PARA A IA
                                safe_ocr_text = sanitize_text_for_ai(texto_ocr)

                                with st.spinner(
                                    "Chamando a IA para extrair campos a partir do texto OCR..."
                                ):
                                    try:
                                        people = extract_people_from_text(
                                            document_text=safe_ocr_text,
                                            api_key=st.session_state["OPENAI_API_KEY"],
                                        )
                                    except ExtractionAIError as e:
                                        st.error(
                                            f"❌ Erro na extração de campos a partir do texto OCR: {e}"
                                        )
                                        people = []
                                    except Exception as e:
                                        st.error(
                                            f"❌ Erro inesperado na extração de campos a partir do texto OCR: {e}"
                                        )
                                        people = []

                                if people:
                                    st.success(
                                        f"✅ Campos extraídos com sucesso para {len(people)} pessoa(s) a partir do OCR!"
                                    )

                                    # Persistência no documentos.json
                                    records = build_document_records(
                                        people=people,
                                        source_file_name=uploaded_file.name,
                                        source_pdf_is_scanned=True,
                                    )
                                    add_document_records(records)

                                    st.info(
                                        f"💾 {len(records)} registro(s) salvo(s) na base local "
                                        "`data/documentos.json` (origem: OCR)."
                                    )

                                    public_list = people_to_public_dict_list(people)

                                    for idx, person_dict in enumerate(public_list, start=1):
                                        st.markdown(f"#### 👤 Pessoa (OCR) {idx}")
                                        st.json(person_dict)
                                else:
                                    st.warning(
                                        "Nenhuma pessoa foi identificada a partir do texto OCR."
                                    )

            # ==========================
            # Extração de campos do texto nativo (quando houver)
            # ==========================
            st.markdown("### 🧬 Extração de campos do documento com IA")

            if not result.full_text.strip():
                st.info(
                    "Não há texto nativo extraído suficiente para enviar à IA. "
                    "Se este documento for apenas uma imagem, utilize o OCR acima "
                    "para extrair o texto antes."
                )
            else:
                if st.button("🔍 Extrair campos com IA (uma ou mais pessoas)"):
                    # 🔧 SANITIZAÇÃO DO TEXTO ANTES DE ENVIAR PARA A IA
                    safe_text = sanitize_text_for_ai(result.full_text)

                    with st.spinner("Chamando a IA para extrair campos..."):
                        try:
                            people = extract_people_from_text(
                                document_text=safe_text,
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

                                # Persistência no documentos.json
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

    # ==========================
    # COLUNA 2 – FUTURO RAG
    # ==========================
    with col2:
        st.subheader("2. Consulta aos dados (RAG)")
        st.info(
            "Após extrair e armazenar os dados, você poderá fazer perguntas em linguagem natural "
            "sobre os documentos, e o sistema RAG irá responder com base na base de dados."
        )

        st.markdown(
            "> 💬 Em breve: aqui ficará o chat para consulta inteligente aos dados extraídos "
            "usando RAG. Nesta etapa, já implementamos o upload, a leitura (texto / OCR) e a "
            "extração via IA; o próximo passo é persistir embeddings e habilitar as consultas."
        )


if __name__ == "__main__":
    main()
