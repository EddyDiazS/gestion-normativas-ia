import numpy as np
from sentence_transformers import SentenceTransformer

# Modelo robusto para español
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

def embed_text(text: str) -> np.ndarray:
    embedding = model.encode(text, normalize_embeddings=True)
    return np.array(embedding, dtype="float32")
