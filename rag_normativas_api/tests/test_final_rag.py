"""
Test final completo del flujo RAG con artículo 13
"""

from app.services.bootstrap import rag_engine
from app.rag.retriever import _extract_article_numbers

question = "Me podrias explicar el articulo 13"

print(f"=== Test Final del RAG Engine ===\n")
print(f"Pregunta: {question}\n")

# Paso 1: Extracción
articles = _extract_article_numbers(question)
print(f"[1] Artículos extraídos: {articles}")

# Paso 2: Búsqueda y respuesta
answer, verified, sources = rag_engine.answer(question, k=5, session_id="test_final")

print(f"\n[2] Respuesta obtenida:")
print(f"    Verificada: {verified}")
print(f"    Fuentes: {len(sources)}")
print(f"    Texto (primeros 300 chars):\n    {answer[:300]}")

if sources:
    print(f"\n[3] Fuentes citadas:")
    for source in sources:
        print(f"    - {source}")

# Verificación final
if "no se encuentra establecida explicitamente" in answer.lower():
    print("\n❌ ERROR: Sigue retornando 'no se encontró información'")
    print("    SOLUCIÓN: El servidor debe ser REINICIADO para cargar los cambios")
else:
    print("\n✅ ÉXITO: El servidor está retornando información del artículo 13")
