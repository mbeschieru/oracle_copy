from uuid import UUID
from app.domain.repositories.meeting_repository import MeetingRepositoryInterface
from app.domain.entities.calendar import Meeting
from app.use_case.validators.role_validator import require_manager
from app.domain.entities.user import User

class MeetingService:

    def __init__(self, repo: MeetingRepositoryInterface):
        self.repo = repo

    def get_user_meetings(self, user_id: UUID):
        return self.repo.get_meetings_for_user(user_id)

    def create_meeting(self, meeting: Meeting, created_by: User):
        require_manager(created_by)
        self.repo.create_meeting(meeting)
        return {"status": "created"}
