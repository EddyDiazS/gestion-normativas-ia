import httpx
import os
from app.config import GOOGLE_API_KEY

ACADEMIC_AGENT_URL = os.getenv("ACADEMIC_AGENT_URL", "http://127.0.0.1:8001")


def ask_academic_agent(question: str, role: str, faculty: str = None, 
                        program: str = None, user_id: str = None, 
                        session_id: str = None) -> tuple:
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
        print(f"🔢 keys del agente: {list(data.keys())}")
        print(f"🔢 data completa: {data}")
        inp = data.get("tokens_input", 0)
        out = data.get("tokens_output", 0)
        cost = data.get("estimated_cost", round((inp * 0.075 + out * 0.30) / 1_000_000, 6))
        print(f"📤 → role={role} | faculty={faculty} | program={program}")
        print(f"📥 ← {data.get('answer','')[:100]}")
        return data.get("answer", "No se pudo obtener respuesta del agente académico."), inp, out, cost
    except Exception as e:
        print(f"Error contactando agente académico: {e}")
        return "El agente académico no está disponible en este momento.", 0, 0, 0.0