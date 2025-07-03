from sqlalchemy import Column, Date, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.infrastructure.config.db_config import Base

class TimesheetModel(Base):
    __tablename__ = "timesheets"

    timesheet_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    week_start = Column(Date, nullable=False)
    approved = Column(Boolean, default=False)

    user = relationship("UserModel", backref="timesheets")
