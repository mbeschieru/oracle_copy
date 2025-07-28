import uuid

from sqlalchemy import Column, Date, ForeignKey, String
from sqlalchemy.types import CHAR

from app.infrastructure.config.db_config import Base


class AbsenceModel(Base):
    __tablename__ = "absences"

    absence_id = Column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id = Column(CHAR(36), ForeignKey("users.user_id"), nullable=False)
    week_start = Column(Date, nullable=False)
    days = Column(
        String(50), nullable=False
    )  # Comma-separated days (e.g., '2025-07-14,2025-07-15')
    reason = Column(String(255), nullable=False)
    status = Column(String(20), default="pending")
    status_description = Column(String(255), nullable=True)

