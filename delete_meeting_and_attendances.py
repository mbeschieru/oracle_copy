from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.meeting_models import MeetingModel
from app.infrastructure.db.models.attendance_models import AttendanceModel

MEETING_TITLE = "Dava.X Academy - ETL Theory training sessions"

def delete_meeting_and_attendances():
    db = SessionLocal()
    try:
        meeting = db.query(MeetingModel).filter(MeetingModel.title == MEETING_TITLE).first()

        if not meeting:
            print(f"Meetingul cu titlul '{MEETING_TITLE}' nu a fost găsit.")
            return

        # Șterge prezențele asociate
        deleted_attendances = db.query(AttendanceModel).filter(
            AttendanceModel.meeting_id == meeting.meeting_id
        ).delete(synchronize_session=False)

        # Șterge meetingul
        db.delete(meeting)
        db.commit()

        print(f"Șters: {deleted_attendances} prezențe.")
        print(f"Șters meeting: {MEETING_TITLE} (ID: {meeting.meeting_id})")

    except Exception as e:
        db.rollback()
        print(f"Eroare: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    delete_meeting_and_attendances()
