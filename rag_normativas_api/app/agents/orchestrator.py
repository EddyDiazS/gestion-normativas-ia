import google.generativeai as genai
from app.config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)

def classify_question(question: str) -> str:
    prompt = f"""Clasifica esta pregunta en una categoría:

RAG: reglamento, normativas, artículos, políticas, procedimientos, sanciones, cancelaciones.
ACADEMIC: datos de estudiantes, rendimiento, riesgo deserción, promedios, finanzas, becas, deudas.

Pregunta: "{question}"
Responde SOLO: RAG o ACADEMIC"""

    try:
        response = genai.GenerativeModel("gemini-2.5-flash").generate_content(prompt)
        result = response.text.strip().upper()
        return "ACADEMIC" if "ACADEMIC" in result else "RAG"
    except:
        return "RAG"