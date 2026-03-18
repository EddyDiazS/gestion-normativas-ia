"""
Test del flujo completo: pregunta -> extracción -> búsqueda -> respuesta
"""

from app.rag.retriever import _extract_article_numbers, recuperar_contexto
from app.services.bootstrap import rag_engine

question = "Hola , Me podrias explicar el articulo 13 del reglamento academico"

print(f"Pregunta: {question}\n")

# Paso 1: Extracción de artículos
print("=== Paso 1: Extracción de artículos ===")
articles = _extract_article_numbers(question)
print(f"Artículos extraídos: {articles}")

# Paso 2: Búsqueda directa usando recuperar_contexto
print("\n=== Paso 2: Búsqueda de contexto ===")
context = recuperar_contexto(question, rag_engine.index, rag_engine.chunks, k=5)
print(f"Contexto recuperado: {len(context)} chunks")

if context:
    for i, chunk in enumerate(context):
        meta = chunk.get("metadata", {})
        article = meta.get("article", "N/A")
        document = meta.get("document", "N/A")
        content = chunk.get("content", "")[:100].replace("\n", " ")
        print(f"\n  [{i+1}] Article: {article}")
        print(f"       Document: {document}")
        print(f"       Content: {content}...")
else:
    print("  ❌ No se recuperó contexto!")
    
# Paso 3: Intentar responder
print("\n=== Paso 3: Generación de respuesta ===")
answer, verified, sources = rag_engine.answer(question, k=5)
print(f"Respuesta verificada: {verified}")
print(f"Fuentes: {len(sources)}")
print(f"Texto respuesta (primeros 200 chars): {answer[:200]}")
