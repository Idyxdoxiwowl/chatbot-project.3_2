def generate_multi_queries(query):
    """Генерация разных формулировок запроса"""
    return [
        query,
        f"What does the Constitution say about {query}?",
        f"Definition of {query}",
        f"How is {query} protected?",
        f"Rights related to {query}",
        f"Legal aspects of {query}",
        f"Constitutional provisions regarding {query}",
        f"Explain {query} in the context of the Constitution",
    ]
