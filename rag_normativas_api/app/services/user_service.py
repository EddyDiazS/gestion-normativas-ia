from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.user import User
from app.models.query_log import QueryLog
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PROGRAMA_MAP_INVERSO = {
    "Administración de negocios internacionales": 1,
    "Ingeniería de Sistemas": 2,
    "Ingeniería Industrial": 3,
    "Marketing": 4,
    "Matemáticas": 5,
    "Psicología": 6,
}

def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_user(db: Session, user: UserCreate):
    if user.cedula:
        existe_cedula = db.query(User).filter(User.cedula == user.cedula).first()
        if existe_cedula:
            raise HTTPException(status_code=400, detail="Ya existe un usuario con esa cédula o código")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        faculty=user.faculty,
        program=user.program,
        cedula=user.cedula
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    if user.role == "ESTUDIANTE":
        try:
            codigo = int(user.cedula)
            existe = db.execute(
                text("SELECT COUNT(*) FROM estudiantes WHERE Codigo_Estudiante = :c"),
                {"c": codigo}
            ).scalar()
            if not existe:
                id_programa = PROGRAMA_MAP_INVERSO.get(user.program) if user.program else None
                db.execute(text("""
                    INSERT INTO estudiantes 
                    (Codigo_Estudiante, EDAD, FECHA_NACIMIENTO, CODIGO_GENERO,
                     SEMESTRES_TRANSCURRIDOS, SEMESTRE_ACTUAL, PERIODO_INGRESO,
                     SIN_JORNADA, ID_PROGRAMA, ID_JORNADA)
                    VALUES (:cod, NULL, NULL, NULL, NULL, NULL, NULL, 0, :id_prog, 1)
                """), {"cod": codigo, "id_prog": id_programa})
                db.commit()
        except (ValueError, TypeError):
            pass

    return db_user


def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, user_data: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        return None

    if user_data.cedula is not None:
        existe_cedula = db.query(User).filter(
            User.cedula == user_data.cedula,
            User.id != user_id
        ).first()
        if existe_cedula:
            raise HTTPException(status_code=400, detail="Ya existe un usuario con esa cédula o código")
        db_user.cedula = user_data.cedula

    if user_data.username is not None:
        db_user.username = user_data.username
    if user_data.email is not None:
        db_user.email = user_data.email
    if user_data.password is not None:
        db_user.hashed_password = get_password_hash(user_data.password)
    if user_data.faculty is not None:
        db_user.faculty = user_data.faculty
    if user_data.program is not None:
        db_user.program = user_data.program
    if user_data.is_active is not None:
        db_user.is_active = user_data.is_active

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return None

    db.query(QueryLog).filter(QueryLog.user_id == user_id).delete()

    try:
        from app.models.activity_log import ActivityLog
        db.query(ActivityLog).filter(ActivityLog.user_id == user_id).delete()
    except Exception:
        pass

    if user.role == "ESTUDIANTE":
        try:
            codigo = int(user.cedula)
            db.execute(text("DELETE FROM riesgo_desercion WHERE Codigo_Estudiante = :c"), {"c": codigo})
            db.execute(text("DELETE FROM ausencias WHERE Codigo_Estudiante = :c"), {"c": codigo})
            db.execute(text("DELETE FROM informacion_financiera WHERE Codigo_Estudiante = :c"), {"c": codigo})
            db.execute(text("DELETE FROM rendimiento_academico WHERE Codigo_Estudiante = :c"), {"c": codigo})
            db.execute(text("DELETE FROM estudiantes WHERE Codigo_Estudiante = :c"), {"c": codigo})
        except Exception as e:
            print(f"⚠️ Error borrando tablas académicas: {e}")

    db.delete(user)
    db.commit()
    return user