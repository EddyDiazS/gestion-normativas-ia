from app.rag.loader import load_documents
from app.rag.chunker import divide_by_articles
from app.rag.index import build_faiss_index
from app.rag.generator import RAGEngine
from app.config import DATA_PATH
from sqlalchemy import text
from app.database import engine

#tablas académicas
tablas_academicas = [
    """
    CREATE TABLE programas (
        ID_PROGRAMA NUMBER PRIMARY KEY,
        NOMBRE_PROGRAMA VARCHAR2(255) NOT NULL
    )
    """,
    """
    CREATE TABLE jornadas (
        ID_JORNADA NUMBER PRIMARY KEY,
        NOMBRE_JORNADA VARCHAR2(100) NOT NULL
    )
    """,
    """
    CREATE TABLE estudiantes (
        CODIGO_ESTUDIANTE NUMBER PRIMARY KEY,
        EDAD NUMBER,
        FECHA_NACIMIENTO DATE,
        CODIGO_GENERO VARCHAR2(1),
        SEMESTRES_TRANSCURRIDOS NUMBER,
        SEMESTRE_ACTUAL NUMBER,
        PERIODO_INGRESO NUMBER,
        SIN_JORNADA NUMBER DEFAULT 0,
        ID_PROGRAMA NUMBER,
        ID_JORNADA NUMBER
    )
    """,
    """
    CREATE TABLE rendimiento_academico (
        ID_RENDIMIENTO NUMBER PRIMARY KEY,
        CODIGO_ESTUDIANTE NUMBER NOT NULL,
        PROMEDIO_PERIODO NUMBER(6,2),
        PROMEDIO_40_DEF NUMBER,
        CALIFICACION_MATEMATICAS NUMBER(6,2),
        ENGLISH_SCORE NUMBER,
        TOTAL_COMP_LECTORA NUMBER,
        EXAMEN_ORAL NUMBER,
        CALIFICACION_40 NUMBER,
        CONOCIMIENTO_PROCEDIMENTAL NUMBER(10,5),
        TOTAL_HABILIDADES_METACOGNITIVAS NUMBER(10,5),
        PERIODO NUMBER
    )
    """,
    """
    CREATE TABLE informacion_financiera (
        ID_FINANCIERA NUMBER PRIMARY KEY,
        CODIGO_ESTUDIANTE NUMBER NOT NULL,
        CODIGO_ESTRATO NUMBER,
        FINANCIACION_INTERNA VARCHAR2(10),
        FINANCIACION_INTERNA_SI NUMBER,
        PROMEDIO_DIAS_PAGO NUMBER(10,2),
        CANTIDAD_MORA NUMBER,
        PORCENTAJE_BECA NUMBER,
        CANTIDAD_CUOTAS NUMBER,
        DEUDA NUMBER(15,2),
        FINANCIAMIENTO NUMBER(15,2),
        PROMEDIO_ENTIDAD_FINANCIACION NUMBER
    )
    """,
    """
    CREATE TABLE ausencias (
        ID_AUSENCIA NUMBER PRIMARY KEY,
        CODIGO_ESTUDIANTE NUMBER NOT NULL,
        AUSENCIA_INTERSEMESTRAL NUMBER,
        CANT_AUSENCIA_ANTERIOR NUMBER
    )
    """,
    """
    CREATE TABLE riesgo_desercion (
        ID_RIESGO NUMBER PRIMARY KEY,
        CODIGO_ESTUDIANTE NUMBER NOT NULL,
        RIESGO VARCHAR2(50),
        PROBABILIDAD_DESERCION NUMBER(10,4)
    )
    """,
]

for tabla_sql in tablas_academicas:
    try:
        with engine.connect() as connection:
            connection.execute(text(tabla_sql))
            connection.commit()
    except Exception:
        pass

# Datos iniciales de programas y jornadas
datos_iniciales = [
    "INSERT INTO programas VALUES (1, 'Administración de negocios internacionales')",
    "INSERT INTO programas VALUES (2, 'Ingeniería de Sistemas')",
    "INSERT INTO programas VALUES (3, 'Ingeniería Industrial')",
    "INSERT INTO programas VALUES (4, 'Marketing')",
    "INSERT INTO programas VALUES (5, 'Matemáticas')",
    "INSERT INTO programas VALUES (6, 'Psicología')",
    "INSERT INTO jornadas VALUES (1, 'Diurna')",
    "INSERT INTO jornadas VALUES (2, 'Nocturna')",
]

for sql in datos_iniciales:
    try:
        with engine.connect() as connection:
            connection.execute(text(sql))
            connection.commit()
    except Exception:
        pass

# ALTER TABLE sobre tablas de usuarios y query_logs para agregar columnas necesarias para el RAG
try:
    with engine.connect() as connection:
        connection.execute(text("ALTER TABLE users ADD cedula VARCHAR2(20) NULL"))
        connection.commit()
except Exception:
    pass

for column_sql in [
    "ALTER TABLE query_logs ADD input_tokens NUMBER(10) DEFAULT 0",
    "ALTER TABLE query_logs ADD output_tokens NUMBER(10) DEFAULT 0",
    "ALTER TABLE query_logs ADD estimated_cost NUMBER(10,6) DEFAULT 0",
    "ALTER TABLE query_logs MODIFY answer VARCHAR2(8000)",
    "ALTER TABLE chat_messages MODIFY content VARCHAR2(8000)",
]:
    try:
        with engine.connect() as connection:
            connection.execute(text(column_sql))
            connection.commit()
    except Exception:
        pass

# Crear secuencias
sequences = ["seq_rendimiento", "seq_ausencias", "seq_financiera", "seq_riesgo"]
for seq in sequences:
    try:
        with engine.connect() as connection:
            connection.execute(text(f"CREATE SEQUENCE {seq} START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE"))
            connection.commit()
    except Exception:
        pass

# Cargar RAG
documents = load_documents(DATA_PATH)
chunks = divide_by_articles(documents)
index, chunks = build_faiss_index(chunks)

rag_engine = RAGEngine(index, chunks)