from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.user_models import UserModel
from app.infrastructure.db.models.project_models import ProjectModel
from app.infrastructure.config.jwt_config import get_password_hash
from datetime import datetime, timezone
import uuid

print("🚀 Starting basic seed process...")

DEFAULT_PASSWORD = "Strong123@"

db = SessionLocal()

# Create manager (without project_id for now)
manager_id = str(uuid.uuid4())
manager = UserModel(
    user_id=manager_id,
    name="Bob Manager",
    email="bob@endava.com",
    password_hash=get_password_hash(DEFAULT_PASSWORD),
    role="manager",
    grade="senior",
    project_id=None
)
db.add(manager)
db.commit()
print("✅ Manager created.")

# Create project linked to manager
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

# Update manager to point to the new project
manager.project_id = project_id
db.commit()
print("🔄 Manager updated with project_id.")

# Create employee assigned to same project
employee = UserModel(
    user_id=str(uuid.uuid4()),
    name="Alice Employee",
    email="alice@endava.com",
    password_hash=get_password_hash(DEFAULT_PASSWORD),
    role="employee",
    grade="junior",
    project_id=project_id
)
db.add(employee)
db.commit()
print("✅ Employee created and linked to project.")

db.close()
print("\n🎉 Basic seed process complete!")
