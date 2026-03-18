"""
Test directo sin depender de FastAPI - para confirmar que el código funciona
"""

import sys
import os

# Asegurar que estamos usando el código actualizado
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.rag.retriever import recuperar_contexto, _extract_article_numbers
from app.rag.loader import load_documents
from app.rag.chunker import divide_by_articles
from app.rag.index import build_faiss_index

question = "Me podrias explicar el articulo 13"

print("=" * 60)
print("TEST DIRECTO: Búsqueda del Artículo 13")
print("=" * 60)
print(f"\nPregunta: {question}\n")

# Paso 1: Extracción de artículos
print("[1] Extracción de números de artículos:")
articles = _extract_article_numbers(question)
print(f"    Artículos encontrados: {articles}")

if not articles:
    print("    ❌ ERROR: No se extrajeron números de artículos")
    sys.exit(1)

# Paso 2: Cargar datos
print("\n[2] Cargando documentos y datos:")
documents = load_documents("data/normativas")
print(f"    Documentos cargados: {len(documents)}")

# Paso 3: Dividir en artículos
print("\n[3] Dividiendo documentos en artículos:")
chunks = divide_by_articles(documents)
print(f"    Chunks creados: {len(chunks)}")

# Paso 4: Crear índice
print("\n[4] Creando índice FAISS:")
index, chunks = build_faiss_index(chunks)
print(f"    Chunks en índice: {len(chunks)}")

# Paso 5: Recuperar contexto
print("\n[5] Recuperando contexto con recuperar_contexto():")
context = recuperar_contexto(question, index, chunks, k=5)
print(f"    Contexto recuperado: {len(context)} chunks")

if not context:
    print("    ❌ ERROR: No se recuperó contexto")
    sys.exit(1)

# Mostrar los chunks encontrados
print("\n[6] Chunks encontrados:")
for i, chunk in enumerate(context, 1):
    meta = chunk.get("metadata", {})
    article = meta.get("article", "N/A")
    document = meta.get("document", "N/A")
    content = chunk.get("content", "")[:120].replace("\n", " ")
    
    print(f"\n    [{i}] {article} ({document})")
    print(f"        Content: {content}...")

# Resumen final
print("\n" + "=" * 60)
if context and any("13" in str(chunk.get("metadata", {}).get("article", "")) for chunk in context):
    print("✅ ÉXITO: El artículo 13 fue recuperado correctamente")
    print("\nEl código funciona. El problema es que el servidor necesita ser")
    print("REINICIADO para cargar los cambios en memoria.")
else:
    print("❌ El artículo 13 NO fue recuperado")
print("=" * 60)
