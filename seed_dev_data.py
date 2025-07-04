from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.user_models import UserModel
from app.infrastructure.db.models.project_models import ProjectModel
from app.infrastructure.db.models.timesheet_models import TimesheetModel
from datetime import date
import uuid

db = SessionLocal()

# Create manager
manager_id = str(uuid.uuid4())
manager = UserModel(
    user_id=manager_id,
    name="Bob Manager",
    email="bob@endava.com",
    role="manager",
    grade="senior",
    project_id=None  # temporary, will link after project
)

# Create project and link manager
project_id = str(uuid.uuid4())
project = ProjectModel(
    project_id=project_id,
    name="Demo Project",
    description="Project for testing",
    manager_id=manager_id
)
manager.project_id = project_id

# Create employee
employee = UserModel(
    user_id=str(uuid.uuid4()),
    name="Alice Employee",
    email="alice@endava.com",
    role="employee",
    grade="junior",
    project_id=project_id
)

# Create a timesheet (no entries yet)
timesheet = TimesheetModel(
    timesheet_id=str(uuid.uuid4()),
    user_id=employee.user_id,
    week_start=date(2025, 7, 1),
    approved=False
)

db.add_all([manager, project, employee, timesheet])
db.commit()
print("✅ Seed data created.")
