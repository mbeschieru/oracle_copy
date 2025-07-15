from datetime import date
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
    status: str
    status_description: str | None = None
    entries: List[TimeEntryDTO] = []
    model_config = ConfigDict(from_attributes=True)
