from app.core.roles import UserRole
from typing import Optional


class AccessFilter:
    def __init__(self, sql_filter: str, blocked_tables: list, description: str):
        self.sql_filter     = sql_filter
        self.blocked_tables = blocked_tables
        self.description    = description


# Mapa de facultades → programas (ajustar según la universidad)
FACULTY_PROGRAMS = {
    "ingenieria":        ["Ingeniería de sistemas", "Ingeniería industrial", "Matemáticas"],
    "ciencias economicas": ["Administración de negocios internacionales", "Marketing"],
    "ciencias sociales": ["Psicología"],
}


def get_access_filter(role: str, faculty: Optional[str], program: Optional[str]) -> AccessFilter:
    role = role.upper()

    if role in (UserRole.RECTOR, UserRole.ADMINISTRADOR):
        return AccessFilter(
            sql_filter="",
            blocked_tables=[],
            description="Acceso total a todos los datos."
        )

    if role == UserRole.DECANO:
        if not faculty:
            return _no_access("Decano sin facultad asignada en su perfil")
        programs = FACULTY_PROGRAMS.get(faculty.lower().strip())
        if not programs:
            return _no_access(f"Facultad '{faculty}' no reconocida en el sistema")
        programs_sql = ", ".join(f"'{p}'" for p in programs)
        return AccessFilter(
            sql_filter=f"AND p.nombre_programa IN ({programs_sql})",
            blocked_tables=[],
            description=f"Acceso a facultad '{faculty}': {', '.join(programs)}."
        )

    if role == UserRole.DIRECTOR:
        if not program:
            return _no_access("Director sin programa asignado en su perfil")
        return AccessFilter(
            sql_filter=f"AND p.nombre_programa = '{program}'",
            blocked_tables=[],
            description=f"Acceso limitado al programa '{program}'."
        )

    if role == UserRole.DOCENTE:
        if not program:
            return _no_access("Docente sin programa asignado en su perfil")
        return AccessFilter(
            sql_filter=f"AND p.nombre_programa = '{program}'",
            blocked_tables=["informacion_financiera"],
            description=(
                f"Acceso al programa '{program}'. "
                "Sin acceso a datos financieros individuales de estudiantes."
            )
        )

    if role == UserRole.ESTUDIANTE:
        return AccessFilter(
            sql_filter="",
            blocked_tables=[],
            description="Solo puede consultar sus propios datos."
        )

    return _no_access(f"Rol '{role}' no reconocido")


def _no_access(reason: str) -> AccessFilter:
    return AccessFilter(
        sql_filter="AND 1=0",
        blocked_tables=[],
        description=f"Sin acceso: {reason}"
    )