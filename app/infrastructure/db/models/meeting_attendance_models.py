from sqlalchemy import Column, DateTime, Enum, ForeignKey
from sqlalchemy.types import CHAR
from datetime import datetime, timezone
import uuid

from app.domain.enums.enums import AttendanceResponse
from app.infrastructure.config.db_config import Base

class MeetingAttendanceModel(Base):
    __tablename__ = "meeting_attendances"

    meeting_attendance_id = Column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    meeting_id = Column(CHAR(36), ForeignKey("meetings.meeting_id"), nullable=False)
    user_id = Column(CHAR(36), ForeignKey("users.user_id"), nullable=False)
    status = Column(Enum(AttendanceResponse), nullable=False)
    responded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

