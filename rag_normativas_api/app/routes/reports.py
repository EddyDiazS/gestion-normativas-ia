from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.query_log import QueryLog
from app.core.roles import require_roles, UserRole

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/all_queries")
def get_all_queries(
    db: Session = Depends(get_db),
    user = Depends(require_roles(UserRole.RECTOR, UserRole.ADMINISTRADOR))
):
    queries = db.query(QueryLog).all()
    return queries


@router.get("/faculty_queries")
def get_faculty_queries(
    db: Session = Depends(get_db),
    user = Depends(require_roles(
        UserRole.RECTOR,
        UserRole.ADMINISTRADOR,
        UserRole.DECANO,
        UserRole.DIRECTOR,
    ))
):
    if user.role in (UserRole.RECTOR.value, UserRole.ADMINISTRADOR.value):
        queries = db.query(QueryLog).all()
    else:
        queries = db.query(QueryLog).filter(
            QueryLog.faculty == user.faculty
        ).all()

    return queries