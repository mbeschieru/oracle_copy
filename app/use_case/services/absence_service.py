import uuid
from datetime import date
from uuid import UUID

from fastapi import HTTPException

from app.domain.dto.absence_dto import AbsenceCreateDTO, AbsenceReadDTO
from app.domain.entities.absence import Absence
from app.domain.enums.enums import UserRole
from app.domain.exceptions.factory_timsheet import permission_denied
from app.domain.repositories.absence_repository import (
    AbsenceRepositoryInterface,
)
from app.domain.repositories.user_repository import UserRepositoryInterface


class AbsenceService:
    def __init__(
        self,
        absence_repo: AbsenceRepositoryInterface,
        user_repo: UserRepositoryInterface,
    ):
        self.repo = absence_repo
        self.user_repo = user_repo

    def create_absence(self, dto: AbsenceCreateDTO, user_id: UUID):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.role == UserRole.MANAGER:
            raise permission_denied("Managers cannot create absences.")
        if dto.week_start.weekday() != 0:
            raise HTTPException(
                status_code=400,
                detail="Absences can only be created"
                "for weeks starting on Monday."
            )
        # Check for existing absence for this week
        existing = self.repo.get_by_week(user_id, dto.week_start)
        if existing:
            raise HTTPException(
                status_code=409, detail="Absence already exists for this week."
            )
        absence = Absence(
            absence_id=uuid.uuid4(),
            user_id=user_id,
            week_start=dto.week_start,
            days=dto.days,
            reason=dto.reason,
            status="pending",
            status_description=None,
        )
        self.repo.save(absence)
        return {"status": "submitted"}

    def get_user_absences(self, user_id: UUID):
        absences = self.repo.get_by_user(user_id)
        return [AbsenceReadDTO.model_validate(a) for a in absences]

    def get_absence_by_week(self, user_id: UUID, week_start: date):
        absence = self.repo.get_by_week(user_id, week_start)
        if not absence:
            raise HTTPException(
                status_code=404, detail="Absence not found for this week."
            )
        return AbsenceReadDTO.model_validate(absence)

    def approve_absence(
        self, absence_id: UUID, manager_id: UUID, description: str = "All ok"
    ):
        manager = self.user_repo.get_by_id(manager_id)
        if not manager or manager.role != UserRole.MANAGER:
            raise permission_denied("Only managers can approve absences.")
        absence = self.repo.get_by_id(absence_id)
        if not absence:
            raise HTTPException(status_code=404, detail="Absence not found.")
        # Check manager's project matches user's project
        user = self.user_repo.get_by_id(absence.user_id)
        if manager.project_id != user.project_id:
            raise permission_denied(
                "You are not authorized to approve this absence."
            )
        self.repo.approve(absence_id, manager_id, description)
        return {"status": "accepted", "description": description}

    def decline_absence(self, absence_id: UUID, manager_id: UUID, reason: str):
        manager = self.user_repo.get_by_id(manager_id)
        if not manager or manager.role != UserRole.MANAGER:
            raise permission_denied("Only managers can decline absences.")
        absence = self.repo.get_by_id(absence_id)
        if not absence:
            raise HTTPException(status_code=404, detail="Absence not found.")
        user = self.user_repo.get_by_id(absence.user_id)
        if manager.project_id != user.project_id:
            raise permission_denied(
                "You are not authorized to decline this absence."
            )
        self.repo.decline(absence_id, manager_id, reason)
        return {"status": "declined", "description": reason}

    def get_project_absences_by_week(self, project_id: UUID, week_start: date):
        absences = self.repo.get_by_project_and_week(project_id, week_start)
        return [AbsenceReadDTO.model_validate(a) for a in absences]
