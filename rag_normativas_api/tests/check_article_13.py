"""
Verificar que el artículo 13 existe en los datos
"""

from app.services.bootstrap import rag_engine

# Listar algunos artículos para ver el formato de metadatos
print("=== Primeros 10 chunks y sus metadatos ===\n")
for i, chunk in enumerate(rag_engine.chunks[:20]):
    meta = chunk.get("metadata", {})
    article = meta.get("article", "N/A")
    document = meta.get("document", "N/A")
    content_preview = chunk.get("content", "")[:80].replace("\n", " ")
    print(f"{i:2}. Article: {article:20} | Doc: {document:20}")
    if i < 5:
        print(f"    Content: {content_preview}...\n")

# Buscar artículo 13 específicamente
print("\n=== Buscando ARTÍCULO 13 ===")
article_13_chunks = []
for chunk in rag_engine.chunks:
    meta = chunk.get("metadata", {})
    article = str(meta.get("article", "")).strip().lower()
    if "articulo" in article and "13" in article:
        article_13_chunks.append(chunk)

print(f"Encontrados {len(article_13_chunks)} chunks con artículo 13")

if article_13_chunks:
    print("\nPrimeros 3 chunks del artículo 13:")
    for i, chunk in enumerate(article_13_chunks[:3]):
        meta = chunk.get("metadata", {})
        content = chunk.get("content", "")[:200].replace("\n", " ")
        print(f"\n  [{i+1}] Metadata: {meta}")
        print(f"      Content: {content}...")
else:
    print("\nNo se encontró artículo 13. Mostrando todos los artículos disponibles:")
    articles_found = set()
    for chunk in rag_engine.chunks[:100]:
        meta = chunk.get("metadata", {})
        article = str(meta.get("article", "")).strip()
        if article and article != "N/A":
            articles_found.add(article)
    
    print(f"Artículos encontrados (primeros 20):")
    for article in sorted(articles_found)[:20]:
        print(f"  - {article}")
