from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import create_user, get_users, delete_user, update_user
from app.core.roles import require_roles, UserRole

router = APIRouter(prefix="/users", tags=["Users"])


# Crear usuario
@router.post("/", response_model=UserResponse)
def create_new_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(UserRole.ADMINISTRADOR, UserRole.RECTOR))
):
    return create_user(db, user)


# Ver todos los usuarios
@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(UserRole.ADMINISTRADOR, UserRole.RECTOR, UserRole.DOCENTE))
):
    return get_users(db)


# Actualizar usuario
@router.put("/{user_id}")
def update_existing_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(UserRole.ADMINISTRADOR, UserRole.RECTOR))
):
    updated_user = update_user(db, user_id, user)

    if not updated_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return updated_user


# Eliminar usuario
@router.delete("/{user_id}")
def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(UserRole.ADMINISTRADOR, UserRole.RECTOR))
):
    user = delete_user(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {"message": "User deleted successfully"}