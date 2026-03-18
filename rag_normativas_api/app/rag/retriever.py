import re
import unicodedata

import faiss
import numpy as np

from app.rag.embeddings import embed_text


STOPWORDS = {
    "de", "la", "el", "los", "las", "un", "una", "unos", "unas", "y", "o",
    "en", "por", "para", "con", "sin", "que", "se", "del", "al", "a",
    "es", "son", "como", "si", "me", "mi", "tu", "su", "sus"
}


def _tokenize(text: str):
    tokens = re.findall(r"[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]+", text.lower())
    return {t for t in tokens if len(t) > 2 and t not in STOPWORDS}


def _normalize_for_regex(text: str) -> str:
    """Normaliza un texto removiendo tildes para búsqueda de regex"""
    # Descomponer el texto
    decomposed = unicodedata.normalize('NFD', text)
    # Remover marcas diacríticas
    normalized = ''.join(c for c in decomposed if unicodedata.category(c) != 'Mn')
    return normalized


def _extract_article_numbers(text: str):
    """Extrae números de artículos mencionados en el texto (ej: 'artículo 10' -> 10)"""
    # Busca patrones como "artículo X", "art. X", etc.
    patterns = [
        r"articulos?\s+(?:numero\s+)?(?:no\.?\s+)?(\d+)",  # articulo(s) numero, sin acentos
        r"art(?:\.?)\s+(?:no\.?\s+)?(\d+)",  # art, art.
    ]
    
    articles = set()
    # Normalizar el texto removiendo acentos
    text_normalized = _normalize_for_regex(text.lower())
    
    for pattern in patterns:
        matches = re.finditer(pattern, text_normalized)
        for match in matches:
            article_num = match.group(1)
            articles.add(article_num)
    
    return articles


def _canonical_article(meta):
    article = str(meta.get("article", "")).lower()
    normalized = re.sub(r"[^\w\s]", " ", article)
    match = re.search(r"\b(\d+|[ivxlcdm]+)\b", normalized, re.IGNORECASE)
    if not match:
        return None
    token = match.group(1).upper()
    return str(int(token)) if token.isdigit() else token


def _query_variants(query: str):
    variants = [query.strip()]

    splitters = [r"\s+y\s+", r"\s+o\s+", r",", r";", r"\."]
    parts = [query]
    for splitter in splitters:
        next_parts = []
        for part in parts:
            next_parts.extend(re.split(splitter, part, flags=re.IGNORECASE))
        parts = next_parts

    for part in parts:
        cleaned = part.strip()
        if len(cleaned) >= 12:
            variants.append(cleaned)

    seen = set()
    unique = []
    for variant in variants:
        key = variant.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(variant)

    return unique


