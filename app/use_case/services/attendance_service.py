from uuid import UUID

from app.domain.repositories.attendance_repository import (
    AttendanceRepositoryInterface,
)


class AttendanceService:

    def __init__(self, attendance_repo: AttendanceRepositoryInterface):
        self.repo = attendance_repo

    def get_attendance(self, user_id: UUID):
        return self.repo.get_attendance_for_user(user_id)
