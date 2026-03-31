from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy import Identity
from sqlalchemy import Text


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    faculty = Column(String(150))
    question = Column(String)
    answer = Column(String)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float(precision=6), default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

