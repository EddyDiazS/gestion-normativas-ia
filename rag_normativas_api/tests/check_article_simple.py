"""
Script simple para verificar el formato de los artículos en memoria
sin cargar embeddings innecesarios
"""

import sys
sys.path.insert(0, '/'.join(__file__.split('/')[:-1]))

from app.rag.loader import load_documents

# Cargar documentos
print("Cargando documentos...")
documents = load_documents("data/normativas")

# Buscar artículo 13
print("\n=== Buscando ARTÍCULO 13 ===")
article_13_docs = []
for doc in documents:
    meta = doc.get("metadata", {})
    article = str(meta.get("article", "")).strip().lower()
    if "13" in article:
        article_13_docs.append(doc)

print(f"Encontrados {len(article_13_docs)} documentos con '13'")

if article_13_docs:
    print("\nPrimeros 3 documentos del artículo 13:")
    for i, doc in enumerate(article_13_docs[:3]):
        meta = doc.get("metadata", {})
        content = doc.get("content", "")[:150].replace("\n", " ")
        print(f"\n  [{i+1}] Metadata article: '{meta.get('article')}'")
        print(f"      Content: {content}...")
else:
    print("\nNo se encontró '13' en los artículos.")
    
print("\n=== Mostrando primeros 30 artículos ===")
articles_found = {}
for doc in documents:
    meta = doc.get("metadata", {})
    article = str(meta.get("article", "")).strip()
    if article and article != "N/A":
        if article not in articles_found:
            articles_found[article] = 0
        articles_found[article] += 1

# Mostrar los primeros 30
sorted_articles = sorted(articles_found.items(), key=lambda x: x[0])
for article, count in sorted_articles[:30]:
    print(f"  {article:25} (chunks: {count})")
