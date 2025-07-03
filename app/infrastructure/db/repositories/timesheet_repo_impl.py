from app.domain.repositories.timesheet_repository import TimesheetRepositoryInterface
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.timesheet_models import TimesheetModel

class TimesheetRepository(TimesheetRepositoryInterface):

    def __init__(self):
        self.db = SessionLocal()

    def get_by_user(self, user_id):
        return self.db.query(TimesheetModel).filter(TimesheetModel.user_id == user_id).all()

    def get_by_user_and_week(self, user_id, week_start):
        return self.db.query(TimesheetModel).filter(
            TimesheetModel.user_id == user_id,
            TimesheetModel.week_start == week_start
        ).first()

    def get_by_id(self, timesheet_id):
        return self.db.query(TimesheetModel).filter(TimesheetModel.timesheet_id == timesheet_id).first()

    def save(self, timesheet: TimesheetModel):
        self.db.add(timesheet)
        self.db.commit()

    def update(self, timesheet: TimesheetModel):
        self.db.merge(timesheet)
        self.db.commit()
