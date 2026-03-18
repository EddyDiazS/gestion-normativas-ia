"""
Test de normalización de "ARTÍCULO 13"
"""

import re

# Test 1: Normalización simple
original = "ARTÍCULO 13"
print(f"Original: '{original}'")
print(f"Bytes: {original.encode('utf-8')}")

lowered = original.lower()
print(f"\nLowercase: '{lowered}'")
print(f"Bytes: {lowered.encode('utf-8')}")

normalized = lowered.replace("á", "a")
print(f"\nNormalizado (replace á): '{normalized}'")
print(f"Bytes: {normalized.encode('utf-8')}")

# Test 2: Regex en string original
print(f"\n=== Test Regex ===")
pattern = r"articulo[sz]?\s+(\d+)"
print(f"Patrón: {pattern}")

for test_str in [original, lowered, normalized]:
    match = re.search(pattern, test_str)
    print(f"\n'{test_str}' -> Match: {match}")
    if match:
        print(f"  Grupos: {match.groups()}")

# Test 3: Alternative replacement usando decompose
import unicodedata

print(f"\n=== Test con Decompose ===")
decomposed = unicodedata.normalize('NFD', original.lower())
print(f"Decomposed: '{decomposed}'")
print(f"Bytes: {decomposed.encode('utf-8')}")

recomposed = ''.join([c for c in decomposed if unicodedata.category(c) != 'Mn'])
print(f"\nSin acentos (decompose): '{recomposed}'")
print(f"Bytes: {recomposed.encode('utf-8')}")

match = re.search(pattern, recomposed)
print(f"\nRegex match: {match}")
