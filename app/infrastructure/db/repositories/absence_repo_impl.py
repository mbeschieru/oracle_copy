from app.domain.repositories.absence_repository import AbsenceRepositoryInterface
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.absence_models import AbsenceModel
from app.domain.entities.absence import Absence
from uuid import UUID
from datetime import date, datetime

class AbsenceRepository(AbsenceRepositoryInterface):
    def _to_entity(self, model: AbsenceModel) -> Absence:
        days = [datetime.strptime(d, "%Y-%m-%d").date() for d in model.days.split(",")] if model.days else []
        return Absence(
            absence_id=model.absence_id,
            user_id=model.user_id,
            week_start=model.week_start,
            days=days,
            reason=model.reason,
            status=model.status,
            status_description=model.status_description
        )

    def get_by_user(self, user_id: UUID):
        with SessionLocal() as session:
            absences = session.query(AbsenceModel).filter(AbsenceModel.user_id == str(user_id)).all()
            return [self._to_entity(a) for a in absences]

    def get_by_id(self, absence_id: UUID):
        with SessionLocal() as session:
            a = session.query(AbsenceModel).filter(AbsenceModel.absence_id == str(absence_id)).first()
            return self._to_entity(a) if a else None

    def get_by_week(self, user_id: UUID, week_start: date):
        with SessionLocal() as session:
            a = session.query(AbsenceModel).filter(
                AbsenceModel.user_id == str(user_id),
                AbsenceModel.week_start == week_start
            ).first()
            return self._to_entity(a) if a else None

    def save(self, absence: Absence):
        with SessionLocal() as session:
            existing = session.query(AbsenceModel).filter(AbsenceModel.absence_id == str(absence.absence_id)).first()
            days_str = ",".join([d.strftime("%Y-%m-%d") for d in absence.days])
            if existing:
                existing.week_start = absence.week_start
                existing.days = days_str
                existing.reason = absence.reason
                existing.status = absence.status
                existing.status_description = absence.status_description
            else:
                model = AbsenceModel(
                    absence_id=str(absence.absence_id),
                    user_id=str(absence.user_id),
                    week_start=absence.week_start,
                    days=days_str,
                    reason=absence.reason,
                    status=absence.status,
                    status_description=absence.status_description
                )
                session.add(model)
            session.commit()

    def approve(self, absence_id: UUID, manager_id: UUID, description: str):
        with SessionLocal() as session:
            model = session.query(AbsenceModel).filter(AbsenceModel.absence_id == str(absence_id)).first()
            if model:
                model.status = "accepted"
                model.status_description = description
                session.commit()

    def decline(self, absence_id: UUID, manager_id: UUID, reason: str):
        with SessionLocal() as session:
            model = session.query(AbsenceModel).filter(AbsenceModel.absence_id == str(absence_id)).first()
            if model:
                model.status = "declined"
                model.status_description = reason
                session.commit()

    def get_by_project_and_week(self, project_id: UUID, week_start: date):
        from app.infrastructure.db.models.user_models import UserModel
        with SessionLocal() as session:
            absences = session.query(AbsenceModel).join(UserModel, AbsenceModel.user_id == UserModel.user_id).filter(
                UserModel.project_id == str(project_id),
                AbsenceModel.week_start == week_start
            ).all()
            return [self._to_entity(a) for a in absences] 