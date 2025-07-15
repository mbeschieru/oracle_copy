from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.dto.meeting_attendance_dto import (
    MeetingAttendanceCreateDTO,
    MeetingAttendanceReadDTO,
)
from app.domain.enums.enums import AttendanceResponse


class MeetingAttendanceRepositoryInterface(ABC):

    @abstractmethod
    def create(
        self, dto: MeetingAttendanceCreateDTO, user_id: UUID
    ) -> MeetingAttendanceReadDTO: ...

    @abstractmethod
    def set_status(
        self, attendance_id: UUID, status: AttendanceResponse
    ) -> MeetingAttendanceReadDTO: ...

    @abstractmethod
    def list_for_meeting(
        self, meeting_id: UUID
    ) -> List[MeetingAttendanceReadDTO]: ...

    @abstractmethod
    def get_by_user_and_meeting(
        self, user_id: UUID, meeting_id: UUID
    ) -> Optional[MeetingAttendanceReadDTO]: ...
