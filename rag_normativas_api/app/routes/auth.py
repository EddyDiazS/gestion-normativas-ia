from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(User).filter(
    (User.username == form_data.username) |
    (User.cedula   == form_data.username)
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuario incorrecto")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    log = ActivityLog(
        user_id=user.id, 
        action = f"Inicio de sesión para el usuario: {user.username}, con Id: {user.id}, y Rol: {user.role}"
    )
    db.add(log)
    db.commit()

    token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role,
            "user_id": user.id
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role
    }