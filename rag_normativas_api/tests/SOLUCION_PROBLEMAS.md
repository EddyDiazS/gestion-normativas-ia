# SOLUCIÓN DE PROBLEMAS - RAG Normativas API

## Problemas Identificados y Solucionados

### Problema 1: Preguntas Generales sin Contexto
**Síntoma**: Cuando se preguntaba "¿Hola?", "¿Cuáles son tus funciones?", etc., el bot respondía "no se encontró información"

**Causa**: El sistema intentaba siempre hacer RAG (Retrieval-Augmented Generation), incluso para preguntas que no requerían consultar documentación.

**Solución**:
1. Agregada función `_is_general_greeting()` en `generator.py` que detecta:
   - Saludos simples ("Hola", "¿Cómo estás?", etc.)
   - Preguntas sobre las funciones del bot ("¿Cuáles son tus funciones?", "¿Qué puedes hacer?", etc.)

2. Agregada función `_get_general_answer()` que retorna respuestas predefinidas sin necesidad de RAG:
   - Respuesta a saludos
   - Listado de funciones principales del asistente

3. Modificado método `answer()` en clase `RAGEngine` para:
   - Detectar preguntas generales primero
   - Si es pregunta general: retornar respuesta directa (sin RAG)
   - Si no: proceder con obtención de contexto normativo

---

### Problema 2: Búsqueda Simple de Artículos
**Síntoma**: Preguntas simples como "explícame el artículo 10" retornaban "no se encontró información", pero preguntas más complejas sí funcionaban.

**Causa**: El retriever usaba principalmente búsqueda semántica (embeddings) sin considerar menciones explícitas de números de artículos en los metadatos de los chunks.

**Solución**:
1. Agregada función `_extract_article_numbers()` que:
   - Extrae números de artículos mencionados explícitamente en la pregunta
   - Usa regex para detectar patrones como "artículo 10", "art. 12", "artículo número 5"
   - Maneja correctamente acentos ("artículo" vs "articulo")

2. Modificada función `recuperar_contexto()` para:
   - **Paso 1**: Buscar artículos mencionados explícitamente en el metadata
   - **Paso 2**: Si encuentra artículos específicos, priorizarlos
   - **Paso 3**: Si hay menos de k resultados, llenar con búsqueda semántica
   - **Paso 4**: Si no hay artículos mencionados, usar búsqueda semántica como antes

---

## Cambios en Archivos

### `app/rag/generator.py`
- Agregadas funciones `_is_general_greeting()` y `_get_general_answer()`
- Modificado método `answer()` para detectar preguntas generales

### `app/rag/retriever.py`
- Agregada función `_extract_article_numbers()` para extraer números de artículos de texto
- Modificada función `recuperar_contexto()` para buscar primero por artículos explícitos en metadata

---

## Pruebas Realizadas

### Test 1: Preguntas Generales ✓
- "Hola" → Detectada como pregunta general → Retorna respuesta de saludo
- "¿Cuáles son tus funciones?" → Detectada como pregunta general → Retorna listado de funciones
- "¿Quién eres?" → Detectada como pregunta general → Retorna introducción del asistente

### Test 2: Extracción de Artículos ✓
- "explícame el artículo 10" → Extrae: {'10'} ✓
- "art. 12 de las normas" → Extrae: {'12'} ✓
- "Cuál es el artículo número 5" → Extrae: {'5'} ✓
- "No menciono números aquí" → Extrae: {} ✓

---

## Comportamiento Esperado Ahora

### Antes (función NO implementada):
```
Usuario: "¿Hola?"
Bot: "La información solicitada no se encuentra establecida explícitamente en la normativa consultada."

Usuario: "Explícame el artículo 10"
Bot: "La información solicitada no se encuentra establecida explícitamente en la normativa consultada."
```

### Después (función implementada):
```
Usuario: "¿Hola?"
Bot: "¡Hola! Soy tu asistente de consultas normativas de la Fundación Universitaria Konrad Lorenz..."

Usuario: "Explícame el artículo 10"
Bot: "[Busca automáticamente el artículo 10 en los datos] 
     El artículo 10 establece que..."
```

---

## Notas Técnicas

1. **Normalización de acentos**: Se implementó normalización de acentos para manejar variaciones como "artículo" vs "articulo"

2. **Priorización de resultados**: Cuando se encuentran artículos mencionados:
   - Se priorizan documentos "original" sobre "secondary"
   - Se prefieren chunks más largos (más contenido)

3. **Compatibilidad**: Los cambios son backward-compatible. Si no se menciona un artículo específico, el sistema usa búsqueda semántica como antes.

4. **Memoria de sesión**: Las respuestas de preguntas generales también se guardan en la memoria de sesión para mantener el contexto de conversación.
