from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.enums.enums import AttendanceResponse


class MeetingAttendanceCreateDTO(BaseModel):
    """DTO for creating a meeting attendance response (accept/decline)."""

    meeting_id: UUID
    status: AttendanceResponse = AttendanceResponse.ACCEPTED


class MeetingAttendanceReadDTO(BaseModel):
    """DTO for reading a meeting attendance response (accept/decline)."""

    meeting_attendance_id: UUID
    meeting_id: UUID
    user_id: UUID
    status: AttendanceResponse
    responded_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MeetingAttendanceWithUserDTO(BaseModel):
    meeting_attendance_id: UUID
    meeting_id: UUID
    user_id: UUID
    status: AttendanceResponse
    responded_at: datetime
    user_name: str
    user_email: str
