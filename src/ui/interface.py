import streamlit as st
from src.services.ai_service import consultar_chat_rag


def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Configurações")

        api_key = st.text_input("OpenAI API Key", type="password")

        st.divider()
        st.info("ℹ️ Os dados são salvos apenas na memória temporária desta sessão. Ao recarregar a página, tudo é apagado.")
        
        return api_key


def render_chat(api_key):
    st.divider()
    st.subheader("💬 Converse com seus documentos")

    if "dados_documentos" in st.session_state and st.session_state["dados_documentos"]:
        
        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        for message in st.session_state["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Pergunte algo..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            
            st.session_state["messages"].append({"role": "user", "content": prompt})

            contexto = str(st.session_state["dados_documentos"])
            
            with st.chat_message("assistant"):
                with st.spinner("Analisando documentos..."):
                    try:
                        resposta = consultar_chat_rag(prompt, contexto, api_key)
                        st.markdown(resposta)
                        
                        st.session_state["messages"].append({"role": "assistant", "content": resposta})
                    except Exception as e:
                        st.error(f"Erro ao consultar IA: {e}")

    else:
        st.info("👆 Faça o upload e extração de um documento acima para liberar o chat.")