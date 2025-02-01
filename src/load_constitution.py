from pymongo import MongoClient
import ollama
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["constitution_db"]
collection = db["articles"]

def generate_embedding(text):
    """Генерация эмбеддинга через Ollama и сохранение в виде списка"""
    try:
        client = ollama.Client()
        response = client.embeddings(model="llama3.2:1b", prompt=text)
        return response["embedding"]
    except Exception as e:
        logger.error(f"Ошибка при генерации эмбеддинга: {e}")
        return None

def load_constitution(filename):
    """Загрузка Конституции в MongoDB"""
    try:
        collection.delete_many({})  # Очистка базы перед загрузкой

        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()

        sections = content.split("}")
        for i, section in enumerate(sections):
            section = section.strip()
            if section and "{" in section:
                section_text = section.replace("{", "").strip()
                embedding = generate_embedding(section_text)
                if embedding:
                    document = {
                        "id": f"section_{i+1}",
                        "text": section_text,
                        "embedding": embedding,  # Теперь это list вместо Binary
                    }
                    collection.insert_one(document)
                    logger.info(f"Section {i+1} added.")
        
        logger.info("Конституция успешно загружена в MongoDB!")
    except Exception as e:
        logger.error(f"Ошибка при загрузке: {e}")

# Запуск загрузки данных
constitution_path = "constitution.txt"
load_constitution(constitution_path)
