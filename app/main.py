import streamlit as st


def main():
    st.set_page_config(
        page_title="Extração de Dados PDF + RAG",
        page_icon="📄",
        layout="wide",
    )

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
            "Nesta seção, você poderá enviar um documento em PDF "
            "e a IA irá extrair os campos: Nome, CPF, RG, Data de Nascimento, Gênero e Orgão Emissor."
        )

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