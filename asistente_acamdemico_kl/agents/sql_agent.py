from google import genai
import os
import re
import time

# ==============================
# CONFIGURACIÓN GEMINI
# ==============================

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY no encontrada en variables de entorno")

client = genai.Client(api_key=api_key)
GEMINI_MODEL = "gemini-2.5-flash"


# ==============================
# CARGAR ESQUEMA BD
# ==============================

def get_database_schema():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(current_dir, '..', 'prompts', 'schema_prompt.txt')
    with open(schema_path, 'r', encoding='utf-8') as f:
        return f.read()

DB_SCHEMA = get_database_schema()


# ==============================
# COLUMNAS VÁLIDAS — FUENTE ÚNICA DE VERDAD
# ==============================

VALID_COLUMNS = {
    "programas": [
        "id_programa", "nombre_programa"
    ],
    "jornadas": [
        "id_jornada", "nombre_jornada"
    ],
    "estudiantes": [
        "Codigo_Estudiante", "EDAD", "FECHA_NACIMIENTO", "CODIGO_GENERO",
        "SEMESTRES_TRANSCURRIDOS", "SEMESTRE_ACTUAL", "PERIODO_INGRESO",
        "SIN_JORNADA", "id_programa", "id_jornada"
    ],
    "rendimiento_academico": [
        "id_rendimiento", "Codigo_Estudiante", "PROMEDIO_PERIODO", "PROMEDIO_40_DEF",
        "CALIFICACION_MATEMATICAS", "ENGLISH_SCORE", "TOTAL_COMP_LECTORA",
        "EXAMEN_ORAL", "CALIFICACION_40", "CONOCIMIENTO_PROCEDIMENTAL",
        "TOTAL_HABILIDADES_METACOGNITIVAS", "PERIODO"
    ],
    "informacion_financiera": [
        "id_financiera", "Codigo_Estudiante", "CODIGO_ESTRATO",
        "FINANCIACION_INTERNA", "FINANCIACION_INTERNA_SI", "PROMEDIO_DIAS_PAGO",
        "CANTIDAD_MORA", "PORCENTAJE_BECA", "CANTIDAD_CUOTAS",
        "DEUDA", "FINANCIAMIENTO", "PROMEDIO_ENTIDAD_FINANCIACION"
    ],
    "ausencias": [
        "id_ausencia", "Codigo_Estudiante",
        "AUSENCIA_INTERSEMESTRAL", "CANT_AUSENCIA_ANTERIOR"
    ],
    "riesgo_desercion": [
        "id_riesgo", "Codigo_Estudiante",
        "RIESGO", "PROBABILIDAD_DESERCION"
    ],
}

ALL_VALID_COLUMNS = {col.lower() for cols in VALID_COLUMNS.values() for col in cols}


# ==============================
# LLAMADA A GEMINI CON RETRY
# ==============================

