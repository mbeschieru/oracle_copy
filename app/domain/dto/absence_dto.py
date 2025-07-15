from datetime import date
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AbsenceCreateDTO(BaseModel):
    week_start: date
    days: List[date]
    reason: str


class AbsenceReadDTO(BaseModel):
    absence_id: UUID
    user_id: UUID
    week_start: date
    days: List[date]
    reason: str
    status: str
    status_description: str | None = None
    model_config = ConfigDict(from_attributes=True)
