from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domain.dto.meeting_attendance_dto import (
    MeetingAttendanceCreateDTO,
    MeetingAttendanceReadDTO,
    MeetingAttendanceWithUserDTO,
)
from app.domain.enums.enums import AttendanceResponse
from app.domain.repositories.meeting_attendance_repository import (
    MeetingAttendanceRepositoryInterface,
)
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.meeting_attendance_models import (
    MeetingAttendanceModel,
)
from app.infrastructure.db.models.user_models import UserModel


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
        from app.infrastructure.db.models.meeting_models import MeetingModel

        with SessionLocal() as db:
            print(f"[DEBUG] Checking meeting_id: {dto.meeting_id}")
            meeting = (
                db.query(MeetingModel)
                .filter(MeetingModel.meeting_id == str(dto.meeting_id))
                .first()
            )
            print(f"[DEBUG] Meeting found: {meeting is not None}")
            if not meeting:
                raise HTTPException(
                    status_code=404,
                    detail="Meeting does not exist. Cannot create attendance.",
                )
            obj = MeetingAttendanceModel(
                meeting_id=str(dto.meeting_id),
                user_id=str(user_id),
                status=dto.status,
            )
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return self._to_dto(obj)

    def set_status(self, attendance_id: UUID, status: AttendanceResponse):
        with SessionLocal() as db:
            obj: Optional[MeetingAttendanceModel] = db.query(
                MeetingAttendanceModel
            ).get(str(attendance_id))
            if obj is None:
                return None
            obj.status = status
            db.commit()
            db.refresh(obj)
            return self._to_dto(obj)

    def list_for_meeting(self, meeting_id: UUID):
        with SessionLocal() as db:
            results = (
                db.query(MeetingAttendanceModel, UserModel)
                .join(
                    UserModel,
                    MeetingAttendanceModel.user_id == UserModel.user_id,
                )
                .filter(MeetingAttendanceModel.meeting_id == str(meeting_id))
                .all()
            )
            seen_users = set()
            dtos = []
            for ma, user in results:
                if user.user_id in seen_users:
                    continue
                seen_users.add(user.user_id)
                dtos.append(
                    MeetingAttendanceWithUserDTO(
                        meeting_attendance_id=ma.meeting_attendance_id,
                        meeting_id=ma.meeting_id,
                        user_id=ma.user_id,
                        status=ma.status,
                        responded_at=ma.responded_at,
                        user_name=user.name,
                        user_email=user.email,
                    )
                )
            return dtos

    def get_by_user_and_meeting(self, user_id: UUID, meeting_id: UUID):
        with SessionLocal() as db:
            obj = (
                db.query(MeetingAttendanceModel)
                .filter(
                    MeetingAttendanceModel.user_id == str(user_id),
                    MeetingAttendanceModel.meeting_id == str(meeting_id),
                )
                .one_or_none()
            )
            return self._to_dto(obj) if obj else None
