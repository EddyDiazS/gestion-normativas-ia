def normalize_question(question: str) -> str:
    NORMALIZATIONS = {
        "materia": "asignatura",
        "materias": "asignaturas",
        "pierdo": "repruebo",
        "perder": "reprobar",
        "perdí": "reprobé",
        "perderé": "reprobaré",
        "pierda": "repruebe",
        "carrera": "programa académico",
        "programa": "programa académico",
        "cupo": "cupo académico",
        "me sacan": "pérdida de cupo",
        "echar": "cancelar",
    }

    q = question.lower()

    for k, v in NORMALIZATIONS.items():
        q = q.replace(k, v)

    return q