from google import genai
import os
import re
import time

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY no encontrada")

client = genai.Client(api_key=api_key)
GEMINI_MODEL = "gemini-2.5-flash"


def gemini_call(prompt: str, max_retries: int = 3) -> tuple:
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            usage = response.usage_metadata
            return (
                response.text.strip(),
                getattr(usage, "prompt_token_count", 0) or 0,
                getattr(usage, "candidates_token_count", 0) or 0
            )
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_match = re.search(r'retry.*?(\d+)', error_str, re.IGNORECASE)
                wait_seconds = int(wait_match.group(1)) + 2 if wait_match else 45
                print(f"⏳ Rate limit en response_agent. Esperando {wait_seconds}s...")
                time.sleep(wait_seconds)
                if attempt == max_retries - 1:
                    raise Exception(f"Límite de API alcanzado. Intenta en {wait_seconds}s")
            else:
                raise


RESPONSE_PROMPT = """Eres un asistente académico universitario preciso y confiable.

Pregunta del usuario:
"{question}"

SQL ejecutado (úsalo para saber qué significa cada columna en los datos):
{sql}

Datos retornados por la base de datos:
{data}

CONTEXTO PARA INTERPRETAR LOS DATOS:

Riesgo de deserción (columna RIESGO):
  '1. muy bajo' → riesgo muy bajo de abandonar
  '2. bajo'     → riesgo bajo
  '3. medio'    → riesgo medio
  '4. alto'     → riesgo alto
  '5. muy alto' → riesgo muy alto

PROBABILIDAD_DESERCION: decimal de 0.0 a 1.0 → multiplica x100 para porcentaje
  Ejemplo: 0.67 = "67% de probabilidad de deserción"

Calificaciones con valor -100: significa que el estudiante no presentó esa prueba.

CODIGO_GENERO: M = Masculino, F = Femenino

AUSENCIA_INTERSEMESTRAL: 1 = tuvo ausencia entre semestres, 0 = no tuvo

PROMEDIO_PERIODO: escala sobre 50 (no sobre 5.0)

REGLAS:
1. Responde SOLO con los datos proporcionados. No inventes cifras.
   IMPORTANTE: usa el SQL para identificar qué representa cada valor en los datos.
   Los alias del SELECT (AS promedio_edad, AS probabilidad_pct, etc.) te dicen el significado
   de cada columna en el orden en que aparecen en los datos.
2. Si los datos están vacíos indica claramente que no hay registros con esas características.
3. No menciones nombres de tablas, columnas técnicas ni código SQL.
   Usa lenguaje natural para un directivo o docente universitario.
4. Si hay diferencias entre grupos, explícalas claramente.
5. Si hay muchos registros (más de 10), resume los más relevantes.
6. Sé conciso pero completo. Responde en español.
"""

OUT_OF_SCOPE_RESPONSE = """Lo siento, esa pregunta está fuera del alcance de este sistema.

Soy un asistente académico universitario y solo puedo responder preguntas sobre:
- Estudiantes y programas académicos
- Rendimiento académico (calificaciones, promedios, pruebas)
- Información financiera (becas, mora, deuda, estrato)
- Ausencias e inasistencias
- Riesgo de deserción estudiantil"""


def get_access_denied_response(role: str, faculty: str = None, program: str = None) -> str:
    """Mensaje personalizado según el rol cuando intenta acceder a datos no permitidos."""

    role = role.upper()

    if role == "DECANO" and faculty:
        from app.core.filters import FACULTY_PROGRAMS
        programs = FACULTY_PROGRAMS.get(faculty.lower().strip(), [])
        programs_str = ", ".join(programs) if programs else "su facultad"
        return (
            f"No tienes acceso a esa información.\n\n"
            f"Como Decano de la facultad '{faculty}', solo puedes consultar datos de los programas: "
            f"**{programs_str}**.\n\n"
            f"La información que solicitaste pertenece a un programa fuera de tu facultad."
        )

    if role == "DIRECTOR" and program:
        return (
            f"No tienes acceso a esa información.\n\n"
            f"Como Director, solo puedes consultar datos del programa **{program}**.\n\n"
            f"La información que solicitaste pertenece a otro programa."
        )

    if role == "DOCENTE" and program:
        return (
            f"No tienes acceso a esa información.\n\n"
            f"Como Docente del programa **{program}**, solo puedes consultar datos académicos "
            f"de ese programa. No tienes acceso a datos financieros individuales de estudiantes."
        )

    if role == "ESTUDIANTE":
        return (
            "No tienes acceso a esa información.\n\n"
            "Como Estudiante, solo puedes consultar tus propios datos académicos."
        )

    return (
        "No tienes permiso para acceder a esa información.\n\n"
        f"Tu rol actual ({role}) no tiene acceso a los datos solicitados."
    )


def generate_response(question: str, data, sql: str = "") -> tuple:
    if data == "FUERA_DE_DOMINIO":
        return OUT_OF_SCOPE_RESPONSE, 0, 0

    data_str = "[] (sin registros)" if not data else str(data)
    prompt = RESPONSE_PROMPT.format(
        question=question,
        sql=sql or "No disponible",
        data=data_str
    )
    return gemini_call(prompt)