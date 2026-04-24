from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional

# Mismo SECRET_KEY y ALGORITHM que rag_normativas_api/app/core/security.py
SECRET_KEY = "supersecretkey"
ALGORITHM  = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class TokenUser(BaseModel):
    username: str
    role:     str
    faculty:  Optional[str] = None
    program:  Optional[str] = None


def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenUser:
    """
    Decodifica el JWT generado por la app normativa.
    El token incluye: sub (username), role, faculty, program.
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación requerido. Inicia sesión en el sistema.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role     = payload.get("role")
        if not username or not role:
            raise HTTPException(status_code=401, detail="Token inválido: faltan campos requeridos")
        return TokenUser(
            username=username,
            role=role.upper(),
            faculty=payload.get("faculty"),
            program=payload.get("program"),
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado. Por favor inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )