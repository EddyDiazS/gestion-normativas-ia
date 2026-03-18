from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy import Identity


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, Identity(start=1), primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    action = Column(String(255), nullable=False)

    timestamp = Column(DateTime, server_default=func.now())