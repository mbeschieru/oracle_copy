from abc import ABC, abstractmethod
from uuid import UUID
from datetime import date
from typing import List, Optional
from app.domain.entities.attendance import Attendance

class AttendanceRepositoryInterface(ABC):

    @abstractmethod
    def get_attendance_for_user(self, user_id: UUID) -> List[Attendance]:
        """Get attendance logs for a specific user (time tracking, not meeting responses)"""
        pass

    @abstractmethod
    def get_by_day(self, user_id: UUID, day: date) -> Attendance:
        """Retrieve attendance for a particular day (time tracking)"""
        pass

    @abstractmethod
    def get_attendance_for_meeting(self, meeting_id: UUID, page: int = 1, page_size: int = 10) -> tuple[List[Attendance], int]:
        """Get paginated attendance for a specific meeting (time tracking)"""
        pass

    @abstractmethod
    def get_attendance_count_for_meeting(self, meeting_id: UUID) -> int:
        """Get total attendance count for a meeting (time tracking)"""
        pass

    @abstractmethod
    def create_attendance(self, attendance: Attendance) -> None:
        """Create a new attendance record (time tracking)"""
        pass
