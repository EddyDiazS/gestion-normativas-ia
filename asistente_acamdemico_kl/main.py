from fastapi import FastAPI, HTTPException

import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_ENV = os.getenv("APP_ENV", "local")

if APP_ENV == "production":
    load_dotenv(os.path.join(BASE_DIR, ".env.prod"), override=True)
else:
    load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

from pydantic import BaseModel
from typing import Optional
from agents.sql_agent import generate_sql
from agents.response_agent import generate_response, OUT_OF_SCOPE_RESPONSE
from database.execute_query import run_query
from app.core.filters import get_access_filter, AccessFilter
from app.core.roles import UserRole
import uuid

app = FastAPI(title="Agente Académico", version="3.1")


# ==============================
# MEMORIA DE CONVERSACIÓN
# Diccionario en memoria: session_id → lista de turnos
# Máximo 8 turnos por sesión para no inflar el prompt
# ==============================

MAX_TURNS = 8
sessions: dict = {}


def get_history(session_id: str) -> list:
    return sessions.get(session_id, [])


def save_turn(session_id: str, question: str, sql: str, data, answer: str):
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append({
        "pregunta":  question,
        "sql":       sql,
        "respuesta": answer[:400],          # truncar respuesta larga
        "datos":     str(data)[:300]        # truncar datos largos
    })
    # Mantener solo los últimos MAX_TURNS turnos
    sessions[session_id] = sessions[session_id][-MAX_TURNS:]


def build_history_context(history: list) -> str:
    """Construye el bloque de historial para inyectar en el prompt del SQL agent."""
    if not history:
        return ""
    lines = ["HISTORIAL DE LA CONVERSACIÓN (turnos anteriores — úsalo para entender referencias como 'ellos', 'ese grupo', 'los mismos', 'cuántos son'):"]
    for i, turn in enumerate(history, 1):
        lines.append(f"\nTurno {i}:")
        lines.append(f"  Pregunta: {turn['pregunta']}")
        lines.append(f"  SQL ejecutado: {turn['sql']}")
        lines.append(f"  Respuesta dada: {turn['respuesta']}")
    lines.append("\nSi la nueva pregunta hace referencia a resultados anteriores, usa el SQL del turno previo como base.")
    return "\n".join(lines)


# ==============================
# MODELO DE REQUEST
# ==============================

class Question(BaseModel):
    question:   str
    role:       Optional[str] = "RECTOR"
    faculty:    Optional[str] = None
    program:    Optional[str] = None
    user_id:    Optional[str] = None
    session_id: Optional[str] = None   # si no viene, se genera uno nuevo


# ==============================
# ENDPOINT PRINCIPAL /ask
# ==============================

