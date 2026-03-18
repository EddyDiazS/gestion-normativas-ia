#!/usr/bin/env python
"""Verificar que la extracción de artículos funciona correctamente"""

from app.rag.retriever import _extract_article_numbers

# Test con el texto exacto que el usuario envió
question = 'Me podrias expliacr el articulo 13'
articles = _extract_article_numbers(question)

print(f'Pregunta: {question}')
print(f'Artículos extraídos: {articles}')
print(f'¿Se encontró artículo 13? {"13" in articles}')

# Otros tests
test_cases = [
    'Me podrias expliacr el articulo 13',
    'Explícame el artículo 13',
    'art. 13',
    'Me pide el articulo13 sin espacio',
]

print('\n=== Más tests ===')
for test in test_cases:
    result = _extract_article_numbers(test)
    print(f'{test:40} -> {result}')
