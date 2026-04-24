from enum import Enum

class UserRole(str, Enum):
    RECTOR        = "RECTOR"
    DECANO        = "DECANO"
    DIRECTOR      = "DIRECTOR"
    DOCENTE       = "DOCENTE"
    ESTUDIANTE    = "ESTUDIANTE"
    ADMINISTRADOR = "ADMINISTRADOR"