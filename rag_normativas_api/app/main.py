from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.services.seed import run_seed

from app.database import engine, Base, get_db
from app.services.bootstrap import rag_engine

from app.routes import users, auth, reports

from app.rag_schemas import QuestionRequest, AnswerResponse

from app.models.user import User
from app.models.query_log import QueryLog
from app.models.activity_log import ActivityLog

from app.core.roles import require_roles, UserRole


# Crear tablas
Base.metadata.create_all(bind=engine)
run_seed()
# Crear app
app = FastAPI(title="RAG Normativas API")

# Incluir routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(reports.router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # solo desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint RAG
@app.post("/ask", response_model=AnswerResponse)
def ask(
    payload: QuestionRequest,
    db: Session = Depends(get_db),
    user=Depends(
        require_roles(
            UserRole.RECTOR,
            UserRole.DECANO,
            UserRole.DIRECTOR,
            UserRole.DOCENTE,
            UserRole.ESTUDIANTE
        )
    )
):

    # 🔹 Lógica según rol
    if user.role == "ESTUDIANTE":
        payload.top_k = 3

    elif user.role == "DOCENTE":
        payload.top_k = 5

    elif user.role == "DIRECTOR":
        payload.top_k = 6

    elif user.role == "DECANO":
        payload.top_k = 8

    elif user.role == "RECTOR":
        payload.top_k = 10

    # Ejecutar RAG
    answer, verified, sources = rag_engine.answer(
        payload.question,
        payload.top_k,
        payload.session_id
    )

    # Guardar consulta en base de datos
    log = QueryLog(
        user_id=user.id,
        faculty=user.faculty,
        question=payload.question,
        answer=answer
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return AnswerResponse(
        answer=answer,
        verified=verified,
        sources=sources
    )