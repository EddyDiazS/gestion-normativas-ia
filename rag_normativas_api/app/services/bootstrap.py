from app.rag.loader import load_documents
from app.rag.chunker import divide_by_articles
from app.rag.index import build_faiss_index
from app.rag.generator import RAGEngine
from app.config import DATA_PATH

documents = load_documents(DATA_PATH)
chunks = divide_by_articles(documents)
index, chunks = build_faiss_index(chunks)

rag_engine = RAGEngine(index, chunks)
