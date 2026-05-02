import streamlit as st
from src.assistant import ask
from src.ingest import ingest_file
import tempfile, os

st.set_page_config(page_title="Страховой ассистент")
st.title("Ассистент по страховому законодательству РК")

with st.sidebar:
    st.header("📁 База знаний")
    uploaded = st.file_uploader("Загрузить закон (.docx)", type="docx")
    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as f:
            f.write(uploaded.read())
            ingest_file(f.name)
        st.success(f"{uploaded.name} добавлен в базу")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and "sources" in msg:
            with st.expander("Источники"):
                for doc, meta in msg["sources"]:
                    source = meta.get("source", "Неизвестный документ")
                    article = meta.get("article", "")
                    paragraph = meta.get("paragraph", "")
                    if article and paragraph:
                        ref = f"{source}, ст. {article}, п. {paragraph}"
                    elif article:
                        ref = f"{source}, ст. {article}"
                    else:
                        ref = source
                    st.caption(f"**{ref}:** {doc[:200]}...")

if question := st.chat_input("Задайте вопрос по страховому законодательству..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("assistant"):
        with st.spinner("Ищу в законах..."):
            answer, chunks = ask(question)
        
        st.write(answer)
        with st.expander("📄 Источники"):
            for doc, meta in chunks:
                source = meta.get("source", "Неизвестный документ")
                article = meta.get("article", "")
                paragraph = meta.get("paragraph", "")
                if article and paragraph:
                    ref = f"{source}, ст. {article}, п. {paragraph}"
                elif article:
                    ref = f"{source}, ст. {article}"
                else:
                    ref = source
                st.caption(f"**{ref}:** {doc[:200]}...")
    
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": chunks})