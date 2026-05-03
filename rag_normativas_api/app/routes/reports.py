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
        UserRole.DOCENTE
    ))
):
    base = db.query(QueryLog, User).join(User, QueryLog.user_id == User.id, isouter=True)

    if user.role in (UserRole.RECTOR.value, UserRole.ADMINISTRADOR.value):
            results = base.order_by(QueryLog.created_at.desc()).all()

    elif user.role == UserRole.DECANO.value:
            results = base.filter(QueryLog.faculty == user.faculty)\
                        .order_by(QueryLog.created_at.desc()).all()

    elif user.role in (UserRole.DIRECTOR.value, UserRole.DOCENTE.value):
            results = base.join(User, QueryLog.user_id == User.id, isouter=True)\
                        .filter(User.program == user.program)\
                        .order_by(QueryLog.created_at.desc()).all()
    else:
            results = []

    return [
            {
                "id":         row[0].id,
                "user_id":    row[0].user_id,
                "username":   row[1].username if row[1] else "—",
                "faculty":    row[1].faculty  if row[1] else "—",
                "program":    row[1].program  if row[1] else "—",
                "role":       row[1].role     if row[1] else "—",
                "question":   row[0].question,
                "answer":     row[0].answer,
                "agent_type": row[0].agent_type,
                "created_at": row[0].created_at.isoformat() if row[0].created_at else None,
            }
            for row in results
        ]


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
@router.get("/gastos")
def get_gastos(
        db: Session = Depends(get_db),
        user = Depends(require_roles(UserRole.RECTOR, UserRole.ADMINISTRADOR))
    ):
        queries = db.query(QueryLog, User)\
            .join(User, QueryLog.user_id == User.id, isouter=True)\
            .order_by(QueryLog.created_at.desc())\
            .all()
        
        total_input  = sum(row[0].input_tokens  or 0 for row in queries)
        total_output = sum(row[0].output_tokens or 0 for row in queries)
        total_cost   = sum(row[0].estimated_cost or 0 for row in queries)

        return {
            "resumen": {
                "total_consultas": len(queries),
                "total_input_tokens": total_input,
                "total_output_tokens": total_output,
                "total_tokens": total_input + total_output,
                "costo_total_usd": total_cost
            },
            "detalle": [
                {
                    "id":             row[0].id,
                    "username":       row[1].username if row[1] else "—",
                    "role":           row[1].role     if row[1] else "—", 
                    "faculty":        row[1].faculty  if row[1] else "—",
                    "question":       row[0].question,
                    "input_tokens":   row[0].input_tokens  or 0,
                    "output_tokens":  row[0].output_tokens or 0,
                    "total_tokens":   (row[0].input_tokens or 0) + (row[0].output_tokens or 0),
                    "estimated_cost": row[0].estimated_cost or 0,
                    "created_at":     row[0].created_at.isoformat() if row[0].created_at else None,  
                }
                for row in queries
            ]
        }
@router.get("/gastos/top_usuarios")
def get_top_usuarios(
    db: Session = Depends(get_db),
    user = Depends(require_roles(UserRole.RECTOR, UserRole.ADMINISTRADOR))
):
    from sqlalchemy import func as sqlfunc
    resultados = (
        db.query(
            User.username,
            User.faculty,
            User.role,
            sqlfunc.sum(QueryLog.input_tokens + QueryLog.output_tokens).label("total_tokens"),
            sqlfunc.sum(QueryLog.estimated_cost).label("total_costo"),
            sqlfunc.count(QueryLog.id).label("total_consultas")
        )
        .join(User, QueryLog.user_id == User.id)
        .filter(QueryLog.input_tokens > 0)
        .group_by(User.username, User.faculty, User.role)
        .order_by(sqlfunc.sum(QueryLog.estimated_cost).desc())
        .limit(5)
        .all()
    )
    return [
        {
            "username":        r.username,
            "faculty":         r.faculty or "—",
            "role":            r.role,
            "total_tokens":    int(r.total_tokens or 0),
            "total_costo":     float(r.total_costo or 0),
            "total_consultas": int(r.total_consultas or 0),
        }
        for r in resultados
    ]

@router.get("/gastos/por_facultad")
def get_por_facultad(
    db: Session = Depends(get_db),
    user = Depends(require_roles(UserRole.RECTOR, UserRole.ADMINISTRADOR))
):
    from sqlalchemy import func as sqlfunc
    resultados = (
        db.query(
            User.faculty,
            sqlfunc.sum(QueryLog.input_tokens + QueryLog.output_tokens).label("total_tokens"),
            sqlfunc.sum(QueryLog.estimated_cost).label("total_costo"),
            sqlfunc.count(QueryLog.id).label("total_consultas")
        )
        .join(User, QueryLog.user_id == User.id)
        .filter(QueryLog.input_tokens > 0)
        .group_by(User.faculty)
        .order_by(sqlfunc.sum(QueryLog.estimated_cost).desc())
        .all()
    )
    return [
        {
            "faculty":         r.faculty or "Sin facultad",
            "total_tokens":    int(r.total_tokens or 0),
            "total_costo":     float(r.total_costo or 0),
            "total_consultas": int(r.total_consultas or 0),
        }
        for r in resultados
    ]