def gemini_call(prompt: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_match = re.search(r'retry.*?(\d+)', error_str, re.IGNORECASE)
                wait_seconds = int(wait_match.group(1)) + 2 if wait_match else 45
                print(f"⏳ Rate limit. Esperando {wait_seconds}s (intento {attempt+1}/{max_retries})...")
                time.sleep(wait_seconds)
                if attempt == max_retries - 1:
                    raise Exception(f"Límite de API alcanzado. Intenta en {wait_seconds}s")
            else:
                raise


# ==============================
# LIMPIAR SQL
# ==============================

def clean_sql(sql: str) -> str:
    sql = sql.strip()
    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = sql.replace("```", "").strip()
    sql = sql.rstrip(";").strip()
    sql = re.sub(r'\n{3,}', '\n\n', sql)
    return sql


# ==============================
# VALIDAR SEGURIDAD
# ==============================

def validate_sql_security(sql: str) -> str:
    sql_lower = sql.lower()
    if not sql_lower.strip().startswith("select"):
        raise Exception("❌ Solo se permiten consultas SELECT")
    forbidden = ["delete", "update", "insert", "drop", "alter", "truncate", "create"]
    for word in forbidden:
        if re.search(rf"\b{word}\b", sql_lower):
            raise Exception(f"❌ Consulta no permitida: contiene '{word}'")
    return sql


# ==============================
# VERIFICAR COLUMNAS
# ==============================

def verify_sql_columns(sql: str) -> list:
    cleaned = re.sub(r"'[^']*'", "", sql)
    cleaned = re.sub(r"--.*", "", cleaned)
    tokens = re.findall(r'\b(?:\w+\.)?([\w_]+)\b', cleaned)

    sql_keywords = {
        "select", "from", "where", "join", "on", "and", "or", "not", "in",
        "as", "by", "group", "order", "having", "limit", "offset", "count",
        "avg", "sum", "min", "max", "distinct", "inner", "left", "right",
        "outer", "null", "is", "like", "between", "case", "when", "then",
        "else", "end", "asc", "desc", "int", "varchar", "decimal", "date",
        "true", "false", "union", "all", "exists", "coalesce", "round",
        # nombres de tablas
        "agente_academico", "programas", "jornadas", "estudiantes",
        "rendimiento_academico", "informacion_financiera", "ausencias", "riesgo_desercion",
        # alias de tablas
        "e", "p", "j", "ra", "f", "a", "rd",
        # alias de columnas calculadas comunes
        "total", "cantidad", "promedio", "resultado", "conteo", "nivel", "nombre",
        "promedio_riesgo", "probabilidad_promedio", "total_estudiantes",
        "promedio_matematicas", "promedio_edad", "con_beca", "total_con_beca",
        "promedio_mora", "promedio_ausencias", "promedio_ausencias_anteriores",
        "ausencias_previas", "total_riesgo", "nivel_riesgo", "riesgo_nivel",
        "total_masculino", "total_femenino", "promedio_deuda", "total_deuda",
        "promedio_dias", "promedio_habilidades", "promedio_procedimental",
        "total_sin_jornada", "promedio_probabilidad", "pct"
    }

    suspicious = []
    for token in tokens:
        token_lower = token.lower()
        if token_lower in sql_keywords:
            continue
        if token_lower.isdigit():
            continue
        if len(token) > 3 and token_lower not in ALL_VALID_COLUMNS:
            suspicious.append(token)

    return list(set(suspicious))


# ==============================
# PROMPT DE GENERACIÓN SQL
# ==============================

SQL_GENERATION_PROMPT = """Eres un experto en SQL MySQL para sistemas académicos universitarios.

Tu tarea tiene DOS pasos:

PASO 1 - VERIFICAR DOMINIO:
Determina si la pregunta está relacionada con el sistema académico universitario
(estudiantes, programas, rendimiento, finanzas, ausencias, riesgo de deserción).
Si NO está relacionada, responde ÚNICAMENTE con la palabra: FUERA_DE_DOMINIO

PASO 2 - GENERAR SQL (solo si está dentro del dominio):
Convierte la pregunta en una consulta SQL precisa usando SOLO las columnas del diccionario.

BASE DE DATOS: agente_academico

ESQUEMA:
{schema}

DICCIONARIO DE COLUMNAS (FUENTE ÚNICA DE VERDAD - NO USES OTRAS):

tabla: programas
  - id_programa       INT     → PK
  - nombre_programa   VARCHAR → nombre del programa académico

tabla: jornadas
  - id_jornada        INT     → PK
  - nombre_jornada    VARCHAR → Diurna o Nocturna

tabla: estudiantes
  - Codigo_Estudiante       INT     → PK identificador del estudiante
  - EDAD                    INT     → edad en años
  - FECHA_NACIMIENTO        DATE    → fecha de nacimiento
  - CODIGO_GENERO           VARCHAR → M=Masculino, F=Femenino
  - SEMESTRES_TRANSCURRIDOS INT     → semestres cursados hasta ahora
  - SEMESTRE_ACTUAL         INT     → semestre en que está matriculado
  - PERIODO_INGRESO         INT     → periodo en que ingresó (ej: 20231)
  - SIN_JORNADA             INT     → 1=sin jornada asignada, 0=tiene jornada
  - id_programa             INT     → FK a programas
  - id_jornada              INT     → FK a jornadas (NULL si SIN_JORNADA=1)

tabla: rendimiento_academico
  - Codigo_Estudiante               INT     → FK a estudiantes
  - PROMEDIO_PERIODO                DECIMAL → promedio de notas del periodo (escala sobre 50)
  - PROMEDIO_40_DEF                 INT     → indicador de promedio 40
  - CALIFICACION_MATEMATICAS        DECIMAL → nota matemáticas (-100 = no presentó)
  - ENGLISH_SCORE                   INT     → puntaje inglés (-100 = no presentó)
  - TOTAL_COMP_LECTORA              INT     → puntaje comprensión lectora
  - EXAMEN_ORAL                     INT     → nota examen oral (-100 = no presentó)
  - CALIFICACION_40                 INT     → calificación sobre 40
  - CONOCIMIENTO_PROCEDIMENTAL      DECIMAL → puntaje conocimiento procedimental
  - TOTAL_HABILIDADES_METACOGNITIVAS DECIMAL → puntaje habilidades metacognitivas
  - PERIODO                         INT     → periodo académico evaluado (ej: 20261)

tabla: informacion_financiera
  - Codigo_Estudiante            INT     → FK a estudiantes
  - CODIGO_ESTRATO               INT     → estrato socioeconómico (1 a 6)
  - FINANCIACION_INTERNA         VARCHAR → SI o NO tiene financiación interna
  - FINANCIACION_INTERNA_SI      INT     → 1=tiene financiación interna, 0=no tiene
  - PROMEDIO_DIAS_PAGO           DECIMAL → promedio días que tarda en pagar
  - CANTIDAD_MORA                INT     → veces que ha entrado en mora
  - PORCENTAJE_BECA              INT     → porcentaje de beca (0 a 100)
  - CANTIDAD_CUOTAS              INT     → cuotas de pago pactadas
  - DEUDA                        DECIMAL → monto de deuda en pesos
  - FINANCIAMIENTO               DECIMAL → porcentaje de financiamiento
  - PROMEDIO_ENTIDAD_FINANCIACION INT    → entidad de financiación (0 o 1)

tabla: ausencias
  - Codigo_Estudiante       INT → FK a estudiantes
  - AUSENCIA_INTERSEMESTRAL INT → 1=tuvo ausencia entre semestres, 0=no tuvo
  - CANT_AUSENCIA_ANTERIOR  INT → cantidad de ausencias en periodos anteriores

tabla: riesgo_desercion
  - Codigo_Estudiante      INT     → FK a estudiantes
  - RIESGO                 VARCHAR → nivel de riesgo en texto:
                                     '1. muy bajo', '2. bajo', '3. medio',
                                     '4. alto', '5. muy alto'
  - PROBABILIDAD_DESERCION DECIMAL → probabilidad 0.0 a 1.0 (ej: 0.67 = 67%)

REGLAS SQL OBLIGATORIAS:
1. USA SOLO columnas del diccionario. NUNCA inventes columnas.
2. SIEMPRE usa alias (e, p, j, ra, f, a, rd) y prefija TODAS las columnas con él.
3. JOIN solo si la pregunta requiere datos de más de una tabla.
4. Para filtrar por riesgo usa los valores EXACTOS del texto:
   WHERE rd.RIESGO = '1. muy bajo'
   WHERE rd.RIESGO = '2. bajo'
   WHERE rd.RIESGO = '3. medio'
   WHERE rd.RIESGO = '4. alto'
   WHERE rd.RIESGO = '5. muy alto'
   Para "alto riesgo" en general: WHERE rd.RIESGO IN ('4. alto', '5. muy alto')
5. Para PROBABILIDAD_DESERCION multiplicar por 100 para mostrar como porcentaje.
6. Para calificaciones con -100 (no presentó): SIEMPRE filtrar con != -100 cuando calcules
   AVG o cualquier agregación sobre estas columnas:
   CALIFICACION_MATEMATICAS, ENGLISH_SCORE, EXAMEN_ORAL
   Ejemplo correcto:   AVG(ra.CALIFICACION_MATEMATICAS) con WHERE ra.CALIFICACION_MATEMATICAS != -100
   Si hay JOIN con otras tablas usa AND: WHERE rd.RIESGO = '...' AND ra.CALIFICACION_MATEMATICAS != -100
   Si agrupas por nivel de riesgo y necesitas calificaciones, usa subconsulta o LEFT JOIN con filtro.
7. Incluye nombre_programa / nombre_jornada (no IDs) cuando aplique.
   IMPORTANTE — AMBIGÜEDAD CON MATEMÁTICAS:
   La BD tiene tanto una columna CALIFICACION_MATEMATICAS (prueba académica) como
   un programa académico llamado 'Matemáticas'. Distingue así:
   - "promedio de matemáticas" / "nota de matemáticas" / "calificación de matemáticas"
     → usar CALIFICACION_MATEMATICAS de rendimiento_academico (con filtro != -100)
   - "estudiantes de matemáticas" / "programa de matemáticas" / "carrera de matemáticas"
     → filtrar WHERE p.nombre_programa = 'Matemáticas'
   - "promedio de matemáticas de los estudiantes de matemáticas"
     → ambos: JOIN programas WHERE nombre_programa='Matemáticas' AND CALIFICACION_MATEMATICAS != -100
8. No expliques nada. No uses markdown. Devuelve SOLO SQL. Sin punto y coma al final.
   Si la pregunta está fuera del dominio devuelve SOLO: FUERA_DE_DOMINIO

EJEMPLOS:

P: "¿cuántos estudiantes hay por nivel de riesgo?"
SQL: SELECT rd.RIESGO AS nivel_riesgo, COUNT(*) AS cantidad FROM riesgo_desercion rd GROUP BY rd.RIESGO ORDER BY rd.RIESGO

P: "¿cuántos estudiantes tienen riesgo alto?"
SQL: SELECT COUNT(*) AS total FROM riesgo_desercion rd WHERE rd.RIESGO IN ('4. alto', '5. muy alto')

P: "¿cuál es la probabilidad de deserción promedio?"
SQL: SELECT ROUND(AVG(rd.PROBABILIDAD_DESERCION) * 100, 2) AS probabilidad_promedio_pct FROM riesgo_desercion rd

P: "¿cuál es el riesgo de deserción por programa?"
SQL: SELECT p.nombre_programa, rd.RIESGO, COUNT(*) AS total FROM riesgo_desercion rd JOIN estudiantes e ON rd.Codigo_Estudiante = e.Codigo_Estudiante JOIN programas p ON e.id_programa = p.id_programa GROUP BY p.nombre_programa, rd.RIESGO ORDER BY p.nombre_programa, rd.RIESGO

P: "¿cuál es el promedio de matemáticas?"
SQL: SELECT AVG(ra.CALIFICACION_MATEMATICAS) AS promedio_matematicas FROM rendimiento_academico ra WHERE ra.CALIFICACION_MATEMATICAS != -100

P: "¿cuál es el promedio de matemáticas por nivel de riesgo?"
SQL: SELECT rd.RIESGO, AVG(ra.CALIFICACION_MATEMATICAS) AS promedio_matematicas FROM riesgo_desercion rd JOIN rendimiento_academico ra ON rd.Codigo_Estudiante = ra.Codigo_Estudiante WHERE ra.CALIFICACION_MATEMATICAS != -100 GROUP BY rd.RIESGO ORDER BY rd.RIESGO

P: "¿cuál es el promedio de matemáticas, deuda y probabilidad de deserción por nivel de riesgo?"
SQL: SELECT rd.RIESGO, AVG(ra.CALIFICACION_MATEMATICAS) AS promedio_matematicas, AVG(f.DEUDA) AS promedio_deuda, ROUND(AVG(rd.PROBABILIDAD_DESERCION)*100,2) AS probabilidad_pct FROM riesgo_desercion rd JOIN rendimiento_academico ra ON rd.Codigo_Estudiante = ra.Codigo_Estudiante JOIN informacion_financiera f ON rd.Codigo_Estudiante = f.Codigo_Estudiante WHERE ra.CALIFICACION_MATEMATICAS != -100 GROUP BY rd.RIESGO ORDER BY rd.RIESGO

P: "¿cuántos estudiantes hay por programa?"
SQL: SELECT p.nombre_programa, COUNT(*) AS total FROM estudiantes e JOIN programas p ON e.id_programa = p.id_programa GROUP BY p.nombre_programa ORDER BY total DESC

P: "¿cuántos estudiantes hay por género?"
SQL: SELECT e.CODIGO_GENERO, COUNT(*) AS total FROM estudiantes e GROUP BY e.CODIGO_GENERO

P: "¿cuántos estudiantes tienen beca?"
SQL: SELECT COUNT(*) AS con_beca FROM informacion_financiera f WHERE f.PORCENTAJE_BECA > 0

P: "¿los estudiantes con ausencia intersemestral tienen más riesgo?"
SQL: SELECT a.AUSENCIA_INTERSEMESTRAL, rd.RIESGO, COUNT(*) AS total FROM riesgo_desercion rd JOIN ausencias a ON a.Codigo_Estudiante = rd.Codigo_Estudiante GROUP BY a.AUSENCIA_INTERSEMESTRAL, rd.RIESGO ORDER BY a.AUSENCIA_INTERSEMESTRAL, rd.RIESGO

P: "¿cuántas ausencias anteriores tienen en promedio los estudiantes de alto riesgo?"
SQL: SELECT AVG(a.CANT_AUSENCIA_ANTERIOR) AS promedio_ausencias FROM ausencias a JOIN riesgo_desercion rd ON rd.Codigo_Estudiante = a.Codigo_Estudiante WHERE rd.RIESGO IN ('4. alto', '5. muy alto')

P: "¿cuál es el promedio de deuda por programa?"
SQL: SELECT p.nombre_programa, AVG(f.DEUDA) AS promedio_deuda FROM informacion_financiera f JOIN estudiantes e ON f.Codigo_Estudiante = e.Codigo_Estudiante JOIN programas p ON e.id_programa = p.id_programa GROUP BY p.nombre_programa ORDER BY promedio_deuda DESC

P: "¿cuál es el clima hoy?"
SQL: FUERA_DE_DOMINIO
9. INTERPRETACIÓN DE "FACULTAD" (IMPORTANTE):

En esta base de datos NO existe una tabla de facultades.
El término "facultad" debe interpretarse como una agrupación de programas académicos (tabla programas).

Reglas:

- "facultad" = programas
- "por facultad" = agrupar por p.nombre_programa
- "facultad de X" = filtrar programas relacionados con X usando LIKE

Mapeo:

- "facultad de psicología"
  → p.nombre_programa LIKE '%psicolog%'

- "facultad de matemáticas e ingenierías"
  → p.nombre_programa LIKE '%ingenier%' OR p.nombre_programa LIKE '%matematic%'

- "facultad de negocios"
  → p.nombre_programa LIKE '%admin%' OR p.nombre_programa LIKE '%negocio%'

También considerar sinónimos:
"facultad", "escuela", "área académica" → SIEMPRE mapear a programas

Ejemplos:

P: "¿cuántos estudiantes hay por facultad?"
SQL: SELECT p.nombre_programa, COUNT(*) AS total FROM estudiantes e JOIN programas p ON e.id_programa = p.id_programa GROUP BY p.nombre_programa ORDER BY total DESC

P: "¿cuántos estudiantes hay en la facultad de psicología?"
SQL: SELECT COUNT(*) AS total FROM estudiantes e JOIN programas p ON e.id_programa = p.id_programa WHERE p.nombre_programa LIKE '%psicolog%'

P: "¿cuántos estudiantes hay en la facultad de matemáticas e ingenierías?"
SQL: SELECT COUNT(*) AS total FROM estudiantes e JOIN programas p ON e.id_programa = p.id_programa WHERE p.nombre_programa LIKE '%ingenier%' OR p.nombre_programa LIKE '%matematic%'
{role_context}
PREGUNTA: {question}
"""


# ==============================
# GENERAR SQL
# ==============================

def generate_sql(question: str, access_filter=None, history_context: str = "") -> str:
    """
    access_filter: instancia de AccessFilter con sql_filter, blocked_tables y description.
    Si se pasa, se inyecta en el prompt para restringir el SQL generado.
    """

    # Verificar acceso antes de llamar al LLM
    if access_filter and access_filter.sql_filter == "AND 1=0":
        raise Exception("FUERA_DE_DOMINIO")

    # Detectar si la pregunta involucra tablas bloqueadas para este rol
    if access_filter and access_filter.blocked_tables:
        TABLA_KEYWORDS = {
            "informacion_financiera": [
                "beca", "becas", "deuda", "mora", "cuota", "cuotas", "financ",
                "pago", "pagos", "estrato", "estratos", "dinero", "cobro", "cobros"
            ]
        }
        question_lower = question.lower()
        for tabla in access_filter.blocked_tables:
            keywords = TABLA_KEYWORDS.get(tabla, [])
            if any(kw in question_lower for kw in keywords):
                raise Exception(f"ACCESO_DENEGADO_TABLA:{tabla}")

    # Detectar si ESTUDIANTE pregunta por datos grupales o de otros estudiantes
    from app.core.roles import UserRole
    if access_filter and hasattr(access_filter, '_role') and False:
        pass  # placeholder
    # Detectar rol estudiante por el filtro inyectado con codigo_estudiante
    if (access_filter and "codigo_estudiante" in question.lower() is False
        and access_filter.sql_filter == ""
        and "ESTUDIANTE" in (access_filter.description or "").upper()):
        pass  # se maneja en main.py

    # Construir contexto de rol
    role_context = ""
    if access_filter and access_filter.sql_filter:
        role_context = (
            f"RESTRICCIÓN DE ACCESO (obligatoria, no negociable):\n"
            f"{access_filter.description}\n"
            f"Agrega SIEMPRE este filtro en el WHERE: {access_filter.sql_filter}"
        )

    # Combinar historial + restricciones de rol
    full_context = ""
    if history_context:
        full_context += history_context + "\n\n"
    if role_context:
        full_context += role_context

    prompt = SQL_GENERATION_PROMPT.format(
        schema=DB_SCHEMA,
        question=question,
        role_context=full_context
    )
    raw = gemini_call(prompt)

    if "FUERA_DE_DOMINIO" in raw.upper():
        raise Exception("FUERA_DE_DOMINIO")

    sql = clean_sql(raw)
    sql = validate_sql_security(sql)

    suspicious = verify_sql_columns(sql)
    if suspicious:
        print(f"⚠️  Columnas sospechosas: {suspicious} — reintentando...")
        retry_prompt = prompt + f"""

CORRECCIÓN REQUERIDA: La consulta contiene estas columnas que NO EXISTEN en la BD: {suspicious}
Revisa el DICCIONARIO y regenera usando ÚNICAMENTE columnas listadas.
{role_context}
PREGUNTA: {question}
"""
        raw = gemini_call(retry_prompt)
        sql = clean_sql(raw)
        sql = validate_sql_security(sql)

    return sql