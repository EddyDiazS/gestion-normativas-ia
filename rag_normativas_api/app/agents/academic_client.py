import httpx
import os
from app.config import GOOGLE_API_KEY

ACADEMIC_AGENT_URL = os.getenv("ACADEMIC_AGENT_URL", "http://127.0.0.1:8001")


def ask_academic_agent(question: str, role: str, faculty: str = None, 
                        program: str = None, user_id: str = None, 
                        session_id: str = None) -> str:
    try:
        response = httpx.post(
            f"{ACADEMIC_AGENT_URL}/ask",
            json={
                "question":   question,
                "role":       role,
                "faculty":    faculty,
                "program":    program,
                "user_id":    str(user_id) if user_id else None,
                "session_id": session_id,
            },
            timeout=30.0
        )
        data = response.json()
        return data.get("answer", "No se pudo obtener respuesta del agente académico.")
    except Exception as e:
        print(f"Error contactando agente académico: {e}")
        return "El agente académico no está disponible en este momento."