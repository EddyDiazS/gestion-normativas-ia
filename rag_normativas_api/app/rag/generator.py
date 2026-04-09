import re
import unicodedata
from typing import Optional

import google.generativeai as genai

from app.config import GOOGLE_API_KEY
from app.rag.retriever import recuperar_contexto
from app.utils.normalizer import normalize_question

genai.configure(api_key=GOOGLE_API_KEY)
SESSION_MEMORY = {}
NO_ANSWER_CANONICAL = (
    "La informacion solicitada no se encuentra establecida explicitamente en la normativa consultada."
)
UNCERTAINTY_MARKERS = (
    "no se encuentra establecida explicitamente",
    "no se encuentra establecido explicitamente",
    "no se encuentra completo",
    "no se encuentra completa",
    "no esta completo",
    "no esta completa",
    "no se establece explicitamente",
    "no se establece",
    "no se define explicitamente",
    "no se define",
    "no se detalla",
    "no se detalla como",
    "no se especifica",
    "no se evidencia",
    "no es posible determinar",
    "no se puede determinar",
    "no se dispone de informacion suficiente",
    "no se cuenta con informacion suficiente",
    "contexto normativo suministrado",
)


def _is_general_greeting(question: str) -> bool:
    """Detecta preguntas generales que no necesitan RAG (saludos, funciones, etc.)"""
    q = question.lower().strip()
    
    # Saludos simples
    greetings = [
        "hola", "hi", "hello", "buenos días", "buenas tardes", "buenas noches",
        "que tal", "qué tal", "como estas", "cómo estás", "how are you"
    ]
    
    # Preguntas sobre el bot mismo
    function_markers = [
        "cuáles son tus funciones", "cuales son tus funciones",
        "qué puedes hacer", "que puedes hacer",
        "para qué sirves", "para que sirves",
        "cuál es tu función", "cual es tu funcion",
        "qué eres", "que eres",
        "quién eres", "quien eres",
        "ayuda", "help",
        "cómo funciona", "como funciona"
    ]
    
    # Considerar como pregunta general si es muy corta o es un saludo/función
    if len(q.split()) <= 3:
        for greeting in greetings:
            if greeting in q:
                return True
    
    for marker in function_markers:
        if marker in q:
            return True
    
    return False


