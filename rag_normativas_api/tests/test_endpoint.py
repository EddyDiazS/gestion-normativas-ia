"""
Test directo del endpoint /ask para verificar que funciona
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Test 1: Pregunta sobre artículo 13
print("=" * 70)
print("TEST 1: Búsqueda del Artículo 13")
print("=" * 70)

question_1 = "Me podrias explicar el articulo 13"
payload_1 = {
    "question": question_1,
    "top_k": 5,
    "session_id": "test1"
}

try:
    response = requests.post(f"{BASE_URL}/ask", json=payload_1, timeout=30)
    print(f"\nPregunta: {question_1}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        answer = data.get("answer", "")
        verified = data.get("verified", False)
        sources = data.get("sources", [])
        
        print(f"Verificada: {verified}")
        print(f"Fuentes: {len(sources)}")
        print(f"\nRespuesta (primeros 300 chars):")
        print(f"{answer[:300]}")
        
        # Verificación
        if "no se encuentra establecida explicitamente" in answer.lower():
            print("\n❌ PROBLEMA: Sigue retornando 'no se encontró información'")
        else:
            print("\n✅ ÉXITO: Retorna información del artículo 13")
    else:
        print(f"ERROR: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ ERROR DE CONEXIÓN: {e}")
    print("El servidor probablemente no está ejecutándose en 127.0.0.1:8000")

# Test 2: Pregunta general
print("\n" + "=" * 70)
print("TEST 2: Pregunta General")
print("=" * 70)

question_2 = "¿Cuáles son tus funciones?"
payload_2 = {
    "question": question_2,
    "top_k": 5,
    "session_id": "test2"
}

try:
    response = requests.post(f"{BASE_URL}/ask", json=payload_2, timeout=30)
    print(f"\nPregunta: {question_2}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        answer = data.get("answer", "")
        
        print(f"\nRespuesta (primeros 300 chars):")
        print(f"{answer[:300]}")
        
        if "funciones" in answer.lower():
            print("\n✅ ÉXITO: Responde sobre sus funciones")
        else:
            print("\n❌ Respuesta inesperada")
    else:
        print(f"ERROR: {response.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 70)
