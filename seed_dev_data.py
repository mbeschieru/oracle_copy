from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.user_models import UserModel
from app.infrastructure.db.models.project_models import ProjectModel
from app.infrastructure.db.models.timesheet_models import TimesheetModel
from datetime import date
import uuid

db = SessionLocal()

print("🚀 Starting seed process...")

# Step 1: Create manager (without project_id for now)
manager_id = str(uuid.uuid4())
manager = UserModel(
    user_id=manager_id,
    name="Bob Manager",
    email="bob@endava.com",
    role="manager",
    grade="senior",
    project_id=None
)
db.add(manager)
db.commit()
print("✅ Manager created.")

# Step 2: Create project linked to manager
project_id = str(uuid.uuid4())
project = ProjectModel(
    project_id=project_id,
    name="Demo Project",
    description="Project for testing",
    manager_id=manager_id
)
db.add(project)
db.commit()
print("✅ Project created and linked to manager.")

# Step 3: Update manager to point to the new project
manager.project_id = project_id
db.commit()
print("🔄 Manager updated with project_id.")

# Step 4: Create employee assigned to same project
employee = UserModel(
    user_id=str(uuid.uuid4()),
    name="Alice Employee",
    email="alice@endava.com",
    role="employee",
    grade="junior",
    project_id=project_id
)
db.add(employee)
db.commit()
print("✅ Employee created and linked to project.")

# Step 5: Create a timesheet (no entries yet)
timesheet = TimesheetModel(
    timesheet_id=str(uuid.uuid4()),
    user_id=employee.user_id,
    week_start=date(2025, 7, 1),
    approved=False
)
db.add(timesheet)
db.commit()
print("✅ Timesheet created for employee.")

print("🎉 Seed process complete.")
