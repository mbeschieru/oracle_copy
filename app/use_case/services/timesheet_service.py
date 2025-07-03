from uuid import UUID
from datetime import date
from app.domain.repositories.timesheet_repository import TimesheetRepositoryInterface
from app.domain.entities.timesheet import Timesheet
from app.domain.exceptions.base import DomainException
from app.use_case.validators.role_validator import require_manager
from app.domain.entities.user import User
from app.domain.dto.timesheet_dto import TimesheetReadDTO

from app.domain.exceptions.factory_timsheet import (
    timesheet_not_found,
    duplicate_timesheet,
    duplicate_time_entry,
    user_timesheet_not_found,
    timesheet_already_approved
)

class TimesheetService:

    def __init__(self, timesheet_repo: TimesheetRepositoryInterface):
        self.repo = timesheet_repo

    def get_timesheets_for_user(self, user_id: UUID):
        timesheets = self.repo.get_by_user(user_id)
        if not timesheets:
           raise user_timesheet_not_found(str(user_id))
        return TimesheetReadDTO.from_orm(timesheets)

    def get_timesheet_by_week(self, user_id: UUID, week_start: date):
        timesheets  = self.repo.get_by_user_and_week(user_id , str(week_start))
        if not timesheets :
             raise user_timesheet_not_found(str(user_id), str(week_start))
        return TimesheetReadDTO.from_orm(timesheets)
    
    def submit_timesheet(self, timesheet: Timesheet):

        existing = self.repo.get_by_user_and_week(timesheet.user_id, str(timesheet.week_start))

        if existing:
           raise duplicate_timesheet(str(timesheet.user_id), str(timesheet.week_start))
        
        seen_days = set()

        for entry in timesheet.entries:
            if entry.day in seen_days:
              raise duplicate_time_entry(str(entry.day))
            seen_days.add(entry.day)
        
        self.repo.save(timesheet)
        return {"status": "submitted"}

    def approve_timesheet(self, timesheet_id: UUID , manager: User):   
        require_manager(manager)

        timesheet = self.repo.get_by_id(timesheet_id)
        if not timesheet:
           raise timesheet_not_found(str(timesheet_id))
        
        if timesheet.approved:
            raise timesheet_already_approved(str(timesheet_id))
        
        timesheet.approved = True
        self.repo.save(timesheet)
        return {"status": "approved"}
