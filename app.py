import streamlit as st
from src.assistant import ask
from src.ingest import ingest_file
import tempfile, os
from datetime import datetime
import json

st.set_page_config(page_title="Страховой ассистент")
st.title("Ассистент по страховому законодательству РК")

def save_feedback(question, answer, sources, rating):
    feedback_file = "feedback.json"
    if os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    sources_serializable = [
        {
            "text": doc[:500], 
            "source": meta.get("source", ""),
            "article": meta.get("article", ""),
            "paragraph": meta.get("paragraph", "")
        }
        for doc, meta in sources
    ]

    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "sources": sources_serializable,
        "rating": rating  
    }
    data.append(feedback_entry)
    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

with st.sidebar:
    st.header("📁 База знаний")
    uploaded = st.file_uploader("Загрузить закон (.docx)", type="docx")
    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as f:
            f.write(uploaded.read())
            ingest_file(f.name)
        st.success(f"{uploaded.name} добавлен в базу")

    if os.path.exists("feedback.json"):
        with open("feedback.json", "r", encoding="utf-8") as f:
            fb_data = json.load(f)
        st.info(f"Собрано отзывов: {len(fb_data)}")
if "messages" not in st.session_state:
    st.session_state.messages = []

for idx, msg in enumerate(st.session_state.messages):
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
            col1, col2 = st.columns([0.1, 0.1])
            with col1:
                if st.button("👍", key=f"like_{idx}"):
                    save_feedback(st.session_state.messages[idx-1]["content"], msg["content"], msg["sources"], "good")
                    st.success("Спасибо за положительный отзыв!")
            with col2:
                if st.button("👎", key=f"dislike_{idx}"):
                    save_feedback(st.session_state.messages[idx-1]["content"], msg["content"], msg["sources"], "bad")
                    st.warning("Спасибо, мы улучшим ответ!")

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
    st.rerun()