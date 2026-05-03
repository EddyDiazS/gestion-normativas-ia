import httpx
import os

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
            timeout=60.0
        )
        data = response.json()
        print(f"🔢 keys del agente: {list(data.keys())}")
        print(f"🔢 data completa: {data}")

        # Si el agente retornó error sin answer
        if "detail" in data and "answer" not in data:
            print(f"❌ Error del agente: {data['detail']}")
            return "El agente académico encontró un error procesando tu consulta.", 0, 0, 0.0

        inp    = data.get("tokens_input", 0)
        out    = data.get("tokens_output", 0)
        cost   = data.get("estimated_cost", round((inp * 0.075 + out * 0.30) / 1_000_000, 6))
        answer = data.get("answer", "").strip()

        if not answer:
            return "No se pudo obtener respuesta del agente académico.", inp, out, cost

        print(f"📤 → role={role} | faculty={faculty} | program={program}")
        print(f"📥 ← {answer[:100]}")
        return answer, inp, out, cost

    except Exception as e:
        print(f"Error contactando agente académico: {e}")
        return "El agente académico no está disponible en este momento.", 0, 0, 0.0