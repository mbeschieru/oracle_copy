from typing import List, Optional
from uuid import UUID

from app.domain.entities.calendar import Meeting
from app.domain.repositories.meeting_repository import (
    MeetingRepositoryInterface,
)
from app.infrastructure.config.db_config import SessionLocal
from app.infrastructure.db.models.meeting_models import MeetingModel


class MeetingRepository(MeetingRepositoryInterface):

    def __init__(self):
        pass  # Don't create session in constructor

    def _get_session(self):
        """Get a new database session"""
        return SessionLocal()

    def get_all_meetings(self) -> List[Meeting]:
        """Get all meetings"""
        db = self._get_session()
        try:
            meetings = (
                db.query(MeetingModel)
                .order_by(MeetingModel.datetime.desc())
                .all()
            )
            return [
                Meeting(
                    meeting_id=UUID(meeting.meeting_id),
                    title=meeting.title,
                    datetime=meeting.datetime,
                    duration_minutes=meeting.duration_minutes,
                )
                for meeting in meetings
            ]
        finally:
            db.close()

    def get_meeting_by_id(self, meeting_id: UUID) -> Optional[Meeting]:
        """Get meeting by ID"""
        db = self._get_session()
        try:
            meeting = (
                db.query(MeetingModel)
                .filter(MeetingModel.meeting_id == str(meeting_id))
                .first()
            )
            if not meeting:
                return None

            return Meeting(
                meeting_id=UUID(meeting.meeting_id),
                title=meeting.title,
                datetime=meeting.datetime,
                duration_minutes=meeting.duration_minutes,
            )
        finally:
            db.close()

    def get_meetings_for_user(self, user_id: UUID) -> List[Meeting]:
        """Get meetings for a specific user"""
        # This would need to join with attendance table to get user's meetings
        # For now, returning all meetings
        return self.get_all_meetings()

    def create_meeting(self, meeting: Meeting) -> None:
        """Create a new meeting"""
        db = self._get_session()
        try:
            meeting_model = MeetingModel(
                meeting_id=str(meeting.meeting_id),
                title=meeting.title,
                datetime=meeting.datetime,
                duration_minutes=meeting.duration_minutes,
            )
            db.add(meeting_model)
            db.commit()
        finally:
            db.close()
