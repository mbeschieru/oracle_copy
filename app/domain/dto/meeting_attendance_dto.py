from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.domain.enums.enums import AttendanceResponse
from datetime import datetime

class MeetingAttendanceCreateDTO(BaseModel):
    meeting_id: UUID
    status: AttendanceResponse = AttendanceResponse.ACCEPTED  # default when the user clicks ✓

class MeetingAttendanceReadDTO(BaseModel):
    meeting_attendance_id: UUID
    meeting_id: UUID
    user_id: UUID
    status: AttendanceResponse
    responded_at: datetime

    model_config = ConfigDict(from_attributes=True)
