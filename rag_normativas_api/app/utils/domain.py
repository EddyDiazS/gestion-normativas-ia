import re

# Situaciones académicas reguladas (lenguaje natural)
SITUATIONAL_PATTERNS = [
    r"reprueb",
    r"pierdo el cupo",
    r"perder el cupo",
    r"cancelaci[oó]n de (materia|asignatura|semestre)",
    r"repetir (materia|asignatura)",
    r"n[uú]mero de veces",
    r"tercera vez",
    r"segunda vez",
    r"matr[ií]cula",
    r"evaluaci[oó]n",
    r"promedio",
    r"requisitos",
    r"sanci[oó]n acad[eé]mica",
    r"consecuencia acad[eé]mica",
    r"programa profesional",
    r"programa acad[eé]mico",
]

# Términos institucionales
INSTITUTIONAL_TERMS = [
    "konrad",
    "fundación universitaria",
    "reglamento",
    "normativa",
    "estatuto académico"
]


def is_academic_normative_question(question: str) -> bool:
    q = question.lower()

    # 1️⃣ Detecta situación académica
    situational = any(re.search(p, q) for p in SITUATIONAL_PATTERNS)

    # 2️⃣ Detecta contexto institucional (opcional)
    institutional = any(term in q for term in INSTITUTIONAL_TERMS)

    # ✅ Aceptar si describe una situación académica,
    # aunque no diga explícitamente "artículo"
    return situational or institutional