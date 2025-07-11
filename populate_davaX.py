import csv
import uuid
from datetime import datetime
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.user_models import UserModel

CSV_PATH = "Dava.csv"
PROJECT_ID = "fb3e3ef1-14ae-4d2f-9694-28ab9f1f38c1"
DEFAULT_ROLE = "employee"
DEFAULT_GRADE = "junior"

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

def populate_users():
    db = SessionLocal()
    participants = load_participants(CSV_PATH)
    inserted = 0
    skipped = 0

    try:
        for row in participants:
            name = row.get("Name", "").strip()
            email = row.get("Email", "").strip().lower()

            if not name or not email:
                continue

            if db.query(UserModel).filter(UserModel.email == email).first():
                skipped += 1
                continue

            user = UserModel(
                user_id=str(uuid.uuid4()),
                name=name,
                email=email,
                role=DEFAULT_ROLE,
                grade=DEFAULT_GRADE,
                created_at=datetime.utcnow(),
                project_id=PROJECT_ID
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
    finally:
        db.close()

if __name__ == "__main__":
    populate_users()
