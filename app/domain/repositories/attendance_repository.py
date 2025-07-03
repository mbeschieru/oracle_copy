from abc import ABC, abstractmethod
from uuid import UUID
from datetime import date
from typing import List
from app.domain.entities.attendance import Attendance

class AttendanceRepositoryInterface(ABC):

    @abstractmethod
    def get_attendance_for_user(self, user_id: UUID) -> List[Attendance]:
        """Get attendance logs for a specific user"""
        pass

    @abstractmethod
    def get_by_day(self, user_id: UUID, day: date) -> Attendance:
        """Retrieve attendance for a particular day"""
        pass
