from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from google.auth import default
from sqlalchemy.orm import Session
from app.schemas import user
from app.services.seed import run_seed
from app.database import engine, Base, get_db
from app.services.bootstrap import rag_engine
from app.routes import users, auth, reports
from app.rag_schemas import QuestionRequest, AnswerResponse
from app.models.user import User
from app.models.query_log import QueryLog
from app.models.activity_log import ActivityLog
from app.models.chat_message import ChatMessage
from app.core.roles import require_roles, UserRole
from app.agents.orchestrator import classify_question
from app.agents.academic_client import ask_academic_agent
from app.routes.admin_import import router as import_router

                

# Crear tablas
try:
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("✅ Tablas creadas correctamente")
except Exception as e:
    print(f"❌ Error en create_all: {e}")
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    existing_tables = [t.lower() for t in inspector.get_table_names()]
    print(f"📋 Tablas existentes: {existing_tables}")
    for table in Base.metadata.sorted_tables:
        if table.name.lower() not in existing_tables:
            try:
                table.create(bind=engine)
                print(f"✅ Tabla creada: {table.name}")
            except Exception as te:
                print(f"❌ No se pudo crear {table.name}: {te}")

        else:
            print(f"ℹ️  Ya existe: {table.name}")
run_seed()

from sqlalchemy import text, inspect as sa_inspect
try:
    with engine.connect() as conn:
        inspector = sa_inspect(engine)
        cols = [c["name"].lower() for c in inspector.get_columns("query_logs")]
        if "agent_type" not in cols:
            conn.execute(text("ALTER TABLE query_logs ADD agent_type VARCHAR2(20) DEFAULT 'RAG'"))
            conn.commit()
except Exception:
    pass
# Crear app
app = FastAPI(title="RAG Normativas API")
# Incluir routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(import_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # solo desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/chat/history")
def get_chat_history(session_id: str, db: Session = Depends(get_db), user=Depends(require_roles(
    UserRole.RECTOR,
    UserRole.DECANO,
    UserRole.DIRECTOR,
    UserRole.DOCENTE,
    UserRole.ESTUDIANTE,
    UserRole.ADMINISTRADOR
))):
    msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session_id, 
                                        ChatMessage.user_id == user.id).order_by(ChatMessage.created_at).all()
    return [{"role": m.role, "content": m.content, "agent_type": m.agent_type, "created_at":str (m.created_at)} for m in msgs]

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
            UserRole.ESTUDIANTE,
            UserRole.ADMINISTRADOR
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
    agent_type = classify_question(payload.question)
    print(f"🔍 user.role={user.role} | user.faculty={user.faculty} | user.program={user.program} | agent={agent_type}")


    if agent_type == "ACADEMIC":
        answer, input_tokens, output_tokens, estimated_cost = ask_academic_agent(
            question   = payload.question,
            role       = user.role,
            faculty    = user.faculty,
            program    = user.program,
            user_id    = user.cedula or user.username,
            session_id = payload.session_id,
        )
        verified = True
        sources  = []
    else:
        answer, verified, sources, input_tokens, output_tokens, estimated_cost = rag_engine.answer(
            payload.question, payload.top_k, payload.session_id
        )

    # Guardar consulta en base de datos
    log = QueryLog(
        user_id=user.id,
        faculty=user.faculty,
        question=payload.question[:1900],
        answer=answer[:7900],
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost=estimated_cost,
        agent_type="ACADEMIC" if agent_type == "ACADEMIC" else "RAG"
        )
    print(f"💾 Guardando → input={input_tokens} output={output_tokens} cost={estimated_cost} agent={agent_type}")

    db.add(log)
    db.commit()

    db.add(ChatMessage(session_id=payload.session_id or "default",
                       user_id=user.id, role="user", content=payload.question,
                       agent_type=agent_type))
    db.add(ChatMessage(session_id=payload.session_id or "default",
                       user_id=user.id, role="assistant", content=answer,
                       agent_type=agent_type))
    db.commit()
    db.refresh(log)

    return AnswerResponse(
        answer=answer,
        verified=verified,
        sources=sources
    )

@app.get("/chat/sessions")
def get_chat_sessions(
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        UserRole.RECTOR, UserRole.DECANO, UserRole.DIRECTOR,
        UserRole.DOCENTE, UserRole.ESTUDIANTE, UserRole.ADMINISTRADOR
    ))
):
    from sqlalchemy import func
    sessions = db.query(
        ChatMessage.session_id,
        func.min(ChatMessage.content).label("first_message"),
        func.min(ChatMessage.created_at).label("created_at")
    ).filter(
        ChatMessage.user_id == user.id,
        ChatMessage.role == "user"
    ).group_by(ChatMessage.session_id)\
     .order_by(func.min(ChatMessage.created_at).desc())\
     .all()
    
    return [{"session_id": s.session_id, 
             "title": s.first_message[:30] + "..." if len(s.first_message) > 30 else s.first_message,
             "created_at": str(s.created_at)} for s in sessions]