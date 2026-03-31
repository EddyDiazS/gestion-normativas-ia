from unittest import result
from app.rag.loader import load_documents
from app.rag.chunker import divide_by_articles
from app.rag.index import build_faiss_index
from app.rag.generator import RAGEngine
from app.config import DATA_PATH
from sqlalchemy import text
from app.database import engine

try: 
    with engine.connect() as connection:
        connection.execute(text("ALTER TABLE users ADD cedula VARCHAR2(20) NULL"))
        connection.commit()
except Exception:
    pass

for column_sql in [
    "ALTER TABLE query_logs ADD input_tokens NUMBER(10) DEFAULT 0",
    "ALTER TABLE query_logs ADD output_tokens NUMBER(10) DEFAULT 0",
    "ALTER TABLE query_logs ADD estimated_cost NUMBER(10,6) DEFAULT 0",
]:
    try:
        with engine.connect() as connection:
            connection.execute(text(column_sql))
            connection.commit()
    except Exception:
        pass

documents = load_documents(DATA_PATH)
chunks = divide_by_articles(documents)
index, chunks = build_faiss_index(chunks)

rag_engine = RAGEngine(index, chunks)
