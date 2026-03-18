from enum import Enum
from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user

class UserRole(str, Enum):
    RECTOR = "RECTOR"
    DECANO = "DECANO"
    DIRECTOR = "DIRECTOR"
    DOCENTE = "DOCENTE"
    ESTUDIANTE = "ESTUDIANTE"
    ADMINISTRADOR = "ADMINISTRADOR"

def require_roles(*roles):

    def role_checker(user=Depends(get_current_user)):

        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para este recurso"
            )

        return user

    return role_checker