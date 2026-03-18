#!/usr/bin/env python3
"""
Test para validar que _clean_response_for_verification() funciona correctamente.
"""

import re


def _clean_response_for_verification(answer_text: str) -> str:
    """
    Post-procesamiento: limpia la respuesta de referencias a artículos tangenciales.
    """
    cleaned = answer_text
    
    patterns_to_remove = [
        r"\s*El Parágrafo del Artículo 36 además indica.*?[\.\n]",
        r"\s*En caso de contar con crédito financiero directo o vigente.*?[\.\n]",
        r"\s*\d+\.\s+En caso de contar con crédito financiero.*?[\.\n]",
        r"\s*\(Artículo 36 y Artículo 52\)",
        r"\s*\(Artículo 37\)",
        r",\s*Artículo 37\)",
        r",\s*Artículo 52",
        r",\s*Artículo 36",
    ]
    
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)
    cleaned = re.sub(r"  +", " ", cleaned)
    
    return cleaned.strip()


print("=" * 80)
print("PRUEBA 1: Elimina referencia a Art. 36 en parágrafo")
print("=" * 80)

test_1 = """Por sanciones disciplinarias: La condición de estudiante se pierde si ha sido objeto 
de sanciones disciplinarias (Artículo 41). El Parágrafo del Artículo 36 además indica que la 
reserva de cupo no opera en casos de pérdida de calidad de estudiante por motivos disciplinarios. 
Esto ratifica la imposibilidad de continuar."""

cleaned_1 = _clean_response_for_verification(test_1)
has_art36_1 = "Artículo 36" in cleaned_1
print(f"Texto original contiene 'Artículo 36': True")
print(f"Texto limpio contiene 'Artículo 36': {has_art36_1}")
print(f"✅ CORRECTO (debe ser False)" if not has_art36_1 else "❌ INCORRECTO")
print()

print("=" * 80)
print("PRUEBA 2: Elimina referencia a Art. 36 y 52 entre paréntesis")
print("=" * 80)

test_2 = """El estudiante debe estar a paz y salvo con la Institución (Artículo 36 y Artículo 52)."""

cleaned_2 = _clean_response_for_verification(test_2)
has_art36_2 = "Artículo 36" in cleaned_2
has_art52_2 = "Artículo 52" in cleaned_2
print(f"Contiene 'Artículo 36': {has_art36_2}")
print(f"Contiene 'Artículo 52': {has_art52_2}")
print(f"✅ CORRECTO" if (not has_art36_2 and not has_art52_2) else "❌ INCORRECTO")
print()

print("=" * 80)
print("PRUEBA 3: Mantiene artículos esenciales (41, 78, 80)")
print("=" * 80)

test_3 = """El estudiante pierde cupo (Artículo 41) por reprobación (Artículo 78) 
y puede solicitar reintegro (Artículo 80)."""

cleaned_3 = _clean_response_for_verification(test_3)
has_art41 = "Artículo 41" in cleaned_3
has_art78 = "Artículo 78" in cleaned_3
has_art80 = "Artículo 80" in cleaned_3
print(f"Artículo 41: {has_art41}, Artículo 78: {has_art78}, Artículo 80: {has_art80}")
print(f"✅ CORRECTO" if (has_art41 and has_art78 and has_art80) else "❌ INCORRECTO")
print()

print("=" * 80)
print("PRUEBA 4: Limpia frase sobre 'crédito financiero' ")
print("=" * 80)

test_4 = """Requisitos:
1. Solicitud al Consejo (Art. 80)
2. Consejería académica
3. En caso de contar con crédito financiero directo o vigente con la Institución, 
   el estudiante debe pactar un acuerdo de pago y estar a paz y salvo."""

cleaned_4 = _clean_response_for_verification(test_4)
has_credit_phrase = "crédito financiero" in cleaned_4
print(f"Contiene frase 'crédito financiero': {has_credit_phrase}")
print(f"✅ CORRECTO (debe ser False)" if not has_credit_phrase else "❌ INCORRECTO")
print()

print("=" * 80)
print("RESUMEN")
print("=" * 80)

results = [
    ("Prueba 1: Elimina Art. 36 en párrafo", not has_art36_1),
    ("Prueba 2: Elimina Art. 36 y 52 entre paréntesis", not has_art36_2 and not has_art52_2),
    ("Prueba 3: Mantiene artículos esenciales", has_art41 and has_art78 and has_art80),
    ("Prueba 4: Elimina frase de crédito financiero", not has_credit_phrase),
]

passed = sum(1 for _, result in results if result)
total = len(results)

for test_name, result in results:
    status = "✅" if result else "❌"
    print(f"{status} {test_name}")

print(f"\nResultado: {passed}/{total} pruebas pasadas")
if passed == total:
    print("🎉 Limpieza funcionando correctamente!")
else:
    print(f"⚠️ {total - passed} prueba(s) fallida(s)")
