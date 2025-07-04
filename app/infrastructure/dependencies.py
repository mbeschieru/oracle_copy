from app.use_case.services.user_service import UserService
from app.use_case.services.timesheet_service import TimesheetService
from app.infrastructure.db.repositories.user_repo_impl import UserRepository
from app.infrastructure.db.repositories.timesheet_repo_impl import TimesheetRepository

def get_user_service():
    return UserService(UserRepository())

def get_timesheet_service():
    return TimesheetService(timesheet_repo = TimesheetRepository,
                            user_repo = UserRepository)
