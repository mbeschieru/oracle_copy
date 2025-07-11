from sqlalchemy import Column, Date, Boolean, ForeignKey, Float, String
from sqlalchemy.types import CHAR
from sqlalchemy.orm import relationship
import uuid
from app.infrastructure.config.db_config import Base
from app.infrastructure.db.models.project_models import ProjectModel

class TimeEntryModel(Base):
    __tablename__ = "time_entries"

    entry_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timesheet_id = Column(CHAR(36), ForeignKey("timesheets.timesheet_id"), nullable=False)
    day = Column(Date, nullable=False)
    hours = Column(Float, nullable=False)
    project_id = Column(CHAR(36), ForeignKey("projects.project_id"), nullable=False)
    description = Column(String(255), nullable=False)

class TimesheetModel(Base):
    __tablename__ = "timesheets"

    timesheet_id =  Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.user_id") , nullable= True)
    week_start = Column(Date, nullable=False)
    approved = Column(Boolean, default=False)
    status = Column(String(20), default="pending")
    status_description = Column(String(255), nullable=True)
    entries = relationship("TimeEntryModel", backref="timesheet", cascade="all, delete-orphan")

    
    
