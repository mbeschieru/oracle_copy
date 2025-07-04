from uuid import UUID
from datetime import date
import uuid
from app.domain.exceptions.factory_user import user_not_found
from app.domain.repositories.timesheet_repository import TimesheetRepositoryInterface
from app.domain.repositories.user_repository import UserRepositoryInterface
from app.domain.entities.timesheet import TimeEntry, Timesheet
from app.use_case.validators.role_validator import require_manager
from app.domain.entities.user import User
from app.domain.dto.timesheet_dto import TimesheetCreateDTO, TimesheetReadDTO
from app.domain.enums.enums import UserRole

from app.domain.exceptions.factory_timsheet import (
    timesheet_not_found,
    duplicate_timesheet,
    duplicate_time_entry,
    user_timesheet_not_found,
    timesheet_already_approved,
    permission_denied
)

class TimesheetService:

    def __init__(self, timesheet_repo: TimesheetRepositoryInterface , user_repo : UserRepositoryInterface):
        self.repo = timesheet_repo
        self.user_repo = UserRepositoryInterface

    def get_timesheet_by_id(self , timesheet_id : UUID):
        timesheet = self.repo.get_by_id(timesheet_id)
        if not timesheet:
            raise timesheet_not_found(str(timesheet_id))

    def get_timesheets_for_user(self, requester_id : UUID , target_user_id: UUID):
        if requester_id != target_user_id:
           requester = self.user_repo.get_by_id(requester_id)
           target_user= self.user_repo.get_by_id(target_user_id)

           if not requester or not target_user :
                raise user_timesheet_not_found(str(target_user_id))
           
           if requester.role != UserRole.MANAGER or requester.project_id != target_user.project_id:
                raise permission_denied("You may only view your own timesheets or those of employees on your project.")

        timesheets =self.repo.get_by_user(target_user_id)
        if not timesheets:
            raise user_timesheet_not_found(str(target_user_id))
        
        return [TimesheetReadDTO.from_orm(ts) for ts in timesheets]
        


    def get_timesheet_by_week(self, requester_id: UUID, target_user_id: UUID, week_start: date):
        if requester_id != target_user_id:

            requester = self.user_repo.get_by_id(requester_id)
            target_user = self.user_repo.get_by_id(target_user_id)

            if not requester or not target_user:
                raise user_timesheet_not_found(str(target_user_id))

            if requester.role != UserRole.MANAGER or requester.project_id != target_user.project_id:
                raise permission_denied("Unauthorized to view this user's timesheet.")

        ts = self.repo.get_by_user_and_week(target_user_id, str(week_start))
        if not ts:
            raise user_timesheet_not_found(str(target_user_id), str(week_start))

        return TimesheetReadDTO.from_orm(ts)

    
    def submit_timesheet(self, dto: TimesheetCreateDTO, user_id: UUID):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise user_not_found(str(user_id))

        existing = self.repo.get_by_user_and_week(user_id, str(dto.week_start))
        if existing:
            raise duplicate_timesheet(str(user_id), str(dto.week_start))

        seen_days = set()
        for entry in dto.entries:
            if entry.day in seen_days:
                raise duplicate_time_entry(str(entry.day))
            seen_days.add(entry.day)

        ts = Timesheet(
            timesheet_id=uuid.uuid4(),
            user_id=user_id,
            week_start=dto.week_start,
            entries=[TimeEntry(**e.dict()) for e in dto.entries],
            approved=False
        )

        self.repo.save(ts)
        return {"status": "submitted"}


    def approve_timesheet(self, timesheet_id: UUID , manager: User):   

        timesheet = self.repo.get_by_id(timesheet_id)

        if not timesheet:
           raise timesheet_not_found(str(timesheet_id))
        
        employee = self.user_repo.get_by_id(timesheet.user_id)
        
        if manager.role != UserRole.MANAGER or manager.project_id != employee.project_id:
            raise permission_denied("You are not authorized to approve this timesheet")
    
        if timesheet.approved:
            raise timesheet_already_approved(str(timesheet_id))
        
        timesheet.approved = True
        self.repo.save(timesheet)
        return {"status": "approved"}
