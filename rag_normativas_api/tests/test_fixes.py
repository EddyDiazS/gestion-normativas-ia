"""
Test para verificar los fixes de:
1. Preguntas generales (saludos, funciones del bot)
2. Búsqueda de artículos específicos
"""

from app.rag.generator import _is_general_greeting, _get_general_answer
from app.rag.retriever import _extract_article_numbers

# Tests para preguntas generales
test_greetings = [
    "Hola",
    "¿Hola?",
    "Hola, ¿cómo estás?",
    "¿Cuáles son tus funciones?",
    "¿Qué puedes hacer?",
    "¿Para qué sirves?",
    "¿Quién eres?",
]

print("=== Test 1: Preguntas Generales ===")
for question in test_greetings:
    is_general = _is_general_greeting(question)
    print(f"\n'{question}'")
    print(f"  ¿Es pregunta general? {is_general}")
    if is_general:
        answer = _get_general_answer(question)
        print(f"  Respuesta (primeros 100 chars): {answer[:100]}...")

# Tests para extracción de números de artículos
test_article_queries = [
    "explícame el artículo 10",
    "¿Qué dice el artículo 10 de la normativa académica?",
    "Cuál es el artículo número 5",
    "art. 12 de las normas",
    "Explícame los artículos 10, 15 y 20",
    "Para qué sirve el artículo 11",
    "No menciono números aquí",
]

print("\n\n=== Test 2: Extracción de Números de Artículos ===")
for query in test_article_queries:
    articles = _extract_article_numbers(query)
    print(f"\n'{query}'")
    print(f"  Artículos extraídos: {articles if articles else 'Ninguno'}")

print("\n✓ Tests completados")
