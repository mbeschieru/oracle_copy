from uuid import UUID
from datetime import date
from app.domain.exceptions.factory_user import user_not_found
from app.domain.repositories.timesheet_repository import TimesheetRepositoryInterface
from app.domain.repositories.user_repository import UserRepositoryInterface
from app.domain.entities.timesheet import TimeEntry, Timesheet
from app.use_case.validators.role_validator import require_manager
from app.domain.entities.user import User
from app.domain.dto.timesheet_dto import TimesheetCreateDTO, TimesheetReadDTO, TimeEntryDTO
from app.domain.enums.enums import UserRole
from app.use_case.validators.user_identity import assert_user_can_access_user


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
        self.user_repo = user_repo

    def get_timesheet_by_id(self , timesheet_id : UUID):
        timesheet = self.repo.get_by_id(timesheet_id)
        if not timesheet:
            raise timesheet_not_found(str(timesheet_id))
        return timesheet

    def get_timesheets_for_user(self, requester_id: UUID, target_user_id: UUID):
        assert_user_can_access_user(requester_id, target_user_id, self.user_repo)

        timesheets = self.repo.get_by_user(target_user_id)
        if not timesheets:
            raise user_timesheet_not_found(str(target_user_id))

        return [TimesheetReadDTO.from_orm(ts) for ts in timesheets]

        
    def get_timesheet_by_week(self, requester_id: UUID, target_user_id: UUID, week_start: date):
        assert_user_can_access_user(requester_id, target_user_id, self.user_repo)

        ts = self.repo.get_by_user_and_week(target_user_id, str(week_start))
        if not ts:
            raise user_timesheet_not_found(str(target_user_id), str(week_start))

        # Map ORM entries to DTOs
        entries = [
            TimeEntryDTO(
                day=e.day,
                hours=e.hours,
                project_id=e.project_id,
                description=e.description
            ) for e in getattr(ts, 'entries', [])
        ]
        return TimesheetReadDTO(
            timesheet_id=ts.timesheet_id,
            user_id=ts.user_id,
            week_start=ts.week_start,
            approved=ts.approved,
            status=getattr(ts, 'status', 'pending'),
            status_description=getattr(ts, 'status_description', None),
            entries=entries
        )

    
    def submit_timesheet(self, dto: TimesheetCreateDTO, user_id: UUID):
        from fastapi import HTTPException
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise user_not_found(str(user_id))
        if user.role == UserRole.MANAGER:
            raise permission_denied("Managers are not allowed to submit timesheets.")
        # Enforce week_start is Monday
        if dto.week_start.weekday() != 0:
            raise HTTPException(status_code=400, detail="Timesheets can only be created for weeks starting on Monday.")
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
            approved=False,
            status='pending',
            status_description=None
        )

        self.repo.save(ts)
        return {"status": "submitted"}


    def approve_timesheet(self, timesheet_id: UUID , manager: User, description: str = "All ok"):   

        timesheet = self.repo.get_by_id(timesheet_id)

        if not timesheet:
           raise timesheet_not_found(str(timesheet_id))
        
        employee = self.user_repo.get_by_id(timesheet.user_id)
        
        if manager.role != UserRole.MANAGER or manager.project_id != employee.project_id:
            raise permission_denied("You are not authorized to approve this timesheet")
    
        if getattr(timesheet, 'status', 'pending') == 'accepted':
            raise timesheet_already_approved(str(timesheet_id))
        
        timesheet.approved = True
        timesheet.status = 'accepted'
        timesheet.status_description = description
        self.repo.save(timesheet)
        return {"status": "accepted", "description": description}

    def decline_timesheet(self, timesheet_id: UUID, manager: User, reason: str):
        timesheet = self.repo.get_by_id(timesheet_id)
        if not timesheet:
            raise timesheet_not_found(str(timesheet_id))
        employee = self.user_repo.get_by_id(timesheet.user_id)
        if manager.role != UserRole.MANAGER or manager.project_id != employee.project_id:
            raise permission_denied("You are not authorized to decline this timesheet")
        timesheet.approved = False
        timesheet.status = 'declined'
        timesheet.status_description = reason
        self.repo.save(timesheet)
        return {"status": "declined", "description": reason}
