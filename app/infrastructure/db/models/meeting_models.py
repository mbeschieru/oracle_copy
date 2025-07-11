from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.types import CHAR
from app.infrastructure.config.db_config import Base
import uuid
from datetime import datetime

class MeetingModel(Base):
    __tablename__ = "meetings"

    meeting_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    datetime = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
