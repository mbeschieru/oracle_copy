from abc import ABC, abstractmethod
from datetime import date
from typing import List
from uuid import UUID

from app.domain.entities.attendance import Attendance


class AttendanceRepositoryInterface(ABC):

    @abstractmethod
    def get_attendance_for_user(self, user_id: UUID) -> List[Attendance]:
        """Get attendance logs for a specific user)"""

    @abstractmethod
    def get_by_day(self, user_id: UUID, day: date) -> Attendance:
        """Retrieve attendance for a particular day (time tracking)"""

    @abstractmethod
    def get_attendance_for_meeting(
        self, meeting_id: UUID, page: int = 1, page_size: int = 10
    ) -> tuple[List[Attendance], int]:
        """Get paginated attendance for a specific meeting (time tracking)"""

    @abstractmethod
    def get_attendance_count_for_meeting(self, meeting_id: UUID) -> int:
        """Get total attendance count for a meeting (time tracking)"""

    @abstractmethod
    def create_attendance(self, attendance: Attendance) -> None:
        """Create a new attendance record (time tracking)"""
