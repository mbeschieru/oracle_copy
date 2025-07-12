import csv
import uuid
from datetime import datetime, timezone
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.user_models import UserModel
from app.infrastructure.db.models.project_models import ProjectModel
from app.infrastructure.config.jwt_config import get_password_hash

CSV_PATH = "Dava.csv"
DEFAULT_ROLE = "employee"
DEFAULT_GRADE = "junior"
DEFAULT_PASSWORD = "Strong123@"

def load_participants(file_path):
    with open(file_path, encoding="ISO-8859-1") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith("Name,First Join,Last Leave"):
            start_idx = i
            break
    else:
        raise ValueError(" Secțiunea '2. Participants' nu a fost găsită.")

    return list(csv.DictReader(lines[start_idx:], skipinitialspace=True))

def get_project(db):
    existing_project = db.query(ProjectModel).first()
    print(f"Using existing project: {existing_project.name} (ID: {existing_project.project_id})")
    return existing_project.project_id

def populate_users():
    db = SessionLocal()
    participants = load_participants(CSV_PATH)
    inserted = 0
    skipped = 0

    try:
        project_id = get_project(db)
        
        for row in participants:
            name = row.get("Name", "").strip()
            email = row.get("Email", "").strip().lower()

            if not name or not email:
                continue

            if db.query(UserModel).filter(UserModel.email == email).first():
                skipped += 1
                continue

            user_project_id = project_id if inserted < 10 else None
            
            user = UserModel(
                user_id=str(uuid.uuid4()),
                name=name,
                email=email,
                password_hash=get_password_hash(DEFAULT_PASSWORD),
                role=DEFAULT_ROLE,
                grade=DEFAULT_GRADE,
                created_at=datetime.now(timezone.utc),
                project_id=user_project_id
            )

            db.add(user)
            db.flush()  
            inserted += 1

        db.commit()

        print(f"{inserted} useri inserați.")
        print(f"{skipped} useri săriți (existenți deja).")

    except Exception as e:
        db.rollback()
        print(" Eroare la inserare:", e)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_users()
