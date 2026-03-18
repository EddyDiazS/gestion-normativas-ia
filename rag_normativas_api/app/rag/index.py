import faiss
import numpy as np

from app.rag.embeddings import embed_text


def build_faiss_index(chunks):
    embeddings = []
    valid_chunks = []

    for chunk in chunks:
        try:
            emb = embed_text(chunk["content"])
            if emb is None or len(emb) == 0:
                continue

            embeddings.append(emb)
            valid_chunks.append(chunk)
        except Exception as error:
            print(f"Error embedding: {error}")

    if not embeddings:
        raise ValueError("No se pudieron generar embeddings validos.")

    embeddings = np.array(embeddings, dtype="float32")
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    print(f"Indice FAISS creado con {index.ntotal} vectores")
    return index, valid_chunks
