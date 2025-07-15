from datetime import date, datetime, time
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MeetingReadDTO(BaseModel):
    meeting_id: UUID
    title: str
    datetime: datetime
    duration_minutes: int
    model_config = ConfigDict(from_attributes=True)


class AttendanceReadDTO(BaseModel):
    attendance_id: UUID
    meeting_id: UUID
    user_id: UUID
    user_name: str
    user_email: str
    day: date
    check_in: time
    check_out: time
    time_spent: int  # in minutes
    model_config = ConfigDict(from_attributes=True)


class MeetingWithAttendanceDTO(BaseModel):
    meeting: MeetingReadDTO
    attendances: List[AttendanceReadDTO]
    total_attendances: int
    page: int
    page_size: int
    total_pages: int


class PaginatedAttendanceDTO(BaseModel):
    attendances: List[AttendanceReadDTO]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class MeetingCreateDTO(BaseModel):
    title: str
    datetime: datetime
    duration_minutes: int
