from sqlalchemy import Column, Integer, String, Boolean, DateTime, Identity
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Identity(start=1, increment=1),primary_key=True)

    username = Column(String(100), nullable=False)

    email = Column(String(150), nullable=False)

    hashed_password = Column(String(255), nullable=False)

    role = Column(String(50), nullable=False)

    faculty = Column(String(150), nullable=True)
    
    program = Column(String(150), nullable=True)

    cedula = Column(String(20), nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())