@app.post("/ask")
def ask_agent(request: Question):
    print(f"🚨 AGENTE RECIBIÓ: role={request.role} | program={request.program} | question={request.question[:50]}")
    question   = request.question
    role       = (request.role or "RECTOR").upper()
    faculty    = request.faculty
    program    = request.program
    user_id    = request.user_id or "anonimo"

    # Gestión de sesión
    session_id = request.session_id or str(uuid.uuid4())
    history    = get_history(session_id)
    history_context = build_history_context(history)

    print(f"\n👤 {user_id} | {role} | sesión: {session_id} | turno: {len(history)+1}")
    print(f"❓ {question}")

    # Filtro de acceso según rol
    access_filter = get_access_filter(role, faculty, program)
    print(f"🔒 {access_filter.description}")

    # Estudiante solo ve sus propios datos
    question_for_sql = question
    if role == UserRole.ESTUDIANTE and user_id != "anonimo":
        forced_filter = f"AND e.Codigo_Estudiante = {user_id}"
        access_filter.sql_filter = forced_filter
        access_filter.description = f"Acceso solo al estudiante con código {user_id}"
        question_for_sql = question 

    try:
        sql , sql_inp, sql_out= generate_sql(
            question_for_sql,
            access_filter=access_filter,
            history_context=history_context
        )
        print(f"🔍 SQL:\n{sql}\n")

    except Exception as e:
        error_msg = str(e)

        if "FUERA_DE_DOMINIO" in error_msg:
            return {
                "question":   request.question,
                "session_id": session_id,
                "sql":        None,
                "data":       None,
                "answer":     OUT_OF_SCOPE_RESPONSE,
                "role":       role
            }

        if "ACCESO_DENEGADO_TABLA" in error_msg:
            from agents.response_agent import get_access_denied_response
            return {
                "question":   request.question,
                "session_id": session_id,
                "sql":        None,
                "data":       None,
                "answer":     get_access_denied_response(role, faculty, program),
                "role":       role
            }

        print(f"❌ Error SQL: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Error al generar consulta: {error_msg}")

    try:
        data = run_query(sql)
        print(f"📊 Filas: {len(data) if data else 0}")
    except Exception as e:
        print(f"❌ Error BD: {e}")
        raise HTTPException(status_code=500, detail=f"Error ejecutando consulta: {str(e)}")

    # Acceso denegado por filtro de rol (resultado vacío)
    if role != UserRole.ESTUDIANTE and access_filter.sql_filter and access_filter.sql_filter != "":
        resultado_vacio = (
            not data or
            (len(data) == 1 and len(data[0]) == 1 and data[0][0] == 0)
        )
        if resultado_vacio:
            from agents.response_agent import get_access_denied_response
            return {
                "question":   request.question,
                "session_id": session_id,
                "sql":        sql,
                "data":       [],
                "answer":     get_access_denied_response(role, faculty, program),
                "role":       role
            }

    # Estudiante intentando ver datos de otro estudiante
    if role == UserRole.ESTUDIANTE:
        resultado_vacio = (
            not data or
            (len(data) == 1 and len(data[0]) == 1 and data[0][0] == 0)
        )
        if resultado_vacio:
            from agents.response_agent import get_access_denied_response
            return {
                "question":   request.question,
                "session_id": session_id,
                "sql":        sql,
                "data":       [],
                "answer":     get_access_denied_response(role, faculty, program),
                "role":       role
            }

    try:
        answer, res_inp, res_out = generate_response(request.question, data, sql=sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando respuesta: {str(e)}")
    
    total_input = sql_inp + res_inp
    total_output = sql_out + res_out
    cost = round((total_input * 0.075 + total_output * 0.30) / 1_000_000, 6)

    # Guardar turno en el historial de la sesión
    save_turn(session_id, request.question, sql, data, answer)

    print(f"✅ AGENTE ACADÉMICO → role={role} | program={program} | filas={len(data) if data else 0} | respuesta={answer[:80]}")
    return {
        "question":   request.question,
        "session_id": session_id,
        "sql":        sql,
        "data":       data,
        "answer":     answer,
        "role":       role,
        "turn":       len(get_history(session_id)),
        "tokens_input": total_input,
        "tokens_output": total_output,
        "estimated_cost": cost
    }


# ==============================
# GESTIÓN DE SESIONES
# ==============================

@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    """Limpia el historial de una sesión."""
    if session_id in sessions:
        sessions.pop(session_id)
    return {"message": "Sesión limpiada", "session_id": session_id}


@app.get("/session/{session_id}")
def get_session(session_id: str):
    """Retorna el historial de una sesión."""
    history = get_history(session_id)
    return {
        "session_id": session_id,
        "turns":      len(history),
        "history":    history
    }


# ==============================
# ENDPOINT /stats
# ==============================

@app.get("/stats")
def get_stats(
    role:    str = "RECTOR",
    faculty: Optional[str] = None,
    program: Optional[str] = None,
    user_id: Optional[str] = None,
):
    role = role.upper()
    access_filter = get_access_filter(role, faculty, program)
    f = access_filter.sql_filter
    

    join_prog        = "JOIN estudiantes e ON rd.Codigo_Estudiante = e.Codigo_Estudiante JOIN programas p ON e.id_programa = p.id_programa"
    join_prog_simple = "JOIN programas p ON e.id_programa = p.id_programa"
    where   = f"WHERE 1=1 {f}" if f else ""
    where_e = f"WHERE 1=1 {f}" if f else ""

    try:
        r = run_query(f"SELECT COUNT(DISTINCT e.Codigo_Estudiante) FROM estudiantes e {join_prog_simple} {where_e}")
        total_estudiantes = r[0][0] if r else 0

        r = run_query(f"SELECT rd.RIESGO, COUNT(*) FROM riesgo_desercion rd {join_prog} {where} GROUP BY rd.RIESGO ORDER BY rd.RIESGO")
        distribucion_riesgo = {row[0]: row[1] for row in r} if r else {}

        r = run_query(f"SELECT ROUND(AVG(rd.PROBABILIDAD_DESERCION)*100,2) FROM riesgo_desercion rd {join_prog} {where}")
        prob_promedio = float(r[0][0]) if r and r[0][0] else 0.0

        programa_top = None
        if role in ("RECTOR", "ADMINISTRADOR", "DECANO"):
            r = run_query(f"SELECT p.nombre_programa, COUNT(*) AS total FROM estudiantes e {join_prog_simple} {where_e} GROUP BY p.nombre_programa ORDER BY total DESC LIMIT 1")
            if r:
                programa_top = {"programa": r[0][0], "estudiantes": r[0][1]}

        where_alto = f"WHERE rd.RIESGO IN ('4. alto', '5. muy alto') {f}" if f else "WHERE rd.RIESGO IN ('4. alto', '5. muy alto')"
        r = run_query(f"SELECT COUNT(*) FROM riesgo_desercion rd {join_prog} {where_alto}")
        en_riesgo_alto = r[0][0] if r else 0

        r = run_query(f"SELECT e.CODIGO_GENERO, COUNT(*) FROM estudiantes e {join_prog_simple} {where_e} GROUP BY e.CODIGO_GENERO")
        distribucion_genero = {("Masculino" if row[0] == "M" else "Femenino"): row[1] for row in r} if r else {}

        riesgo_por_programa = []
        if role in ("RECTOR", "ADMINISTRADOR", "DECANO"):
            r = run_query(f"SELECT p.nombre_programa, rd.RIESGO, COUNT(*), ROUND(AVG(rd.PROBABILIDAD_DESERCION)*100,1) FROM riesgo_desercion rd {join_prog} {where} GROUP BY p.nombre_programa, rd.RIESGO ORDER BY p.nombre_programa, rd.RIESGO")
            riesgo_por_programa = [{"programa": row[0], "nivel_riesgo": row[1], "total": row[2], "probabilidad_pct": float(row[3])} for row in r] if r else []

        return {
            "role":    role,
            "scope":   access_filter.description,
            "resumen": {
                "total_estudiantes":                   total_estudiantes,
                "en_riesgo_alto_muy_alto":             en_riesgo_alto,
                "pct_riesgo_alto":                     round(en_riesgo_alto / total_estudiantes * 100, 1) if total_estudiantes else 0,
                "probabilidad_desercion_promedio_pct": prob_promedio,
                "programa_con_mas_estudiantes":        programa_top,
                "distribucion_genero":                 distribucion_genero,
            },
            "distribucion_riesgo": distribucion_riesgo,
            "riesgo_por_programa": riesgo_por_programa,
        }

    except Exception as e:
        print(f"❌ Error en /stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando estadísticas: {str(e)}")


@app.get("/health")
def health():
    return {"status": "ok", "version": "3.1"}


# ==============================
# TODO: INTEGRACIÓN JWT
# @app.post("/ask")
# def ask_agent(request: Question, current_user: TokenUser = Depends(get_current_user)):
#     role    = current_user.role
#     faculty = current_user.faculty
#     program = current_user.program
#     user_id = current_user.username
# ==============================