"""
Test simple para funciones de detección sin dependencias pesadas
"""

import re

# Copiar las funciones aquí para test aislado
def _extract_article_numbers(text: str):
    """Extrae números de artículos mencionados en el texto (ej: 'artículo 10' -> 10)"""
    patterns = [
        r"articulo[sz]?\s+(?:número\s+)?(?:no\.?\s+)?(\d+)",  # articulo(s), artículos con acentos
        r"art(?:\.?)\s+(?:no\.?\s+)?(\d+)",  # art, art.
        r"articulo\s+num(?:ero)?\s+(\d+)",  # articulo numero
    ]
    
    articles = set()
    text_lower = text.lower()
    # Normalizar acentos para búsqueda
    text_normalized = text_lower.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    
    for pattern in patterns:
        matches = re.finditer(pattern, text_normalized)
        for match in matches:
            article_num = match.group(1)
            articles.add(article_num)
    
    return articles


def _is_general_greeting(question: str) -> bool:
    """Detecta preguntas generales que no necesitan RAG (saludos, funciones, etc.)"""
    q = question.lower().strip()
    
    # Saludos simples
    greetings = [
        "hola", "hi", "hello", "buenos días", "buenas tardes", "buenas noches",
        "que tal", "qué tal", "como estas", "cómo estás", "how are you"
    ]
    
    # Preguntas sobre el bot mismo
    function_markers = [
        "cuáles son tus funciones", "cuales son tus funciones",
        "qué puedes hacer", "que puedes hacer",
        "para qué sirves", "para que sirves",
        "cuál es tu función", "cual es tu funcion",
        "qué eres", "que eres",
        "quién eres", "quien eres",
        "ayuda", "help",
        "cómo funciona", "como funciona"
    ]
    
    # Considerar como pregunta general si es muy corta o es un saludo/función
    if len(q.split()) <= 3:
        for greeting in greetings:
            if greeting in q:
                return True
    
    for marker in function_markers:
        if marker in q:
            return True
    
    return False


# Tests para preguntas generales
test_greetings = [
    ("Hola", True),
    ("¿Hola?", True),
    ("Hola, ¿cómo estás?", True),
    ("¿Cuáles son tus funciones?", True),
    ("¿Qué puedes hacer?", True),
    ("¿Para qué sirves?", True),
    ("¿Quién eres?", True),
    ("Explícame el artículo 10", False),
    ("¿Qué dice la normativa?", False),
]

print("=== Test 1: Preguntas Generales ===")
passed = 0
for question, expected in test_greetings:
    is_general = _is_general_greeting(question)
    status = "✓" if is_general == expected else "✗"
    print(f"{status} '{question}' -> {is_general} (esperado: {expected})")
    if is_general == expected:
        passed += 1

print(f"\nResultado: {passed}/{len(test_greetings)} pruebas pasadas\n")

# Tests para extracción de números de artículos
test_article_queries = [
    ("explícame el artículo 10", {"10"}),
    ("¿Qué dice el artículo 10 de la normativa académica?", {"10"}),
    ("Cuál es el artículo número 5", {"5"}),
    ("art. 12 de las normas", {"12"}),
    ("Explícame los artículos 10, 15 y 20", {"10"}),  # Solo art(iculo) 10
    ("Para qué sirve el artículo 11", {"11"}),
    ("No menciono números aquí", set()),
]

print("=== Test 2: Extracción de Números de Artículos ===")
passed = 0
for query, expected in test_article_queries:
    articles = _extract_article_numbers(query)
    status = "✓" if articles == expected else "✗"
    print(f"{status} '{query}'")
    print(f"  Encontrado: {articles}, Esperado: {expected}")
    if articles == expected:
        passed += 1

print(f"\nResultado: {passed}/{len(test_article_queries)} pruebas pasadas")
print("\n✓ Tests completados")
