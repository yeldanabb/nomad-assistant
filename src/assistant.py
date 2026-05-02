from groq import Groq
from retrieve import retrieve
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

SYSTEM_PROMPT = """Ты — юридический ассистент страховой компании Nomad Insurance.
Отвечай строго на основе предоставленных фрагментов законодательства.
Каждый фрагмент содержит метаданные: [Название закона, Статья N, Пункт M].
ОБЯЗАТЕЛЬНО указывай в ответе номер статьи и пункта, например: "Согласно статье 12-2, пункту 3 ..."
Если ответа нет в документах - скажи об этом честно.
Не добавляй вымышленные статьи или законы."""

def ask(question: str):
    context_chunks = retrieve(question, top_k=5)
    context_parts = []
    for text, metadata in context_chunks:
        source = metadata.get("source", "Неизвестный источник")
        article = metadata.get("article", "")
        paragraph = metadata.get("paragraph", "")
        if article and paragraph:
            ref = f"[{source}, Статья {article}, Пункт {paragraph}]"
        elif article:
            ref = f"[{source}, Статья {article}]"
        else:
            ref = f"[{source}]"
        context_parts.append(f"{ref}\n{text}")

    context = "\n\n".join(context_parts)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Контекст из законов:\n{context}\n\nВопрос: {question}"}
        ],
        temperature=0.15,
        max_tokens=1500
    )
    answer = response.choices[0].message.content.strip()
    if "статья" not in answer.lower() and "статье" not in answer.lower():
        answer += "\n\n*Внимание: ответ не содержит ссылок на конкретные статьи. Проверьте информацию по первоисточникам.*"
    return answer, context_chunks