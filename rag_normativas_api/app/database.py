from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SERVICE

DATABASE_URL = (
    f"oracle+oracledb://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/?service_name={DB_SERVICE}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()