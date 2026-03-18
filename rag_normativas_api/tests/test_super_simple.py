"""
Test SUPER SIMPLE: solo extracción de artículos y normalización Unicode
SIN cargar embeddings ni índices
"""

from app.rag.retriever import _extract_article_numbers, _normalize_for_regex
import re

question = "Me podrias explicar el articulo 13"

print("=" * 60)
print("TEST SIMPLE: Extracción y Normalización")
print("=" * 60)

# Test 1: Extracción
print(f"\nPregunta: {question}")
articles = _extract_article_numbers(question)
print(f"Artículos extraídos: {articles}")

if "13" in articles:
    print("✅ EXTRACCIÓN FUNCIONA: Se encontró artículo 13")
else:
    print("❌ ERROR EN EXTRACCIÓN: No se encontró artículo 13")

# Test 2: Normalización
print("\n" + "-" * 60)
print("TEST NORMALIZACIÓN UNICODE")
test_articles = [
    "ARTÍCULO 13",
    "artículo 13",
    "ARTICULO 13",
]

for test in test_articles:
    normalized = _normalize_for_regex(test)
    match = re.search(r"articulos?\s+(\d+)", normalized)
    
    print(f"\nOriginal: '{test}'")
    print(f"Normalizado: '{normalized}'")
    print(f"Regex match: {match.group(1) if match else 'NO'}")
    
    if match and match.group(1) == "13":
        print("✅ FUNCIONA")
    else:
        print("❌ NO FUNCIONA")

print("\n" + "=" * 60)
print("TEST COMPLETADO")
print("=" * 60)
