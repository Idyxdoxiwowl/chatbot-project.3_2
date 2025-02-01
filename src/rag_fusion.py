def fuse_rag_results(results):
    """Применяет RAG Fusion для улучшения выдачи результатов"""
    if not results:
        return []

    unique_articles = {}
    
    for score, article in results:
        if not article:
            continue
        article_id = article.get("id")
        if article_id and article_id not in unique_articles:
            unique_articles[article_id] = (score, article)

    sorted_results = sorted(unique_articles.values(), key=lambda x: x[0], reverse=True)
    
    return sorted_results
