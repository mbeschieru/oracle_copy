from uuid import UUID

from sqlalchemy.orm import joinedload

from app.domain.repositories.timesheet_repository import (
    TimesheetRepositoryInterface,
)
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.timesheet_models import (
    TimeEntryModel,
    TimesheetModel,
)


class TimesheetRepository(TimesheetRepositoryInterface):

    def get_by_user(self, user_id):
        with SessionLocal() as session:
            return (
                session.query(TimesheetModel)
                .options(joinedload(TimesheetModel.entries))
                .filter(TimesheetModel.user_id == user_id)
                .all()
            )

    def get_by_user_and_week(self, user_id, week_start):
        with SessionLocal() as session:
            return (
                session.query(TimesheetModel)
                .options(joinedload(TimesheetModel.entries))
                .filter(
                    TimesheetModel.user_id == user_id,
                    TimesheetModel.week_start == week_start,
                )
                .first()
            )

    def get_by_id(self, timesheet_id):
        with SessionLocal() as session:
            return (
                session.query(TimesheetModel)
                .options(joinedload(TimesheetModel.entries))
                .filter(TimesheetModel.timesheet_id == timesheet_id)
                .first()
            )

    def save(self, timesheet):
        with SessionLocal() as session:
            existing = (
                session.query(TimesheetModel)
                .filter(
                    TimesheetModel.timesheet_id == str(timesheet.timesheet_id)
                )
                .first()
            )
            if existing:
                # Update fields
                existing.approved = timesheet.approved
                existing.status = timesheet.status
                existing.status_description = timesheet.status_description
                session.commit()
            else:
                orm_timesheet = TimesheetModel(
                    timesheet_id=str(timesheet.timesheet_id),
                    user_id=str(timesheet.user_id),
                    week_start=timesheet.week_start,
                    approved=timesheet.approved,
                    status=timesheet.status,
                    status_description=timesheet.status_description,
                )
                orm_timesheet.entries = [
                    TimeEntryModel(
                        day=entry.day,
                        hours=entry.hours,
                        project_id=str(entry.project_id),
                        description=entry.description,
                    )
                    for entry in timesheet.entries
                ]
                session.add(orm_timesheet)
                session.commit()

    def update(self, timesheet: TimesheetModel):
        with SessionLocal() as session:
            session.merge(timesheet)
            session.commit()

    def approve(self, timesheet_id: UUID) -> None:
        with SessionLocal() as session:
            timesheet = (
                session.query(TimesheetModel)
                .filter(TimesheetModel.timesheet_id == str(timesheet_id))
                .first()
            )
            if not timesheet:
                raise Exception(f"Timesheet {timesheet_id} not found")

            timesheet.approved = True
            session.commit()
