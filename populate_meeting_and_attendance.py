import os
import csv
import uuid
import re
from datetime import datetime
from io import StringIO
from sqlalchemy.orm.exc import NoResultFound

from app.domain.enums.enums import AttendanceResponse
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.meeting_models import MeetingModel
from app.infrastructure.db.models.attendance_models import AttendanceModel
from app.infrastructure.db.models.user_models import UserModel
from app.infrastructure.db.models.meeting_attendance_models import (
    MeetingAttendanceModel,
)

#folder davaX_data
#-ETL24.csv
#-ETL25.csv
#-ETL26.csv

# Use robust path for CSV_FOLDER
def get_davax_folder():
    return os.path.join(os.path.dirname(__file__), "davaX_data")

CSV_FOLDER = get_davax_folder()

def parse_duration_to_minutes(duration_str: str) -> int:
    hours = minutes = seconds = 0
    if match := re.search(r"(\d+)h", duration_str):
        hours = int(match.group(1))
    if match := re.search(r"(\d+)m", duration_str):
        minutes = int(match.group(1))
    if match := re.search(r"(\d+)s", duration_str):
        seconds = int(match.group(1))
    return hours * 60 + minutes + (1 if seconds >= 30 else 0)

def parse_time_string(time_str: str) -> datetime.time:
    return datetime.strptime(time_str.strip(), "%m/%d/%y, %I:%M:%S %p").time()

def parse_day_string(time_str: str) -> datetime.date:
    return datetime.strptime(time_str.strip(), "%m/%d/%y, %I:%M:%S %p").date()

def extract_meeting_metadata(lines: list[str]) -> tuple[str, datetime, int]:
    title = ""
    start_time_str = ""
    duration_str = ""

    for line in lines:
        parsed = next(csv.reader(StringIO(line.strip())))
        if parsed[0].startswith("Meeting title"):
            title = parsed[1].strip()
        elif parsed[0].startswith("Start time"):
            start_time_str = parsed[1].strip()
        elif parsed[0].startswith("Meeting duration"):
            duration_str = parsed[1].strip()

    start_datetime = datetime.strptime(start_time_str, "%m/%d/%y, %I:%M:%S %p")
    duration_minutes = parse_duration_to_minutes(duration_str)

    return title, start_datetime, duration_minutes

def extract_attendance_data(lines: list[str]) -> list[dict]:
    for i, line in enumerate(lines):
        if line.strip().startswith("Name,First Join,Last Leave"):
            start_idx = i
            break
    else:
        raise ValueError("Secțiunea '2. Participants' nu a fost găsită.")

    reader = csv.DictReader(lines[start_idx:], skipinitialspace=True)
    return list(reader)

def populate_meeting_and_attendance():
    db = SessionLocal()
    # Find a manager user
    manager = db.query(UserModel).filter(UserModel.role == "manager").first()
    if not manager:
        print("No manager user found. Cannot create meetings.")
        db.close()
        return
    print(f"Meetings will be created by manager: {manager.email}")
    try:
        for filename in os.listdir(CSV_FOLDER):
            if not filename.endswith(".csv"):
                continue

            file_path = os.path.join(CSV_FOLDER, filename)
            print(f"\n=== Procesare fișier: {filename} ===")

            with open(file_path, encoding="ISO-8859-1") as f:
                lines = f.readlines()

            title, start_datetime, duration_minutes = extract_meeting_metadata(lines)

            existing = db.query(MeetingModel).filter(
                MeetingModel.title == title,
                MeetingModel.datetime == start_datetime
            ).first()

            if existing:
                print(f"Meeting-ul '{title}' din {start_datetime} există deja în DB (ID: {existing.meeting_id}).")
                continue

            meeting_id = str(uuid.uuid4())
            meeting = MeetingModel(
                meeting_id=meeting_id,
                title=title,
                datetime=start_datetime,
                duration_minutes=duration_minutes
            )
            db.add(meeting)
            db.flush()

            print(f"Meeting inserat: {title} la {start_datetime}, {duration_minutes} minute.")

            participants = extract_attendance_data(lines)
            inserted, skipped, duplicates_in_csv = 0, 0, 0
            seen_emails = set()

            for row in participants:
                email = row["Email"].strip().lower()
                if email == "email":
                    continue
                if email in seen_emails:
                    duplicates_in_csv += 1
                    continue
                seen_emails.add(email)

                check_in_str = row["First Join"]
                check_out_str = row["Last Leave"]
                duration_str = row["In-Meeting Duration"]

                try:
                    user = db.query(UserModel).filter(UserModel.email == email).one()
                except NoResultFound:
                    skipped += 1
                    continue

                already_exists = db.query(AttendanceModel).filter_by(
                    meeting_id=meeting_id,
                    user_id=user.user_id
                ).first()

                if already_exists:
                    skipped += 1
                    continue

                attendance = AttendanceModel(
                    attendance_id=str(uuid.uuid4()),
                    meeting_id=meeting_id,
                    user_id=user.user_id,
                    day=parse_day_string(check_in_str),
                    check_in=parse_time_string(check_in_str),
                    check_out=parse_time_string(check_out_str),
                    time_spent=parse_duration_to_minutes(duration_str)
                )
                db.add(attendance)

                """
                attendance = MeetingAttendanceModel(
                    meeting_attendance_id=str(uuid.uuid4()),
                    meeting_id=meeting_id,
                    user_id=user.user_id,
                    status=AttendanceResponse.ACC   # or DECLINED / PENDING
                )
                db.add(attendance)
                """

                inserted += 1

            db.commit()

            print(f"Prezențe adăugate: {inserted}")
            print(f"Participanți săriți (email inexistent sau deja în DB): {skipped}")
            print(f"Participanți ignorați (duplicat în CSV): {duplicates_in_csv}")

    finally:
        db.close()


if __name__ == "__main__":
    populate_meeting_and_attendance()
