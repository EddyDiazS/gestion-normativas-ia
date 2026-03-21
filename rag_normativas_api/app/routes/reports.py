from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.query_log import QueryLog
from app.core.roles import require_roles, UserRole
from app.models.activity_log import ActivityLog 
from app.models.user import User 

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
@router.get("/activity_logs")
def get_activity_logs(
    db: Session = Depends(get_db),
    user = Depends(require_roles(UserRole.RECTOR, UserRole.ADMINISTRADOR))
):
    logs = (
        db.query(ActivityLog, User)
        .join(User, ActivityLog.user_id == User.id, isouter=True)
        .order_by(ActivityLog.timestamp.desc())
        .all()
    )
    return [
        {
            "id":        row[0].id,
            "user_id":   row[0].user_id,
            "username":  row[1].username if row[1] else "—",
            "role":      row[1].role     if row[1] else "—",
            "action":    row[0].action,
            "timestamp": row[0].timestamp.isoformat() if row[0].timestamp else None,
        }
        for row in logs
    ]