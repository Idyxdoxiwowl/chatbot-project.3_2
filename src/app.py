import streamlit as st
import pymongo
from pymongo import MongoClient
import numpy as np
from multi_query import generate_multi_queries
from rag_fusion import fuse_rag_results
import ollama

# Подключение к MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["constitution_db"]
collection = db["articles"]

st.title("Constitution AI Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Генерация эмбеддингов через Ollama
def generate_embedding(text):
    client = ollama.Client()
    response = client.embeddings(model="llama3.2:1b", prompt=text)
    return response["embedding"]

# Поиск с Multi Query + RAG Fusion
def search_articles_rag_fusion(query):
    """Поиск статей с использованием RAG Fusion"""
    query_embedding = np.array(generate_embedding(query))
    articles = list(collection.find())

    results = []
    for article in articles:
        article_embedding = np.array(article.get("embedding", []))
        similarity = np.dot(query_embedding, article_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(article_embedding)
        )
        results.append((similarity, article))

    results.sort(reverse=True, key=lambda x: x[0])

    # Отладка - проверяем самые релевантные статьи
    for sim, article in results[:5]:
        print(f"Similarity: {sim:.4f}, Article: {article['id']}")

    return [result[1] for result in results[:5]]

# Интерфейс Streamlit
st.sidebar.subheader("Search Constitution")
search_query = st.sidebar.text_input("Search in Constitution")
if st.sidebar.button("Search"):
    if search_query.strip():
        try:
            results = search_articles_rag_fusion(search_query)
            st.sidebar.write("Search Results:")
            for article in results:
                st.sidebar.markdown(f"- {article['text'][:200]}...")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

# Чат с ботом
st.subheader("Chat with AI")
with st.container():
    user_input = st.text_input("Ask a question about the Constitution:")

    if st.button("Send"):
        if user_input.strip():
            st.session_state["messages"].append({"user": "You", "content": user_input})
            try:
                results = search_articles_rag_fusion(user_input)
                relevant_context = "\n\n".join(article['text'] for article in results)

                bot_response = f"Based on the Constitution, here are some relevant details:\n\n{relevant_context[:500]}..."

                st.session_state["messages"].append({"user": "Bot", "content": bot_response})
            except Exception as e:
                st.error(f"Error: {e}")

    for message in st.session_state["messages"]:
        if message["user"] == "You":
            st.markdown(f"<div style='text-align: left; padding: 8px; background-color: #d9fdd3; border-radius: 10px; margin: 5px 0;'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align: left; padding: 8px; background-color: #f0f0f0; border-radius: 10px; margin: 5px 0;'>{message['content']}</div>", unsafe_allow_html=True)

st.sidebar.subheader("Database Content")
total_documents = collection.count_documents({})
st.sidebar.write(f"Total documents in database: {total_documents}")

preamble = collection.find_one({"id": "preamble"})
if preamble:
    st.sidebar.markdown(f"**Preamble:** {preamble['text'][:200]}...")
