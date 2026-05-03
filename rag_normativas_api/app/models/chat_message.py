from sqlalchemy import Column, Integer, String, DateTime, Text, Identity
from sqlalchemy.sql import func
from app.database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, Identity(start=1, increment=1), primary_key=True)
    session_id = Column(String(1000), nullable=False)
    user_id = Column(Integer, nullable=False)
    role = Column(String(50), nullable=False)  
    content = Column(String(8000), nullable=True)
    agent_type = Column(String(50), default="RAG")
    created_at = Column(DateTime(timezone=True), server_default=func.now())