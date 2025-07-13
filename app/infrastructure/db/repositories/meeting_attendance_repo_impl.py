from uuid import UUID
from typing import List, Optional

from sqlalchemy.orm import Session
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.meeting_attendance_models import MeetingAttendanceModel
from app.domain.dto.meeting_attendance_dto import (
    MeetingAttendanceCreateDTO,
    MeetingAttendanceReadDTO,
)
from app.domain.enums.enums import AttendanceResponse
from app.domain.repositories.meeting_attendance_repository import (
    MeetingAttendanceRepositoryInterface,
)

class MeetingAttendanceRepository(MeetingAttendanceRepositoryInterface):
    """Concrete CRUD implementation for meeting‑attendance records."""

    def _to_dto(self, m: MeetingAttendanceModel) -> MeetingAttendanceReadDTO:
        return MeetingAttendanceReadDTO(
            meeting_attendance_id=m.meeting_attendance_id,
            meeting_id=m.meeting_id,
            user_id=m.user_id,
            status=m.status,
            responded_at=m.responded_at,
        )

    def __init__(self, db: Session | None = None) -> None:
        self.db = db or SessionLocal()

    def create(self, dto: MeetingAttendanceCreateDTO, user_id: UUID):
        obj = MeetingAttendanceModel(
            meeting_id=dto.meeting_id,
            user_id=user_id,
            status=dto.status,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_dto(obj)

    def set_status(self, attendance_id: UUID, status: AttendanceResponse):
        obj: Optional[MeetingAttendanceModel] = (
            self.db.query(MeetingAttendanceModel)
            .get(str(attendance_id))
        )
        if obj is None:
            return None
        obj.status = status
        self.db.commit()
        self.db.refresh(obj)
        return self._to_dto(obj)

    def list_for_meeting(self, meeting_id: UUID):
        return [
            self._to_dto(o)
            for o in (
                self.db.query(MeetingAttendanceModel)
                .filter(MeetingAttendanceModel.meeting_id == str(meeting_id))
                .all()
            )
        ]

    def get_by_user_and_meeting(self, user_id: UUID, meeting_id: UUID):
        obj = (
            self.db.query(MeetingAttendanceModel)
            .filter(
                MeetingAttendanceModel.user_id == str(user_id),
                MeetingAttendanceModel.meeting_id == str(meeting_id),
            )
            .one_or_none()
        )
        return self._to_dto(obj) if obj else None
