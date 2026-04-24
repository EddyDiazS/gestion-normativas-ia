from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Numeric, Identity
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy import Identity
from sqlalchemy import Text


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, Identity(start=1, increment=1), primary_key=True, index=True)
    user_id = Column(Integer)
    faculty = Column(String(150))
    question = Column(String(2000))
    answer = Column(String(4000))
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    estimated_cost = Column(Numeric(10,6), default=0.0)
    agent_type = Column(String(20), default="RAG")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    