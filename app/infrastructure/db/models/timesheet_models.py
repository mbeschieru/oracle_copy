from sqlalchemy import Column, Date, Boolean, ForeignKey
from sqlalchemy.types import CHAR
from sqlalchemy.orm import relationship
import uuid
from app.infrastructure.config.db_config import Base

class TimesheetModel(Base):
    __tablename__ = "timesheets"

    timesheet_id =  Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.user_id"))
    week_start = Column(Date, nullable=False)
    approved = Column(Boolean, default=False)

    user = relationship("UserModel", backref="timesheets")
