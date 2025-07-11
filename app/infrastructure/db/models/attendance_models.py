from sqlalchemy import Column, Time, Date, ForeignKey
from sqlalchemy.types import CHAR, Integer
from app.infrastructure.config.db_config import Base
import uuid

class AttendanceModel(Base):
    __tablename__ = "attendances"

    attendance_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(CHAR(36), ForeignKey("meetings.meeting_id"), nullable=False)
    user_id = Column(CHAR(36), ForeignKey("users.user_id"), nullable=False)
    day = Column(Date, nullable=False)
    check_in = Column(Time, nullable=False)
    check_out = Column(Time, nullable=False)
    time_spent = Column(Integer, nullable=False)  
