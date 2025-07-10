from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import date
from typing import List

class TimeEntryDTO(BaseModel):
    day: date
    hours: float = Field(..., ge=0, le=24)
    project_id: UUID
    description: str

class TimesheetCreateDTO(BaseModel):
    week_start: date
    entries: List[TimeEntryDTO]

class TimesheetReadDTO(BaseModel):
    timesheet_id: UUID
    user_id: UUID
    week_start: date
    approved: bool

    model_config = ConfigDict(from_attributes=True)
