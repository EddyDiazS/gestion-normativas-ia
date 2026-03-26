from sqlalchemy.orm import Session
from app.models.user import User
from app.models.query_log import QueryLog
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_user(db: Session, user: UserCreate):
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
    return db_user


def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, user_data: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        return None

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
    if user_data.cedula is not None:
        db_user.cedula = user_data.cedula
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

    db.delete(user)
    db.commit()
    return user