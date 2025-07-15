from typing import List
from uuid import UUID

from app.domain.dto.meeting_attendance_dto import (
    MeetingAttendanceCreateDTO,
    MeetingAttendanceReadDTO,
)
from app.domain.enums.enums import AttendanceResponse
from app.domain.repositories.meeting_attendance_repository import (
    MeetingAttendanceRepositoryInterface,
)


class MeetingAttendanceService:

    def __init__(self, repo: MeetingAttendanceRepositoryInterface):
        self.repo = repo

    def create(
        self, dto: MeetingAttendanceCreateDTO, user_id: UUID
    ) -> MeetingAttendanceReadDTO:
        # can add extra validation here (e.g. no duplicate response)
        return self.repo.create(dto, user_id)

    def respond(
        self, attendance_id: UUID, status: AttendanceResponse
    ) -> MeetingAttendanceReadDTO:
        return self.repo.set_status(attendance_id, status)

    def list_for_meeting(
        self, meeting_id: UUID
    ) -> List[MeetingAttendanceReadDTO]:
        return self.repo.list_for_meeting(meeting_id)
