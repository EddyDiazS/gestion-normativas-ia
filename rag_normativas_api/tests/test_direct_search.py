"""
Test simplificado: solo búsqueda directa de artículos sin embeddings
"""

import re
import unicodedata
from app.rag.loader import load_documents
from app.rag.retriever import _extract_article_numbers, _normalize_for_regex

question = "Hola , Me podrias explicar el articulo 13 del reglamento academico"
print(f"Pregunta: {question}\n")

# Paso 1: Extracción de artículos
print("=== Paso 1: Extracción de artículos ===")
articles = _extract_article_numbers(question)
print(f"Artículos extraídos: {articles}")

# Paso 2: Cargar documentos
print("\n=== Paso 2: Cargando documentos ===")
documents = load_documents("data/normativas")
print(f"Documentos cargados: {len(documents)}")

# Paso 3: Búsqueda directa
print("\n=== Paso 3: Búsqueda directa de artículos ===")
direct_article_chunks = []

if articles:
    for doc in documents:
        meta = doc.get("metadata", {})
        article = str(meta.get("article", "")).strip()
        
        # Solo mostrar búsqueda del artículo 13
        if "13" in article:
            print(f"\nVerificando: '{article}'")
            article_normalized = _normalize_for_regex(article.lower())
            print(f"  Normalizado: '{article_normalized}'")
            
            article_match = re.search(r"articulos?\s+(\d+)", article_normalized)
            if article_match:
                article_num = article_match.group(1)
                print(f"  Coincidencia: artículo {article_num}")
                if article_num in articles:
                    print(f"  ✓ ENCONTRADO: {article_num} en {articles}")
                    direct_article_chunks.append(doc)
            else:
                print(f"  ✗ No coincide el regex")

print(f"\n\nTotal de chunks encontrados para artículo(s) {articles}: {len(direct_article_chunks)}")

if direct_article_chunks:
    print("\nPrimeros 2 chunks encontrados:")
    for i, chunk in enumerate(direct_article_chunks[:2]):
        meta = chunk.get("metadata", {})
        content = chunk.get("content", "")[:100].replace("\n", " ")
        print(f"\n  [{i+1}] {meta.get('article')}")
        print(f"       Content: {content}...")

