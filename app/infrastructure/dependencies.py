from app.use_case.services.user_service import UserService
from app.use_case.services.timesheet_service import TimesheetService
from app.use_case.services.absence_service import AbsenceService
from app.infrastructure.db.repositories.user_repo_impl import UserRepository
from app.infrastructure.db.repositories.timesheet_repo_impl import TimesheetRepository
from app.infrastructure.db.repositories.absence_repo_impl import AbsenceRepository

def get_user_service():
    return UserService(UserRepository())

def get_timesheet_service():
    return TimesheetService(timesheet_repo=TimesheetRepository(),
                            user_repo=UserRepository())

def get_absence_service():
    return AbsenceService(AbsenceRepository(), UserRepository())
