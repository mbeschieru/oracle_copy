from abc import ABC, abstractmethod
from uuid import UUID
from datetime import datetime
from typing import List
from app.domain.entities.calendar import Meeting

class MeetingRepositoryInterface(ABC):

    @abstractmethod
    def get_meetings_for_user(self, user_id: UUID) -> List[Meeting]:
        """Get meetings the user is scheduled to attend"""
        pass

    @abstractmethod
    def create_meeting(self, meeting: Meeting) -> None:
        """Create a new meeting — restricted to managers in logic layer"""
        pass