def recuperar_contexto(query, index, chunks, k=5):
    if not chunks:
        return []

    # Primero: buscar artículos mencionados explícitamente en la pregunta
    mentioned_articles = _extract_article_numbers(query)
    direct_article_chunks = []
    
    if mentioned_articles:
        for chunk in chunks:
            meta = chunk.get("metadata", {})
            article = str(meta.get("article", "")).strip()
            
            # El metadata del article puede ser solo el número (ej: "13")
            # Intentar coincidir directamente con el número
            if article in mentioned_articles:
                direct_article_chunks.append(chunk)
            else:
                # Si no coincide directamente, intentar extraer número del texto
                # (en caso que sea "ARTÍCULO 10" o "articulo 10")
                article_normalized = _normalize_for_regex(article.lower())
                article_match = re.search(r"articulos?\s+(\d+)", article_normalized)
                if article_match:
                    article_num = article_match.group(1)
                    if article_num in mentioned_articles:
                        direct_article_chunks.append(chunk)
        
        # Si encontramos artículos mencionados, priorizarlos
        if direct_article_chunks:
            # Limitar a k chunks de artículos directos
            direct_article_chunks.sort(
                key=lambda c: (
                    0 if str(c.get("metadata", {}).get("source_type", "secondary")).lower() == "original" else 1,
                    -len(c.get("content", ""))  # Preferir chunks más largos
                )
            )
            
            if len(direct_article_chunks) >= k:
                return direct_article_chunks[:k]
            
            # Si hay menos de k, llenar con búsqueda semántica
            remaining_k = k - len(direct_article_chunks)
        else:
            remaining_k = k
    else:
        remaining_k = k

    variants = _query_variants(query)
    query_tokens = _tokenize(query)
    search_k = min(max(remaining_k * 8, 24), len(chunks))
    candidates = {}

    for variant in variants:
        q_emb = embed_text(variant)
        if q_emb is None or len(q_emb) == 0:
            continue

        q_emb = np.array([q_emb], dtype="float32")
        faiss.normalize_L2(q_emb)
        scores, indices = index.search(q_emb, search_k)

        for rank, (idx, score) in enumerate(zip(indices[0], scores[0]), start=1):
            if idx < 0 or idx >= len(chunks):
                continue

            semantic_score = (1.0 / (50 + rank)) + float(score)
            if idx not in candidates:
                candidates[idx] = {
                    "semantic": semantic_score,
                    "lexical": 0.0,
                    "lexical_global": 0.0,
                }
            else:
                candidates[idx]["semantic"] = max(candidates[idx]["semantic"], semantic_score)

    # Global lexical pass to recover complementary articles for multi-part questions.
    if query_tokens:
        lexical_rank = []
        for idx, chunk in enumerate(chunks):
            content_tokens = _tokenize(chunk.get("content", ""))
            if not content_tokens:
                continue

            overlap = len(query_tokens & content_tokens)
            if overlap <= 0:
                continue

            score = overlap / max(1, len(query_tokens))
            lexical_rank.append((idx, score))

        lexical_rank.sort(key=lambda item: item[1], reverse=True)
        lexical_pool = lexical_rank[: min(len(chunks), max(k * 6, 24))]
        for idx, score in lexical_pool:
            if idx not in candidates:
                candidates[idx] = {
                    "semantic": 0.0,
                    "lexical": 0.0,
                    "lexical_global": score,
                }
            else:
                candidates[idx]["lexical_global"] = max(
                    candidates[idx].get("lexical_global", 0.0), score
                )

    if not candidates:
        print("Warning: invalid query embedding")
        return []

    for idx in list(candidates.keys()):
        meta = chunks[idx].get("metadata", {})
        source_type = str(meta.get("source_type", "secondary")).lower()
        candidates[idx]["source_boost"] = 0.08 if source_type == "original" else 0.0

        content_tokens = _tokenize(chunks[idx].get("content", ""))
        if not content_tokens or not query_tokens:
            continue

        overlap = len(query_tokens & content_tokens)
        candidates[idx]["lexical"] = overlap / max(1, len(query_tokens))

    ranked_indices = sorted(
        candidates.keys(),
        key=lambda i: (
            candidates[i].get("semantic", 0.0)
            + 0.30 * candidates[i].get("lexical", 0.0)
            + 0.45 * candidates[i].get("lexical_global", 0.0)
            + candidates[i].get("source_boost", 0.0)
        ),
        reverse=True,
    )

    results = []
    seen = set()
    
    # Primero agregar los chunks de artículos directos
    for chunk in direct_article_chunks:
        metadata = chunk.get("metadata", {})
        article_key = _canonical_article(metadata)
        if article_key is not None:
            key = ("article", article_key)
        else:
            key = ("document", metadata.get("document"), metadata.get("article"))
        if key in seen:
            continue
        seen.add(key)
        results.append(chunk)
        if len(results) >= k:
            break
    
    # Luego los de búsqueda semántica
    for idx in ranked_indices:
        if len(results) >= k:
            break
        
        chunk = chunks[idx]
        metadata = chunk.get("metadata", {})
        article_key = _canonical_article(metadata)
        if article_key is not None:
            key = ("article", article_key)
        else:
            key = ("document", metadata.get("document"), metadata.get("article"))
        if key in seen:
            continue

        seen.add(key)
        results.append(chunk)

    return results