def _get_general_answer(question: str) -> str:
    """Proporciona respuestas para preguntas generales sin necesidad de RAG."""
    q = question.lower().strip()
    
    if any(greeting in q for greeting in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas noches", "que tal", "qué tal", "como estas", "cómo estás"]):
        return (
            "¡Hola! Soy el asistente de normativas de la Fundación Universitaria Konrad Lorenz. "
            "Estoy aquí para ayudarte con preguntas sobre el reglamento académico, requisitos de programas, "
            "políticas institucionales y otros temas normativos. "
            "¿En qué puedo ayudarte hoy?"
        )
    
    if any(marker in q for marker in ["cuáles son tus funciones", "cuales son tus funciones", "qué puedes hacer", "que puedes hacer", "para qué sirves", "para que sirves", "cómo funciona", "como funciona"]):
        return (
            "Mis funciones principales son:\n"
            "1. Responder preguntas sobre el reglamento académico y normativas de la institución\n"
            "2. Explicar artículos específicos de la normativa\n"
            "3. Ayudarte a entender requisitos y políticas académicas\n"
            "4. Proporcionar información sobre procedimientos y trámites normados\n"
            "5. Mantener historial de nuestras conversaciones para contexto\n\n"
            "Puedes preguntarme sobre cualquier aspecto normativo institucional."
        )
    
    if any(marker in q for marker in ["quién eres", "quien eres", "qué eres", "que eres"]):
        return (
            "Soy un asistente de IA especializado en normativas de la Fundación Universitaria Konrad Lorenz. "
            "Mi propósito es proporcionar información rápida y precisa sobre reglamentos académicos, "
            "políticas institucionales y procedimientos normativos de la universidad."
        )
    
    if "ayuda" in q or "help" in q:
        return (
            "¡Claro! Aquí hay algunas cosas que puedo hacer:\n"
            "• Explicar artículos del reglamento académico (ej: 'Explícame el artículo 13')\n"
            "• Responder preguntas sobre requisitos y políticas\n"
            "• Aclarar procedimientos y normas académicas\n"
            "• Proporcionar información sobre políticas institucionales\n\n"
            "¿Hay algo específico que necesites saber?"
        )
    
    return "No estoy seguro de cómo responder eso. ¿Puedes rephrasear tu pregunta?"


def _is_complex_question(question: str) -> bool:
    q = question.lower()
    tokens = re.findall(r"\w+", q)
    connectors = [
        "si",
        "entonces",
        "ademas",
        "adicionalmente",
        "pero",
        "y",
        "o",
        "caso",
        "cuando",
        "mientras",
    ]
    has_connectors = sum(1 for connector in connectors if connector in q) >= 2
    is_long = len(tokens) >= 16
    return has_connectors or is_long


def classify_question(question: str) -> str:
    """Clasifica la pregunta en 'NORMATIVE' o 'SITUATIONAL'.

    Reglas sencillas basadas en pistas léxicas:
    - Si contiene referencias personales o escenarios concretos -> SITUATIONAL
    - Si pregunta por el contenido de artículos o textos normativos -> NORMATIVE
    - Por defecto, NORMATIVE
    """
    q = question.lower()
    situational_markers = [
        "mi ", "mi", "estoy", "en mi caso", "que puedo", "qué puedo", "qué hago", "qué debo", "requisitos para", "elegible", "prácticas", "practicas", "si estoy", "si tengo", "estudiante", "semestre",
    ]
    normative_markers = ["qué dice", "qué establece", "según el artículo", "artículo", "qué dispone", "qué regula"]

    if any(marker in q for marker in situational_markers) and not any(marker in q for marker in normative_markers):
        return "SITUATIONAL"
    if any(marker in q for marker in normative_markers) and not any(marker in q for marker in situational_markers):
        return "NORMATIVE"
    if any(marker in q for marker in situational_markers):
        return "SITUATIONAL"
    return "NORMATIVE"


def extract_scenario_slots(question: str) -> dict:
    """Extrae slots básicos de un escenario situacional.

    Devuelve keys posibles: nivel, semestre, objetivo (practicas/reintegro), materias_text
    """
    q = question.lower()
    slots = {"nivel": None, "semestre": None, "objetivo": None, "materias_text": None}

    for nivel in ["tecnico", "tecnologico", "profesional", "especializacion", "maestria", "doctorado"]:
        if nivel in q:
            slots["nivel"] = nivel
            break

    m = re.search(r"(\b[0-9]{1,2}(?:ro|do|er)?\s+semestre\b)|\bsemestre\s+([0-9]{1,2})\b", q)
    if m:
        num = m.group(1) or m.group(2)
        if num:
            slots["semestre"] = re.sub(r"[^0-9]", "", num)

    if "practic" in q or "práctic" in q:
        slots["objetivo"] = "practicas"
    if "reintegro" in q or "reintegr" in q:
        slots["objetivo"] = "reintegro"

    m2 = re.search(r"inscribi[óo]?\s+(.*?)\b(?:y|pero|porque|,|\.|$)", q)
    if m2:
        slots["materias_text"] = m2.group(1).strip()

    return slots


def _normalize_text(value: str) -> str:
    lowered = value.lower().strip()
    normalized = unicodedata.normalize("NFD", lowered)
    without_accents = "".join(
        ch for ch in normalized if unicodedata.category(ch) != "Mn"
    )
    return re.sub(r"\s+", " ", without_accents)


def _is_full_no_answer(answer_text: str) -> bool:
    normalized_answer = _normalize_text(answer_text)
    normalized_target = _normalize_text(NO_ANSWER_CANONICAL)
    if normalized_answer == normalized_target:
        return True
    if normalized_answer.startswith(normalized_target) and len(normalized_answer) <= len(
        normalized_target
    ) + 20:
        return True
    return False


def _has_uncertainty_markers(answer_text: str) -> bool:
    normalized_answer = _normalize_text(answer_text)
    return any(marker in normalized_answer for marker in UNCERTAINTY_MARKERS)


def _clip_context_content(content: str, max_chars: int = 12000):
    if len(content) <= max_chars:
        return content, False

    clipped = content[:max_chars]

    # Avoid splitting words to reduce malformed legal fragments.
    if max_chars < len(content) and not content[max_chars].isspace():
        last_space = clipped.rfind(" ")
        if last_space > max_chars * 0.7:
            clipped = clipped[:last_space]

    return clipped.rstrip() + "\n[Contenido truncado por limite de contexto]", True


def _roman_to_int(value: str):
    roman_values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    token = value.upper()
    if not token or any(ch not in roman_values for ch in token):
        return None

    total = 0
    prev = 0
    for ch in reversed(token):
        current = roman_values[ch]
        if current < prev:
            total -= current
        else:
            total += current
            prev = current
    return total if total > 0 else None


def _canonical_article_tokens(value: str):
    normalized = _normalize_text(str(value))
    parts = re.findall(r"\b(?:\d+|[ivxlcdm]+)\b", normalized, re.IGNORECASE)
    canonical = set()

    for part in parts:
        token = part.upper()
        if token.isdigit():
            canonical.add(str(int(token)))
            continue

        roman_value = _roman_to_int(token)
        if roman_value is not None:
            canonical.add(str(roman_value))
            canonical.add(token)

    return canonical


def _extract_mentioned_articles(answer_text: str):
    normalized = _normalize_text(answer_text)
    citation_blocks = re.findall(
        r"\bart(?:iculo|\.?)s?\s*[:\-]?\s*([0-9ivxlcdm]+(?:\s*(?:,|y|e|-|al)\s*[0-9ivxlcdm]+)*)",
        normalized,
        re.IGNORECASE,
    )

    mentioned = set()
    for block in citation_blocks:
        mentioned |= _canonical_article_tokens(block)
    return mentioned


def _build_facet_queries(question: str):
    normalized = _normalize_text(question).replace("¿", " ").replace("?", " ")
    candidates = [question.strip(), normalized]

    segments = re.split(r"[,;:.]", normalized)
    for segment in segments:
        segment = segment.strip()
        if len(segment.split()) >= 5:
            candidates.append(segment)

        subsegments = re.split(
            r"\b(?:y|e|ademas|adicionalmente|tambien|asi como)\b",
            segment,
            flags=re.IGNORECASE,
        )
        for subsegment in subsegments:
            subsegment = subsegment.strip()
            if len(subsegment.split()) >= 6:
                candidates.append(subsegment)

    tokens = normalized.split()
    if len(tokens) >= 20:
        midpoint = len(tokens) // 2
        candidates.append(" ".join(tokens[:midpoint]))
        candidates.append(" ".join(tokens[midpoint:]))

    unique = []
    seen = set()
    for candidate in candidates:
        key = candidate.strip()
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        unique.append(key)

    return unique[:8]


def _chunk_article_key(chunk):
    meta = chunk.get("metadata", {})
    article_tokens = _canonical_article_tokens(str(meta.get("article", "")))
    numeric_tokens = sorted(
        [token for token in article_tokens if token.isdigit()],
        key=lambda token: int(token),
    )

    if numeric_tokens:
        return ("article", numeric_tokens[0])

    if article_tokens:
        return ("article", sorted(article_tokens)[0])

    return (
        "document",
        str(meta.get("document", "")),
        str(meta.get("article", "N/A")),
    )


def _chunk_primary_article_id(chunk):
    meta = chunk.get("metadata", {})
    tokens = _canonical_article_tokens(str(meta.get("article", "")))
    numeric = sorted([token for token in tokens if token.isdigit()], key=lambda token: int(token))
    if numeric:
        return numeric[0]
    if tokens:
        return sorted(tokens)[0]
    return None


def _extract_referenced_article_ids(content: str):
    normalized = _normalize_text(content)
    references = re.findall(r"\barticulo\s+([0-9ivxlcdm]+)\b", normalized, re.IGNORECASE)
    article_ids = set()
    for ref in references:
        tokens = _canonical_article_tokens(ref)
        article_ids |= {token for token in tokens if token.isdigit()}
        if not any(token.isdigit() for token in tokens):
            article_ids |= tokens
    return article_ids


def _should_replace_chunk(current_chunk, candidate_chunk):
    current_meta = current_chunk.get("metadata", {})
    candidate_meta = candidate_chunk.get("metadata", {})
    current_source = str(current_meta.get("source_type", "secondary")).lower()
    candidate_source = str(candidate_meta.get("source_type", "secondary")).lower()

    if candidate_source == "original" and current_source != "original":
        return True

    if current_source == candidate_source:
        if len(candidate_chunk.get("content", "")) > len(current_chunk.get("content", "")):
            return True

    return False


class RAGEngine:
    def __init__(self, index, chunks):
        self.index = index
        self.chunks = chunks

    def _collect_context_chunks(
        self,
        question: str,
        normalized_question: str,
        retrieval_k: int,
    ):
        facet_queries = _build_facet_queries(question)
        per_query_k = max(4, min(8, retrieval_k))

        selected = {}
        order = []

        def add_chunk(chunk):
            key = _chunk_article_key(chunk)
            if key not in selected:
                selected[key] = chunk
                order.append(key)
                return

            if _should_replace_chunk(selected[key], chunk):
                selected[key] = chunk

        best_by_article = {}
        for chunk in self.chunks:
            article_id = _chunk_primary_article_id(chunk)
            if article_id is None:
                continue
            if article_id not in best_by_article:
                best_by_article[article_id] = chunk
                continue
            if _should_replace_chunk(best_by_article[article_id], chunk):
                best_by_article[article_id] = chunk

        for facet_query in facet_queries:
            facet_norm = normalize_question(facet_query)
            for chunk in recuperar_contexto(
                facet_norm,
                self.index,
                self.chunks,
                per_query_k,
            ):
                add_chunk(chunk)

        extra_k = min(24, max(12, retrieval_k * 2))
        for chunk in recuperar_contexto(
            normalized_question,
            self.index,
            self.chunks,
            extra_k,
        ):
            add_chunk(chunk)

        seed_size = max(4, retrieval_k // 2)
        seed_keys = order[:seed_size]

        referenced_ids = set()
        for key in seed_keys:
            content = selected[key].get("content", "")
            referenced_ids |= _extract_referenced_article_ids(content)

        for article_id in sorted(
            referenced_ids,
            key=lambda value: int(value) if value.isdigit() else value,
        ):
            candidate = best_by_article.get(article_id)
            if candidate is None:
                continue
            add_chunk(candidate)

        ordered_chunks = [selected[key] for key in order]
        ordered_chunks.sort(
            key=lambda chunk: (
                0 if _chunk_primary_article_id(chunk) in referenced_ids else 1,
                0
                if str(chunk.get("metadata", {}).get("source_type", "secondary")).lower()
                == "original"
                else 1
            )
        )

        context_limit = min(16, max(8, retrieval_k + 4))
        return ordered_chunks[:context_limit]

    def answer(
        self,
        question: str,
        k: int = 5,
        session_id: Optional[str] = None,
    ):
        try:
            # Detectar preguntas generales (saludos, funciones del bot)
            if _is_general_greeting(question):
                answer_text = _get_general_answer(question)
                if session_id:
                    SESSION_MEMORY.setdefault(session_id, []).append(
                        f"Pregunta: {question}\nRespuesta: {answer_text}"
                    )
                return answer_text, True, [], 0, 0, 0.0
            
            normalized_question = normalize_question(question)
            retrieval_k = max(k, 10) if _is_complex_question(question) else k
            retrieval_k = min(retrieval_k, 20)

            context_chunks = self._collect_context_chunks(
                question=question,
                normalized_question=normalized_question,
                retrieval_k=retrieval_k,
            )

            if not context_chunks:
                return NO_ANSWER_CANONICAL, False, [], 0, 0, 0.0

            context_parts = []
            context_truncated = False
            for chunk in context_chunks:
                meta = chunk.get("metadata", {})
                document = meta.get("document", "Desconocido")
                article = str(meta.get("article", "N/A"))
                content, was_truncated = _clip_context_content(chunk.get("content", ""))
                context_truncated = context_truncated or was_truncated
                context_parts.append(
                    f"[Fuente: {document} | Articulo: {article}]\n{content}"
                )

            context = "\n\n".join(context_parts)
            history = SESSION_MEMORY.get(session_id, []) if session_id else []
            history_text = "\n".join(history[-4:])

            prompt = f"""
Eres un asistente institucional especializado en la normativa de la Fundacion Universitaria Konrad Lorenz.
Debes funcionar para cualquier pregunta o situacion real relacionada con normas academicas institucionales.

HISTORIAL RECIENTE (solo referencia contextual):
{history_text}

INSTRUCCIONES OBLIGATORIAS:
- Responde UNICAMENTE con base en la informacion del CONTEXTO NORMATIVO.
- No utilices conocimiento externo ni supuestos no respaldados.
- Usa lenguaje normativo, formal e institucional.
- Si hay conflicto entre un resumen y el texto completo del reglamento, prevalece el texto completo.
- Si la pregunta tiene varias partes, responde cada parte por separado.
- Antes de afirmar ausencia de informacion, revisa todo el contexto para identificar articulos aplicables directos o por remision expresa.
- Si una parte no esta soportada, indicalo explicitamente para esa parte.
- Distingue con precision conceptos cercanos (ej.: perdida de cupo vs perdida de condicion de estudiante).
- No conviertas remisiones generales en causales especificas si el articulo no las define directamente.
- Si detectas un fragmento normativo incompleto o truncado, reportalo como limitacion y no lo uses como base concluyente.
- Cita articulos explicitamente en el texto (ejemplo: Articulo 78, Paragrafo 1).
- Al final incluye una linea: "Citas: Articulo X, Articulo Y, ...".
- Si toda la pregunta carece de soporte explicito, responde exactamente:
"{NO_ANSWER_CANONICAL}"

CONTEXTO NORMATIVO:
{context}

PREGUNTA:
{question}

RESPUESTA:
"""

            response = genai.GenerativeModel("gemini-2.5-flash").generate_content(
    prompt
)

            if not response or not response.text:
                return "No se pudo generar una respuesta.", False, [], 0, 0, 0.0

            answer_text = response.text.strip()
            print("Respuesta generada:", response.usage_metadata)

            input_tokens = getattr (response.usage_metadata, "prompt_token_count", 0) or 0
            output_tokens = getattr (response.usage_metadata, "candidates_token_count", 0) or 0
            estimated_cost = (input_tokens * 0.30 / 1000000) + (output_tokens * 2.50 / 1000000)

            if _is_full_no_answer(answer_text):
                return NO_ANSWER_CANONICAL, False, [], input_tokens, output_tokens, estimated_cost

            if session_id:
                SESSION_MEMORY.setdefault(session_id, []).append(
                    f"Pregunta: {question}\nRespuesta: {answer_text}"
                )

            mentioned_articles = _extract_mentioned_articles(answer_text)

            sources = []
            seen = set()
            covered_tokens = set()
            for chunk in context_chunks:
                meta = chunk.get("metadata", {})
                document = meta.get("document", "Desconocido")
                article = str(meta.get("article", "N/A"))
                article_tokens = _canonical_article_tokens(article)

                if not mentioned_articles:
                    continue
                if not (article_tokens & mentioned_articles):
                    continue

                key = (document, article)
                if key in seen:
                    continue
                seen.add(key)
                covered_tokens |= article_tokens
                sources.append({"document": document, "article": article})

            all_citations_supported = bool(mentioned_articles) and mentioned_articles.issubset(
                covered_tokens
            )
            has_partial_uncertainty = _has_uncertainty_markers(answer_text)
            verified = (
                bool(sources)
                and all_citations_supported
                and not has_partial_uncertainty
                and not context_truncated
            )
            return answer_text, verified, sources, input_tokens, output_tokens, estimated_cost

        except Exception as error:
            print("ERROR EN RAGEngine.answer():", error)
            return "Ocurrio un error procesando la pregunta.", False, [], 0, 0, 0.0
